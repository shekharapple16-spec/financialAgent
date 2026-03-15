#!/usr/bin/env python
"""Quick debug script to test PDF analysis"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from tools.financial_analyzer import analyze_financial_pdf
import json
import time

# Load the uploaded PDF
pdf_path = "uploads/sa-fy14-q4-year-finstatement.pdf"

print(f"Testing PDF: {pdf_path}")
print(f"File size: {os.path.getsize(pdf_path)} bytes")
print("-" * 60)

# Test query
query = "Show profitability chart"
print(f"\nQuery: {query}")
print("Processing...")

try:
    start = time.time()
    
    # Read PDF
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    print(f"PDF loaded: {len(pdf_bytes)} bytes")
    
    # Analyze
    result = analyze_financial_pdf(query, pdf_bytes)
    
    elapsed = time.time() - start
    
    print(f"\nAnalysis completed in {elapsed:.2f} seconds")
    print("-" * 60)
    print(f"Intent: {result.get('intent')}")
    print(f"Chart Type: {result.get('chart_type')}")
    print(f"Metrics Found: {result.get('metrics_found')}")
    print(f"Message: {result.get('message', 'SUCCESS')}")
    
    # Check if chart was generated
    if result.get('chart'):
        chart_size = len(result['chart'])
        print(f"Chart Generated: Yes ({chart_size} bytes base64)")
    else:
        print("Chart Generated: NO")
    
    # Show metrics
    if 'profit_margins' in result:
        print(f"Profit Margins: {result['profit_margins']}")
    if 'profit_values' in result:
        print(f"Profit Values: {result['profit_values']}")
    
    print("\nFull Response Keys:", list(result.keys()))
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
