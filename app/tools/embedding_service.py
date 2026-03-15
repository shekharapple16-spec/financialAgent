from openai import OpenAI
import os
import json
from typing import List, Dict, Tuple
import re
import pdfplumber
import io


class EmbeddingService:
    """Service for semantic analysis using NVIDIA embeddings"""
    
    def __init__(self):
        api_key = os.getenv("NVIDIA_API_KEY", "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")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://integrate.api.nvidia.com/v1"
        )
        self.model = "nvidia/nv-embedcode-7b-v1"
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text query
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.client.embeddings.create(
                input=[text],
                model=self.model,
                encoding_format="float",
                extra_body={"input_type": "query", "truncate": "NONE"}
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            return []
    
    def extract_financial_sections(self, pdf_bytes: bytes) -> Dict[str, List[str]]:
        """Extract financial data sections from PDF using semantic understanding
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Dictionary with identified financial sections
        """
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
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    tables = page.extract_tables()
                    
                    if text:
                        # Split into lines for analysis
                        lines = text.split("\n")
                        
                        for line in lines:
                            if not line.strip():
                                continue
                            
                            # Get embedding for this line
                            line_embedding = self.get_embedding(line)
                            
                            if line_embedding:
                                # Categorize based on semantic similarity
                                self._categorize_line(line, line_embedding, sections)
                            else:
                                # Fallback to keyword matching
                                self._categorize_by_keyword(line, sections)
                    
                    # Store tables as raw data
                    if tables:
                        for table in tables:
                            sections["raw_tables"].append({
                                "page": page_num,
                                "data": table
                            })
        
        except Exception as e:
            print(f"Error extracting sections: {str(e)}")
        
        return sections
    
    def _categorize_by_keyword(self, line: str, sections: Dict):
        """Fallback keyword-based categorization"""
        line_lower = line.lower()
        
        if "revenue" in line_lower:
            sections["revenue"].append(line)
        if "profit" in line_lower or "earnings" in line_lower:
            sections["profit"].append(line)
        if "income" in line_lower:
            sections["income"].append(line)
        if "expense" in line_lower or "cost" in line_lower:
            sections["expenses"].append(line)
        if "balance" in line_lower or "assets" in line_lower or "liabilities" in line_lower:
            sections["balance"].append(line)
        if "cash flow" in line_lower:
            sections["cash_flow"].append(line)
        if "margin" in line_lower:
            sections["margins"].append(line)
        if "growth" in line_lower or "increase" in line_lower or "increase" in line_lower:
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
        """Extract numerical values from text lines
        
        Args:
            lines: List of text lines
            
        Returns:
            Tuple of (numbers list, labels list)
        """
        numbers = []
        labels = []
        
        for line in lines:
            # Extract numbers with context
            pattern = r'([A-Za-z\s]+?)[\s:]*(-?\d[\d,]*\.?\d*[KMB]?)'
            matches = re.finditer(pattern, line)
            
            for match in matches:
                label = match.group(1).strip()
                value_str = match.group(2).strip()
                
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
                    numbers.append(value)
                    labels.append(label if label else f"Value {len(numbers)}")
                except:
                    pass
            
            # Fallback: extract all numbers
            if not matches:
                number_pattern = r'-?\d[\d,]*\.?\d*[KMB]?'
                number_matches = re.finditer(number_pattern, line)
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
                        numbers.append(value)
                        labels.append(f"Value {len(numbers)}")
                    except:
                        pass
        
        return numbers, labels
