from .embedding_service import EmbeddingService
from typing import Dict, Tuple


def detect_intent(query: str) -> str:
    """Detect user intent from query using semantic analysis
    
    Args:
        query: Natural language query
        
    Returns:
        Intent type: revenue_growth, profit_trend, comparison, profitability, growth_analysis, summary, unknown
    """
    q = query.lower()
    
    # Check for profitability first (highest priority for margin/profitability related)
    if "profitability" in q or "profitable" in q or "margin" in q:
        return "profitability"
    
    # Keywords for each intent
    intents = {
        "revenue_growth": ["revenue", "sales", "turnover", "income from sales"],
        "profit_trend": ["profit", "earnings", "net income"],
        "comparison": ["compare", "versus", "vs", "comparison", "difference"],
        "growth_analysis": ["growth", "trend", "increase", "decrease", "change"],
        "summary": ["summary", "overview", "analysis"]
    }
    
    # Score each intent
    scores = {}
    for intent, keywords in intents.items():
        score = sum(1 for keyword in keywords if keyword in q)
        if score > 0:
            scores[intent] = score
    
    # Return highest scoring intent
    if scores:
        return max(scores, key=scores.get)
    
    return "unknown"


def detect_chart_type(intent: str, available_metrics: Dict[str, list]) -> Tuple[str, list]:
    """Determine appropriate chart type based on intent and available data
    
    Args:
        intent: Detected intent type
        available_metrics: Dictionary of available metrics with their data
        
    Returns:
        Tuple of (chart_type, data_to_plot)
    """
    
    if intent == "revenue_growth":
        if available_metrics.get("revenue"):
            return "line", available_metrics["revenue"]
        return "none", []
    
    elif intent == "profit_trend":
        if available_metrics.get("profit"):
            return "line", available_metrics["profit"]
        return "none", []
    
    elif intent == "comparison":
        # Return revenue and profit for comparison
        revenue_data = available_metrics.get("revenue", [])
        profit_data = available_metrics.get("profit", [])
        if revenue_data or profit_data:
            return "comparison", [revenue_data, profit_data]
        return "none", []
    
    elif intent == "profitability":
        # Show profit margins if available
        if available_metrics.get("margins"):
            return "bar", available_metrics["margins"]
        elif available_metrics.get("profit"):
            return "bar", available_metrics["profit"]
        return "none", []
    
    elif intent == "growth_analysis":
        # Show all available metrics for growth analysis
        if available_metrics.get("growth"):
            return "line", available_metrics["growth"]
        elif available_metrics.get("revenue"):
            return "line", available_metrics["revenue"]
        return "none", []
    
    else:
        # Default summary view
        if available_metrics.get("revenue"):
            return "bar", available_metrics["revenue"]
        return "none", []