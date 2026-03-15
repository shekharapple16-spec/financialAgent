from .query_router import detect_intent, detect_chart_type
from .chart_generator import generate_chart
from .embedding_service import EmbeddingService

import pdfplumber
import io
import re
import logging
import time
from io import BytesIO

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

embedding_service = EmbeddingService()


def _extract_numbers_from_tables(tables: list) -> dict:
    """Extract financial numbers from PDF tables
    
    Args:
        tables: List of tables from PDF
        
    Returns:
        Dictionary with extracted metrics
    """
    metrics = {
        "revenue": [],
        "profit": [],
        "income": [],
        "expenses": [],
        "margins": [],
        "growth": []
    }
    
    for table in tables:
        if not table or len(table) < 2:
            continue
        
        try:
            # Convert table to text for pattern matching
            table_str = ' '.join(' '.join(str(cell) for cell in row) for row in table).lower()
            
            # Extract rows with numbers
            for row in table[1:]:  # Skip header
                row_str = ' '.join(str(cell) for cell in row)
                
                # Look for revenue indicators
                if any(kw in row_str.lower() for kw in ['revenue', 'sales', 'turnover', 'income from']):
                    nums = _extract_numbers_from_row(row)
                    if nums:
                        metrics["revenue"].extend(nums)
                
                # Look for profit indicators
                if any(kw in row_str.lower() for kw in ['profit', 'earnings', 'net income', 'net profit']):
                    nums = _extract_numbers_from_row(row)
                    if nums:
                        metrics["profit"].extend(nums)
                
                # Look for margin indicators
                if '%' in row_str and any(kw in row_str.lower() for kw in ['margin', 'growth', 'yoy']):
                    nums = _extract_numbers_from_row(row)
                    if nums:
                        metrics["margins"].extend(nums[:3])  # Limit to 3 values per row
        
        except Exception as e:
            logger.warning(f"Error processing table: {str(e)}")
    
    return metrics


def _extract_numbers_from_row(row: list) -> list:
    """Extract numeric values from a table row
    
    Args:
        row: List of cell values
        
    Returns:
        List of numeric values
    """
    numbers = []
    for cell in row:
        if cell is None:
            continue
        
        cell_str = str(cell).strip()
        
        # Skip if too short or non-numeric
        if len(cell_str) < 2 or not any(c.isdigit() for c in cell_str):
            continue
        
        try:
            # Remove currency symbols and commas
            cell_str = re.sub(r'[₹$€£,\s]', '', cell_str)
            
            # Handle K, M, B suffixes
            multiplier = 1
            if cell_str.endswith('K'):
                multiplier = 1_000
                cell_str = cell_str[:-1]
            elif cell_str.endswith('M'):
                multiplier = 1_000_000
                cell_str = cell_str[:-1]
            elif cell_str.endswith('B'):
                multiplier = 1_000_000_000
                cell_str = cell_str[:-1]
            
            # Extract number
            match = re.search(r'-?\d+\.?\d*', cell_str)
            if match:
                value = float(match.group()) * multiplier
                
                # Filter reasonable financial values (between 0.01 and 1 trillion)
                if 0.01 <= value <= 1_000_000_000_000:
                    numbers.append(value)
        
        except Exception:
            pass
    
    return numbers


