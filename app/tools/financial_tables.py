import camelot
import pandas as pd


def extract_financial_metrics(file_path: str):

    tables = camelot.read_pdf(file_path, pages="all")

    metrics = {
        "revenue": [],
        "net_income": [],
        "operating_income": [],
        "eps": []
    }

    for table in tables:

        df = table.df

        for row in df.values:

            row_text = " ".join(row).lower()

            if "revenue" in row_text:
                metrics["revenue"].append(row)

            if "net income" in row_text:
                metrics["net_income"].append(row)

            if "operating income" in row_text:
                metrics["operating_income"].append(row)

            if "eps" in row_text or "earnings per share" in row_text:
                metrics["eps"].append(row)

    return metrics