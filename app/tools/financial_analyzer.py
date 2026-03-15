from .query_router import detect_intent
from .chart_generator import generate_chart

import pdfplumber
import io
import re


def analyze_financial_pdf(query, pdf_bytes):
    """Analyze financial PDF and extract metrics based on query intent
    
    Args:
        query: Natural language query about financial metrics
        pdf_bytes: PDF file content as bytes
    
    Returns:
        Dictionary with analysis results including charts and metrics
    """
    intent = detect_intent(query)

    revenues = []
    profits = []

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                if not text:
                    continue

                for line in text.split("\n"):
                    # Extract revenue data
                    if "revenue" in line.lower():
                        numbers = re.findall(r"\d[\d,]*\.?\d*", line)
                        revenues.extend(numbers)

                    # Extract profit data
                    if "profit" in line.lower():
                        numbers = re.findall(r"\d[\d,]*\.?\d*", line)
                        profits.extend(numbers)
    except Exception as e:
        return {
            "error": f"Error processing PDF: {str(e)}",
            "intent": intent
        }

    # Convert extracted strings to floats for charting
    try:
        revenues = [float(r.replace(",", "")) for r in revenues]
        profits = [float(p.replace(",", "")) for p in profits]
    except ValueError:
        pass

    if intent == "revenue_growth":
        if not revenues:
            return {
                "message": "No revenue data found in PDF",
                "intent": intent
            }
        chart = generate_chart(revenues, "line")
        return {
            "chart": chart,
            "metric": "revenue",
            "data_points": len(revenues),
            "intent": intent
        }

    if intent == "comparison":
        if not revenues or not profits:
            return {
                "message": "Insufficient data for comparison",
                "intent": intent
            }
        chart = generate_chart([revenues, profits], "comparison")
        return {
            "chart": chart,
            "metrics": ["revenue", "profit"],
            "intent": intent
        }

    if intent == "profit_trend":
        if not profits:
            return {
                "message": "No profit data found in PDF",
                "intent": intent
            }
        chart = generate_chart(profits, "line")
        return {
            "chart": chart,
            "metric": "profit",
            "data_points": len(profits),
            "intent": intent
        }

    return {
        "message": "Analysis complete",
        "revenue_data_points": len(revenues),
        "profit_data_points": len(profits),
        "intent": intent
    }