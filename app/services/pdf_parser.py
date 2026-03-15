"""PDF Parser for extracting financial data from PDFs"""

import pdfplumber
import pandas as pd
import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class FinancialPDFParser:
    """Extract financial metrics and tables from PDF files"""
    
    @staticmethod
    def extract_tables(pdf_bytes: bytes) -> List[pd.DataFrame]:
        """Extract all tables from PDF
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            List of DataFrames with extracted tables
        """
        tables = []
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table in page_tables:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            tables.append(df)
                            logger.info(f"Extracted table from page {page_num + 1}: {df.shape}")
        except Exception as e:
            logger.error(f"Error extracting tables: {str(e)}")
        
        return tables
    
    @staticmethod
    def extract_financial_metrics(tables: List[pd.DataFrame]) -> Dict:
        """Extract financial metrics from tables
        
        Args:
            tables: List of DataFrames
            
        Returns:
            Dictionary with organized financial metrics
        """
        metrics = {
            "revenue": [],
            "profit": [],
            "income": [],
            "segments": [],
            "geography": [],
            "growth_rates": []
        }
        
        for table in tables:
            try:
                # Convert all to string for pattern matching
                table_str = table.to_string().lower()
                
                # Extract revenue data
                if 'revenue' in table_str or 'sales' in table_str:
                    metrics["revenue"].extend(
                        FinancialPDFParser._extract_numeric_rows(table, ['revenue', 'sales', 'turnover'])
                    )
                
                # Extract profit data
                if 'profit' in table_str or 'earnings' in table_str:
                    metrics["profit"].extend(
                        FinancialPDFParser._extract_numeric_rows(table, ['profit', 'earnings', 'net income'])
                    )
                
                # Extract segments
                if 'segment' in table_str or 'products' in table_str or 'services' in table_str:
                    metrics["segments"].extend(
                        FinancialPDFParser._extract_numeric_rows(table, ['segment', 'products', 'services'])
                    )
                
                # Extract geography
                if 'geography' in table_str or 'region' in table_str or 'americas' in table_str:
                    metrics["geography"].extend(
                        FinancialPDFParser._extract_numeric_rows(table, ['geography', 'region', 'americas', 'europe', 'india'])
                    )
                
                # Extract growth rates
                if '%' in table_str or 'growth' in table_str or 'yoy' in table_str:
                    metrics["growth_rates"].extend(
                        FinancialPDFParser._extract_percentage_rows(table)
                    )
                
            except Exception as e:
                logger.error(f"Error processing table: {str(e)}")
        
        return metrics
    
    @staticmethod
    def _extract_numeric_rows(df: pd.DataFrame, keywords: List[str]) -> List[Dict]:
        """Extract rows containing keywords with numeric values
        
        Args:
            df: DataFrame to process
            keywords: Keywords to search for
            
        Returns:
            List of dicts with label and values
        """
        results = []
        for idx, row in df.iterrows():
            row_str = ' '.join(str(x).lower() for x in row.values)
            
            # Check if any keyword is in row
            if any(kw in row_str for kw in keywords):
                # Try to extract numeric values
                numeric_values = []
                for val in row.values:
                    try:
                        # Handle currency formats, percentages, etc.
                        val_str = str(val).strip()
                        
                        # Remove currency symbols and commas
                        val_str = re.sub(r'[₹$€£]', '', val_str)
                        val_str = val_str.replace(',', '')
                        
                        # Extract number
                        match = re.search(r'-?\d+\.?\d*', val_str)
                        if match:
                            numeric_values.append(float(match.group()))
                    except:
                        pass
                
                if numeric_values:
                    label = str(row.iloc[0]) if len(row) > 0 else "Metric"
                    results.append({
                        "label": label,
                        "values": numeric_values,
                        "row": row.to_dict()
                    })
        
        return results
    
    @staticmethod
    def _extract_percentage_rows(df: pd.DataFrame) -> List[Dict]:
        """Extract rows with percentage values
        
        Args:
            df: DataFrame to process
            
        Returns:
            List of dicts with percentage data
        """
        results = []
        for idx, row in df.iterrows():
            row_str = ' '.join(str(x) for x in row.values)
            
            if '%' in row_str or 'yoy' in row_str.lower():
                # Extract percentage values
                percentages = re.findall(r'-?\d+\.?\d*%', row_str)
                
                if percentages:
                    label = str(row.iloc[0]) if len(row) > 0 else "Growth Rate"
                    results.append({
                        "label": label,
                        "percentages": percentages,
                        "row": row.to_dict()
                    })
        
        return results
    
    @staticmethod
    def extract_text_sections(pdf_bytes: bytes) -> Dict[str, str]:
        """Extract text sections from PDF
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Dictionary with text sections by page
        """
        sections = {}
        try:
            with pdfplumber.open(pdf_bytes) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        sections[f"page_{page_num + 1}"] = text
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
        
        return sections
