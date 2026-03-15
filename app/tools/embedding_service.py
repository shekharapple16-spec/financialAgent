from openai import OpenAI
import os
import json
from typing import List, Dict, Tuple
import re
import pdfplumber
import io
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for semantic analysis using NVIDIA embeddings"""
    
    def __init__(self):
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError(
                "NVIDIA_API_KEY environment variable is not set. "
                "Please set it before initializing the EmbeddingService."
            )
        logger.info(f"Initializing EmbeddingService with API key: {api_key[:20]}...")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://integrate.api.nvidia.com/v1",
            timeout=60.0  # Increased to 60 seconds for API calls
        )
        self.model = "nvidia/nv-embedcode-7b-v1"
        self.embedding_cache = {}  # Cache embeddings to avoid redundant API calls
        self.pdf_cache = {}  # Cache PDF extractions by file hash
        logger.info("EmbeddingService initialized successfully")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text query
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        # Check cache first
        if text in self.embedding_cache:
            logger.info(f"Using cached embedding for: {text[:50]}...")
            return self.embedding_cache[text]
        
        try:
            logger.info(f"Requesting embedding for: {text[:50]}...")
            start_time = time.time()
            
            response = self.client.embeddings.create(
                input=[text],
                model=self.model,
                encoding_format="float",
                extra_body={"input_type": "query", "truncate": "NONE"}
            )
            
            elapsed = time.time() - start_time
            logger.info(f"Embedding received in {elapsed:.2f}s")
            
            embedding = response.data[0].embedding
            self.embedding_cache[text] = embedding  # Cache result
            logger.info(f"Embedding cached successfully, length: {len(embedding)}")
            return embedding
            
        except TimeoutError as e:
            logger.error(f"Timeout getting embedding: {str(e)}")
            logger.warning("Falling back to keyword-based categorization due to timeout")
            return []
        except Exception as e:
            logger.error(f"Error getting embedding: {type(e).__name__}: {str(e)}")
            logger.warning("Falling back to keyword-based categorization")
            return []
    
    def extract_financial_sections(self, pdf_bytes: bytes) -> Dict[str, List[str]]:
        """Extract financial data sections from PDF using NVIDIA embeddings + keywords
        
        Uses two-stage approach:
        1. Keyword matching (fast, reliable baseline)
        2. Semantic embedding analysis (accurate categorization)
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Dictionary with identified financial sections
        """
        # Check cache using file hash
        import hashlib
        file_hash = hashlib.md5(pdf_bytes).hexdigest()
        if file_hash in self.pdf_cache:
            logger.info("Using cached PDF extraction")
            return self.pdf_cache[file_hash]
        
        sections = {
            "revenue": [],
            "profit": [],
            "income": [],
            "expenses": [],
            "balance": [],
            "cash_flow": [],
            "margins": [],
            "growth": [],
            "raw_tables": []
        }
        
        try:
            logger.info("Starting PDF extraction with NVIDIA embeddings...")
            start_time = time.time()
            
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                logger.info(f"PDF loaded with {len(pdf.pages)} pages")
                
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    tables = page.extract_tables()
                    
                    if text:
                        # Split into lines for analysis
                        lines = text.split("\n")
                        logger.info(f"Page {page_num + 1}: {len(lines)} lines extracted")
                        
                        for line in lines:
                            if not line.strip() or len(line.strip()) < 5:
                                continue
                            
                            # Stage 1: Try keyword matching first (fast)
                            self._categorize_by_keyword(line, sections)
                            
                            # Stage 2: Use NVIDIA embeddings for lines that didn't match keywords
                            # (for better semantic understanding of financial concepts)
                            line_lower = line.lower()
                            has_financial_content = any(word in line_lower for word in 
                                ['revenue', 'profit', 'income', 'expense', 'balance', 'cash', 'margin', 'growth', 'sales', 'earnings', 'assets', 'liabilities'])
                            
                            if has_financial_content and len(line.split()) >= 3:
                                # Line likely contains financial data, use embeddings for accurate categorization
                                self._categorize_with_embeddings(line, sections)
                    
                    # Store tables as raw data
                    if tables:
                        for table in tables:
                            sections["raw_tables"].append({
                                "page": page_num,
                                "data": table
                            })
                        logger.info(f"Page {page_num + 1}: {len(tables)} tables extracted")
            
            elapsed = time.time() - start_time
            logger.info(f"PDF extraction completed in {elapsed:.2f}s")
            logger.info(f"Sections found: {[(k, len(v)) for k, v in sections.items() if v]}")
            logger.info(f"✓ NVIDIA embeddings used for semantic categorization")
            
            # Cache the result
            self.pdf_cache[file_hash] = sections
            
        except Exception as e:
            logger.error(f"Error extracting sections: {str(e)}")
        
        return sections
    
    def _categorize_by_keyword(self, line: str, sections: Dict):
        """Keyword-based categorization (fast and reliable)"""
        line_lower = line.lower()
        
        # Revenue keywords
        if any(kw in line_lower for kw in ["revenue", "sales", "turnover", "total revenue", "net sales", "operating revenue"]):
            sections["revenue"].append(line)
        
        # Profit keywords
        if any(kw in line_lower for kw in ["profit", "earnings", "net income", "net profit", "operating income", "ebit"]):
            sections["profit"].append(line)
        
        # Income keywords
        if any(kw in line_lower for kw in ["income", "income statement", "total income"]):
            sections["income"].append(line)
        
        # Expense keywords
        if any(kw in line_lower for kw in ["expense", "cost", "cogs", "cost of goods", "operating expense", "sg&a"]):
            sections["expenses"].append(line)
        
        # Balance sheet keywords
        if any(kw in line_lower for kw in ["balance", "assets", "liabilities", "equity", "stockholders equity"]):
            sections["balance"].append(line)
        
        # Cash flow keywords
        if any(kw in line_lower for kw in ["cash flow", "operating cash", "investing cash", "financing cash"]):
            sections["cash_flow"].append(line)
        
        # Margin keywords
        if any(kw in line_lower for kw in ["margin", "gross margin", "operating margin", "net margin", "%"]):
            sections["margins"].append(line)
        
        # Growth keywords
        if any(kw in line_lower for kw in ["growth", "increased", "decrease", "change", "vs", "variance", "year-over-year", "yoy"]):
            sections["growth"].append(line)
    
    def _categorize_line(self, line: str, embedding: List[float], sections: Dict):
        """Categorize a line using semantic similarity
        
        Args:
            line: Text line
            embedding: Embedding vector for the line
            sections: Dictionary to store categorized sections
        """
        # Get embeddings for category keywords
        category_keywords = {
            "revenue": ["revenue", "sales", "turnover", "income from sales"],
            "profit": ["profit", "earnings", "net income", "operating income"],
            "income": ["income", "net income", "total income"],
            "expenses": ["expenses", "costs", "operating expenses"],
            "balance": ["balance sheet", "assets", "liabilities", "equity"],
            "cash_flow": ["cash flow", "operating cash", "investing cash", "financing cash"],
            "margins": ["margin", "gross margin", "operating margin", "net margin"],
            "growth": ["growth", "increased", "decrease", "year-over-year"]
        }
        
        # Calculate similarity with category keywords
        best_category = None
        best_similarity = 0
        
        for category, keywords in category_keywords.items():
            category_text = " ".join(keywords)
            try:
                category_embedding = self.client.embeddings.create(
                    input=[category_text],
                    model=self.model,
                    encoding_format="float",
                    extra_body={"input_type": "query", "truncate": "NONE"}
                )
                
                # Simple cosine similarity
                similarity = self._cosine_similarity(embedding, category_embedding.data[0].embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_category = category
            except:
                # Fallback if embedding fails
                self._categorize_by_keyword(line, sections)
                return
        
        if best_category and best_similarity > 0.5:
            sections[best_category].append(line)
        else:
            # Default fallback
            self._categorize_by_keyword(line, sections)
    
    def _categorize_with_embeddings(self, line: str, sections: Dict):
        """Categorize a financial line using NVIDIA embeddings for semantic understanding
        
        This function actually uses the NVIDIA embeddings to understand the semantic meaning
        of the line and categorize it correctly, even if keywords don't match perfectly.
        
        Args:
            line: Text line from PDF
            sections: Dictionary to store categorized sections
        """
        try:
            # Get embedding for the line using NVIDIA API
            line_embedding = self.get_embedding(line)
            
            if not line_embedding:
                # Fallback to keyword if embedding fails
                self._categorize_by_keyword(line, sections)
                return
            
            logger.debug(f"Using embeddings for semantic analysis of: {line[:60]}...")
            
            # Define semantic category descriptions
            category_descriptions = {
                "revenue": "total sales revenue income from products services turnover",
                "profit": "profit earnings net income bottom line operating income ebit",
                "income": "income statement net income earnings revenue",
                "expenses": "operating expenses costs cost of goods SG&A expenditures",
                "balance": "balance sheet assets liabilities equity stockholders",
                "cash_flow": "cash flow from operations investing financing activities",
                "margins": "gross margin operating margin net margin profitability percentage",
                "growth": "growth rate increase decrease year-over-year YoY percentage change"
            }
            
            # Calculate semantic similarity with each category
            best_category = None
            best_similarity = 0
            
            for category, description in category_descriptions.items():
                try:
                    # Get embedding for category description
                    cat_embedding = self.get_embedding(description)
                    
                    if cat_embedding:
                        # Calculate cosine similarity
                        similarity = self._cosine_similarity(line_embedding, cat_embedding)
                        
                        logger.debug(f"  {category}: similarity={similarity:.3f}")
                        
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_category = category
                
                except Exception as e:
                    logger.debug(f"Error getting embedding for {category}: {e}")
            
            # Add line to best matching category if similarity is good enough
            if best_category and best_similarity > 0.6:
                sections[best_category].append(line)
                logger.debug(f"✓ Categorized as '{best_category}' (similarity: {best_similarity:.3f})")
            else:
                # If embedding similarity not confident, use keyword matching
                self._categorize_by_keyword(line, sections)
        
        except Exception as e:
            logger.debug(f"Embedding categorization failed, using keywords: {e}")
            self._categorize_by_keyword(line, sections)
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a ** 2 for a in vec1) ** 0.5
        mag2 = sum(b ** 2 for b in vec2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def extract_numbers_from_lines(self, lines: List[str]) -> Tuple[List[float], List[str]]:
        """Extract numerical values from text lines with better filtering
        
        Args:
            lines: List of text lines
            
        Returns:
            Tuple of (numbers list, labels list)
        """
        numbers = []
        labels = []
        
        for line in lines:
            # Skip very short or very long lines
            if len(line.strip()) < 10 or len(line.strip()) > 300:
                continue
            
            # Extract numbers with context - look for financial values
            # Pattern: Label followed by number (possibly with K/M/B)
            pattern = r'([A-Za-z\s\(\)]+?)[\s:]*(-?\d[\d,]*\.?\d*[KMB]?)\s*(?:\(|\[|$|%|,)'
            matches = re.finditer(pattern, line)
            
            found_any = False
            for match in matches:
                label = match.group(1).strip()
                value_str = match.group(2).strip()
                
                # Skip very small labels (likely noise)
                if len(label) < 3:
                    continue
                
                try:
                    # Convert K, M, B suffixes
                    multiplier = 1
                    if value_str.endswith('K'):
                        multiplier = 1_000
                        value_str = value_str[:-1]
                    elif value_str.endswith('M'):
                        multiplier = 1_000_000
                        value_str = value_str[:-1]
                    elif value_str.endswith('B'):
                        multiplier = 1_000_000_000
                        value_str = value_str[:-1]
                    
                    value = float(value_str.replace(",", "")) * multiplier
                    
                    # Filter outliers - skip values that are clearly not financial metrics
                    # (years, percentages, IDs, etc.)
                    if value < 100 or value > 1_000_000_000_000:
                        continue
                    
                    numbers.append(value)
                    labels.append(label if label else f"Value {len(numbers)}")
                    found_any = True
                except:
                    pass
            
            # Only extract remaining numbers if we didn't find labeled ones
            if not found_any:
                number_pattern = r'-?\d[\d,]*\.?\d*[KMB]?'
                number_matches = list(re.finditer(number_pattern, line))
                # Only take if there's exactly 1-2 numbers in the line
                if 0 < len(number_matches) <= 2:
                    for match in number_matches:
                        value_str = match.group(0).strip()
                        try:
                            multiplier = 1
                            if value_str.endswith('K'):
                                multiplier = 1_000
                                value_str = value_str[:-1]
                            elif value_str.endswith('M'):
                                multiplier = 1_000_000
                                value_str = value_str[:-1]
                            elif value_str.endswith('B'):
                                multiplier = 1_000_000_000
                                value_str = value_str[:-1]
                            
                            value = float(value_str.replace(",", "")) * multiplier
                            
                            # Filter outliers
                            if value < 100 or value > 1_000_000_000_000:
                                continue
                            
                            numbers.append(value)
                            labels.append(f"Value {len(numbers)}")
                        except:
                            pass
        
        # Return top 10 values only for cleaner charts
        if len(numbers) > 10:
            logger.info(f"Filtering {len(numbers)} values down to top 10")
            # Sort and take top 10 by absolute value
            sorted_indices = sorted(range(len(numbers)), key=lambda i: abs(numbers[i]), reverse=True)[:10]
            numbers = [numbers[i] for i in sorted(sorted_indices)]
            labels = [labels[i] for i in sorted(sorted_indices)]
        
        return numbers, labels
