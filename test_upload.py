#!/usr/bin/env python3
"""Test script to verify the upload endpoint works correctly"""

import requests
import time
from pathlib import Path

# Wait for server to start
time.sleep(2)

BASE_URL = "http://localhost:8000"

# Create a test PDF if it doesn't exist
test_pdf_path = Path("d:\\financial-chart-agent\\test_sample.pdf")
if not test_pdf_path.exists():
    # Create a minimal PDF for testing
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    c = canvas.Canvas(str(test_pdf_path), pagesize=letter)
    c.drawString(100, 750, "Test PDF")
    c.save()
    print(f"Created test PDF at {test_pdf_path}")

# Test upload
print("\n=== Testing Upload Endpoint ===")
with open(test_pdf_path, 'rb') as f:
    files = {'file': (test_pdf_path.name, f, 'application/pdf')}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

# Test list PDFs
print("\n=== Testing List PDFs Endpoint ===")
response = requests.get(f"{BASE_URL}/pdfs")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

# Test health
print("\n=== Testing Health Endpoint ===")
response = requests.get(f"{BASE_URL}/health")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
