#!/usr/bin/env python
"""
Test script to verify embedding-based financial analysis
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from tools.embedding_service import EmbeddingService
from tools.query_router import detect_intent, detect_chart_type
from tools.financial_analyzer import analyze_financial_pdf
import json


def test_embedding_service():
    """Test the embedding service"""
    print("\n" + "="*60)
    print("Testing Embedding Service")
    print("="*60)
    
    service = EmbeddingService()
    
    # Test embedding generation
    test_text = "Apple Inc reported revenue of $394.3 billion and net income of $93.7 billion"
    print(f"\nGenerating embedding for: '{test_text}'")
    embedding = service.get_embedding(test_text)
    
    if embedding:
        print(f"[PASS] Embedding generated successfully (dimensions: {len(embedding)})")
    else:
        print("[FAIL] Failed to generate embedding")
        return False
    
    return True


def test_intent_detection():
    """Test intent detection"""
    print("\n" + "="*60)
    print("Testing Intent Detection")
    print("="*60)
    
    test_queries = [
        ("Show revenue growth", "revenue_growth"),
        ("Compare revenue vs profit", "comparison"),
        ("Show profitability chart", "profitability"),
        ("What's the profit trend?", "profit_trend"),
        ("Analyze growth metrics", "growth_analysis"),
    ]
    
    all_passed = True
    for query, expected_intent in test_queries:
        detected_intent = detect_intent(query)
        status = "PASS" if detected_intent == expected_intent else "FAIL"
        print(f"[{status}] Query: '{query}'")
        print(f"   Expected: {expected_intent}, Got: {detected_intent}")
        if detected_intent != expected_intent:
            all_passed = False
    
    return all_passed


def test_chart_type_detection():
    """Test chart type detection"""
    print("\n" + "="*60)
    print("Testing Chart Type Detection")
    print("="*60)
    
    metrics = {
        "revenue": [100, 110, 120, 130],
        "profit": [20, 24, 28, 32],
        "margins": [20, 21.8, 23.3, 24.6]
    }
    
    test_cases = [
        ("revenue_growth", "line"),
        ("profit_trend", "line"),
        ("comparison", "comparison"),
        ("profitability", "bar"),
    ]
    
    all_passed = True
    for intent, expected_chart_type in test_cases:
        chart_type, data = detect_chart_type(intent, metrics)
        status = "PASS" if chart_type == expected_chart_type else "FAIL"
        print(f"[{status}] Intent: {intent}")
        print(f"   Expected chart: {expected_chart_type}, Got: {chart_type}")
        if chart_type != expected_chart_type:
            all_passed = False
    
    return all_passed


def test_number_extraction():
    """Test number extraction from text"""
    print("\n" + "="*60)
    print("Testing Number Extraction")
    print("="*60)
    
    service = EmbeddingService()
    
    test_lines = [
        "Revenue: $394.3B",
        "Net Income: $93.7 Million",
        "Gross Profit: 567,890.50",
        "Operating Margin: 25.4%",
        "Total Assets: 352K"
    ]
    
    numbers, labels = service.extract_numbers_from_lines(test_lines)
    
    print(f"[PASS] Extracted {len(numbers)} numbers from {len(test_lines)} lines")
    for i, (num, label) in enumerate(zip(numbers, labels)):
        print(f"   {i+1}. {label}: {num:,.2f}")
    
    return len(numbers) > 0


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("EMBEDDING-BASED FINANCIAL ANALYSIS - TEST SUITE")
    print("="*80)
    
    tests = [
        ("Embedding Service", test_embedding_service),
        ("Intent Detection", test_intent_detection),
        ("Chart Type Detection", test_chart_type_detection),
        ("Number Extraction", test_number_extraction),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "PASSED" if result else "FAILED"
        except Exception as e:
            results[test_name] = f"ERROR: {str(e)}"
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, result in results.items():
        status_symbol = "PASS" if result == "PASSED" else "FAIL"
        print(f"[{status_symbol}] {test_name}: {result}")
    
    passed_count = sum(1 for r in results.values() if r == "PASSED")
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print("="*80 + "\n")
    
    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
