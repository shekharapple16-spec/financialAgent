from .query_router import detect_intent
from .chart_generator import generate_chart

import pdfplumber
import io
import re


def analyze_financial_pdf(query, pdf_bytes):

    intent = detect_intent(query)

    revenues = []
    profits = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if not text:
                continue

            for line in text.split("\n"):

                if "revenue" in line.lower():
                    numbers = re.findall(r"\d[\d,]*\.?\d*", line)
                    revenues.extend(numbers)

                if "profit" in line.lower():
                    numbers = re.findall(r"\d[\d,]*\.?\d*", line)
                    profits.extend(numbers)

    if intent == "revenue_growth":

        chart = generate_chart(revenues, "line")

        return {
            "chart": chart,
            "metric": "revenue"
        }

    if intent == "comparison":

        chart = generate_chart([revenues, profits], "comparison")

        return {
            "chart": chart,
            "metrics": ["revenue", "profit"]
        }

    if intent == "profit_trend":

        chart = generate_chart(profits, "line")

        return {
            "chart": chart,
            "metric": "profit"
        }

    return {
        "message": "analysis complete"
    }