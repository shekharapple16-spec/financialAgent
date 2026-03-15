import pdfplumber
import re


def extract_revenue_from_pdf(file_path: str):

    revenue_values = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:

            text = page.extract_text()

            if not text:
                continue

            # simple revenue detection
            lines = text.split("\n")

            for line in lines:
                if "revenue" in line.lower():

                    numbers = re.findall(r"\d[\d,]*\.?\d*", line)

                    if numbers:
                        revenue_values.append(numbers)

    return {
    "revenues": [n.replace(",", "") for sub in revenue_values for n in sub]
}