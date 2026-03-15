from .query_router import detect_intent, detect_chart_type
from .chart_generator import generate_chart
from .embedding_service import EmbeddingService

import pdfplumber
import io
import re
import logging
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

embedding_service = EmbeddingService()


def analyze_financial_pdf(query, pdf_bytes):
    """Analyze financial PDF and extract metrics based on query intent
    
    Args:
        query: Natural language query about financial metrics
        pdf_bytes: PDF file content as bytes
    
    Returns:
        Dictionary with analysis results including charts and metrics
    """
    logger.info(f"Starting analysis for query: {query}")
    start_time = time.time()
    
    intent = detect_intent(query)
    logger.info(f"Detected intent: {intent}")
    
    # Extract financial sections using semantic analysis
    sections = embedding_service.extract_financial_sections(pdf_bytes)
    logger.info(f"Sections extracted: {list(sections.keys())}")
    
    # Extract numbers from each section
    metrics = {}
    
    # Process revenue section
    if sections.get("revenue"):
        numbers, labels = embedding_service.extract_numbers_from_lines(sections["revenue"])
        if numbers:
            metrics["revenue"] = numbers
            metrics["revenue_labels"] = labels
    
    # Process profit section
    if sections.get("profit"):
        numbers, labels = embedding_service.extract_numbers_from_lines(sections["profit"])
        if numbers:
            metrics["profit"] = numbers
            metrics["profit_labels"] = labels
    
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
    
    if chart_type == "none":
        logger.warning("No relevant data found for query")
        return {
            "message": "No relevant data found for your query",
            "intent": intent,
            "available_sections": list(sections.keys()),
            "extracted_metrics": list(metrics.keys())
        }
    
    # Generate appropriate chart
    logger.info("Generating chart...")
    chart = generate_chart(data_to_plot, chart_type)
    
    result = {
        "chart": chart,
        "intent": intent,
        "chart_type": chart_type,
        "metrics_found": list(metrics.keys()),
        "sections_analyzed": list(sections.keys())
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