def analyze_financial_pdf(query, pdf_bytes):
    """Analyze financial PDF and extract metrics based on query intent
    
    Args:
        query: Natural language query about financial metrics
        pdf_bytes: PDF file content as bytes
    
    Returns:
        Dictionary with analysis results including charts and metrics
    """
    logger.info(f"Starting analysis for query: {query}")
    logger.info(f"PDF bytes received: {len(pdf_bytes)} bytes")
    start_time = time.time()
    
    try:
        intent = detect_intent(query)
        logger.info(f"Detected intent: {intent}")
        
        # First try to extract tables from PDF (more reliable than text)
        logger.info("Extracting tables from PDF...")
        tables = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                if page_tables:
                    for table in page_tables:
                        tables.append(table)
                        logger.info(f"Found table on page {page_num + 1}: {len(table)} rows")
        
        # Extract financial sections using semantic analysis
        sections = embedding_service.extract_financial_sections(pdf_bytes)
        logger.info(f"Sections extracted: {list(sections.keys())}")
        
        # Extract numbers from tables first (most reliable)
        table_numbers = _extract_numbers_from_tables(tables)
        logger.info(f"Numbers extracted from tables: revenue={len(table_numbers.get('revenue', []))}, "
                   f"profit={len(table_numbers.get('profit', []))}")
        
        # Extract numbers from each section
        metrics = {}
        
        # Merge table numbers with section numbers (table data takes priority)
        # Process revenue section
        revenue_from_text = []
        if sections.get("revenue"):
            numbers, labels = embedding_service.extract_numbers_from_lines(sections["revenue"])
            revenue_from_text = numbers
        
        metrics["revenue"] = table_numbers.get("revenue", []) or revenue_from_text
        if metrics["revenue"]:
            metrics["revenue_labels"] = [f"Revenue {i+1}" for i in range(len(metrics["revenue"]))]
        
        # Process profit section
        profit_from_text = []
        if sections.get("profit"):
            numbers, labels = embedding_service.extract_numbers_from_lines(sections["profit"])
            profit_from_text = numbers
        
        metrics["profit"] = table_numbers.get("profit", []) or profit_from_text
        if metrics["profit"]:
            metrics["profit_labels"] = [f"Profit {i+1}" for i in range(len(metrics["profit"]))]
        
        # Process income section
        if sections.get("income"):
            numbers, labels = embedding_service.extract_numbers_from_lines(sections["income"])
            if numbers:
                metrics["income"] = numbers
                metrics["income_labels"] = labels
        
        # Process expenses section
        if sections.get("expenses"):
            numbers, labels = embedding_service.extract_numbers_from_lines(sections["expenses"])
            if numbers:
                metrics["expenses"] = numbers
                metrics["expenses_labels"] = labels
        
        # Process margins section
        if sections.get("margins"):
            numbers, labels = embedding_service.extract_numbers_from_lines(sections["margins"])
            if numbers:
                metrics["margins"] = numbers
                metrics["margins_labels"] = labels
        
        # Process growth section
        if sections.get("growth"):
            numbers, labels = embedding_service.extract_numbers_from_lines(sections["growth"])
            if numbers:
                metrics["growth"] = numbers
                metrics["growth_labels"] = labels
        
        # Determine chart type based on intent and available metrics
        chart_type, data_to_plot = detect_chart_type(intent, metrics)
        logger.info(f"Selected chart type: {chart_type}")
        
        # Prepare metrics summary - this will be displayed as cards in UI
        metrics_summary = {}
        if metrics.get("revenue") and len(metrics["revenue"]) > 0:
            # Get top revenue values
            revenue_vals = sorted(metrics.get("revenue", []), reverse=True)[:3]
            metrics_summary["total_revenue"] = revenue_vals[0] if revenue_vals else 0
            metrics_summary["revenue_label"] = metrics.get("revenue_labels", ["Revenue"])[0] if metrics.get("revenue_labels") else "Total Revenue"
            metrics_summary["revenue_formatted"] = f"₹{metrics_summary['total_revenue']:,.0f} Cr" if metrics_summary['total_revenue'] > 0 else "N/A"
        
        if metrics.get("profit") and len(metrics["profit"]) > 0:
            profit_vals = sorted(metrics.get("profit", []), reverse=True)[:3]
            metrics_summary["net_profit"] = profit_vals[0] if profit_vals else 0
            metrics_summary["profit_formatted"] = f"₹{metrics_summary['net_profit']:,.0f} Cr" if metrics_summary['net_profit'] > 0 else "N/A"
        
        if chart_type == "none":
            logger.warning("No relevant data found for query")
            elapsed = time.time() - start_time
            return {
                "message": "No relevant data found for your query",
                "intent": intent,
                "available_sections": list(sections.keys()),
                "extracted_metrics": list(metrics.keys()),
                "processing_time_seconds": elapsed
            }
        
        # Generate appropriate chart
        logger.info("Generating chart...")
        chart = generate_chart(data_to_plot, chart_type, title=f"{intent.replace('_', ' ').title()} Analysis")
        
        result = {
            "chart": chart,
            "intent": intent,
            "chart_type": chart_type,
            "metrics_found": list(metrics.keys()),
            "sections_analyzed": list(sections.keys()),
            "metrics_summary": metrics_summary
        }
        
        # Add specific metric information based on intent
        if intent == "revenue_growth":
            result["metric"] = "revenue"
            if "revenue" in metrics:
                result["data_points"] = len(metrics["revenue"])
                result["values"] = metrics["revenue"]
        
        elif intent == "profit_trend":
            result["metric"] = "profit"
            if "profit" in metrics:
                result["data_points"] = len(metrics["profit"])
                result["values"] = metrics["profit"]
        
        elif intent == "comparison":
            result["metrics"] = ["revenue", "profit"]
            if "revenue" in metrics:
                result["revenue_data"] = metrics["revenue"]
            if "profit" in metrics:
                result["profit_data"] = metrics["profit"]
        
        elif intent == "profitability":
            result["metric"] = "profitability"
            if "margins" in metrics:
                result["profit_margins"] = metrics["margins"]
            if "profit" in metrics:
                result["profit_values"] = metrics["profit"]
        
        elif intent == "growth_analysis":
            result["metric"] = "growth"
            if "growth" in metrics:
                result["growth_data"] = metrics["growth"]
        
        elapsed = time.time() - start_time
        result["processing_time_seconds"] = elapsed
        logger.info(f"Analysis completed in {elapsed:.2f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {type(e).__name__}: {str(e)}", exc_info=True)
        elapsed = time.time() - start_time
        return {
            "error": f"Analysis failed: {str(e)}",
            "processing_time_seconds": elapsed
        }