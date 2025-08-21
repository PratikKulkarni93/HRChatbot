#!/usr/bin/env python3
"""
Test script for HR Resource Query Chatbot
Run this script to verify that all components are working correctly.
"""

import requests
import json
import time
import sys

def test_api_connection():
    """Test if FastAPI backend is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI backend is running")
            return True
        else:
            print(f"❌ FastAPI backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ FastAPI backend is not accessible: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint"""
    try:
        test_query = "Find Python developers with machine learning experience"
        response = requests.post(
            "http://localhost:8000/chat",
            json={"message": test_query},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat endpoint working - found {len(data.get('candidates', []))} candidates")
            return True
        else:
            print(f"❌ Chat endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Chat endpoint error: {e}")
        return False

def test_search_endpoint():
    """Test the employee search endpoint"""
    try:
        response = requests.get(
            "http://localhost:8000/employees/search",
            params={"skills": "Python", "experience_min": 3},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search endpoint working - found {data.get('count', 0)} employees")
            return True
        else:
            print(f"❌ Search endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Search endpoint error: {e}")
        return False

def test_stats_endpoint():
    """Test the stats endpoint"""
    try:
        response = requests.get("http://localhost:8000/stats", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint working - {data.get('total_employees', 0)} total employees")
            return True
        else:
            print(f"❌ Stats endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Stats endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing HR Resource Query Chatbot...")
    print("=" * 50)

    tests = [
        ("API Connection", test_api_connection),
        ("Chat Endpoint", test_chat_endpoint),
        ("Search Endpoint", test_search_endpoint),
        ("Stats Endpoint", test_stats_endpoint),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        time.sleep(1)  # Brief pause between tests

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your HR chatbot is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())