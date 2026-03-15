def detect_intent(query: str):

    q = query.lower()

    if "revenue" in q and ("growth" in q or "trend" in q):
        return "revenue_growth"

    if "compare" in q:
        return "comparison"

    if "profit" in q:
        return "profit_trend"

    if "summary" in q:
        return "summary"

    return "unknown"