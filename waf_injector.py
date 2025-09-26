#!/usr/bin/env python3
"""
Interactive WAF Testing CLI
Allows manual injection of malicious payloads and monitors WAF responses
"""

import requests
import json
import time
from datetime import datetime

# WAF API endpoints
WAF_DETECT_URL = "http://localhost:5000/detect"
WAF_ANALYZE_URL = "http://localhost:8000/analyze"

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🚀 WAF PAYLOAD INJECTOR                    ║
║              Interactive Malicious Request Testing            ║
╚══════════════════════════════════════════════════════════════╝
""")

def get_user_input():
    """Get HTTP request details from user"""
    print("\n📝 Enter HTTP Request Details:")
    print("-" * 40)

    method = input("HTTP Method (GET/POST/PUT/DELETE) [GET]: ").strip().upper()
    if not method:
        method = "GET"

    path = input("Request Path [/]: ").strip()
    if not path:
        path = "/"

    # Add query parameters if it's a GET request
    query_params = {}
    if method == "GET":
        query = input("Query Parameters (key=value,key2=value2) [empty]: ").strip()
        if query:
            for pair in query.split(','):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    query_params[key.strip()] = value.strip()

    headers_input = input("Headers (key=value,key2=value2) [empty]: ").strip()
    headers = {}
    if headers_input:
        for pair in headers_input.split(','):
            if '=' in pair:
                key, value = pair.split('=', 1)
                headers[key.strip()] = value.strip()

    body = ""
    if method in ["POST", "PUT", "PATCH"]:
        body = input("Request Body [empty]: ").strip()

    return {
        "method": method,
        "path": path,
        "headers": headers,
        "body": body,
        "query_params": query_params
    }

def send_to_waf(request_data):
    """Send request to WAF for analysis"""
    try:
        print(f"\n🔍 Analyzing request: {request_data['method']} {request_data['path']}")

        # Send to backend API (which will show in dashboard if malicious)
        response = requests.post(WAF_DETECT_URL, json=request_data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"❌ API Error: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return None

def display_result(result, request_data):
    """Display analysis result"""
    if not result:
        return

    print("\n" + "="*60)
    print("🎯 WAF ANALYSIS RESULT")
    print("="*60)

    # Request details
    request_sig = result.get('request_signature', f"{request_data['method']} {request_data['path']}")
    print(f"📨 Request: {request_sig}")
    print(f"⏱️  Processing Time: {result.get('processing_time_ms', 0):.1f}ms")

    is_malicious = result.get('is_malicious', False)
    threat_type = result.get('threat_type', 'none')
    confidence = result.get('confidence', 0)

    if is_malicious:
        print("🚨 THREAT DETECTED!")
        print(f"   Type: {threat_type}")
        print(f"   Confidence: {confidence:.2f}")
        print("📊 This malicious request has been logged in your dashboard!")
    else:
        print("✅ REQUEST ALLOWED")
        print("   No threats detected")
        print("💡 This request passed through safely")
    print("="*60)

def main():
    print_banner()

    print("🔗 Connecting to WAF services...")
    print(f"   Backend API: {WAF_DETECT_URL}")
    print(f"   ML Service: {WAF_ANALYZE_URL}")

    # Test connection
    try:
        response = requests.get("http://localhost:5000/detections", timeout=5)
        if response.status_code == 200:
            print("✅ WAF services are running!")
        else:
            print("⚠️  Backend service may not be responding correctly")
    except:
        print("❌ Cannot connect to WAF services. Please ensure they are running:")
        print("   1. ML Service: python -m uvicorn app:app --host 0.0.0.0 --port 8000")
        print("   2. Backend API: cd backend && npm start")
        return

    print("\n💡 Tip: Try these malicious payloads:")
    print("   SQL Injection: GET /login?username=admin' OR '1'='1")
    print("   XSS: POST /search with body: <script>alert('xss')</script>")
    print("   Path Traversal: GET /../../../etc/passwd")
    print("\n" + "="*60)

    while True:
        try:
            # Get user input
            request_data = get_user_input()

            # Send to WAF
            result = send_to_waf(request_data)

            # Display result
            if result:
                display_result(result, request_data)

            # Ask to continue
            print("\n" + "-"*40)
            choice = input("🔄 Test another request? (y/n) [y]: ").strip().lower()
            if choice in ['n', 'no', 'quit', 'exit']:
                break
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    print("\n🎉 Session ended. Check your dashboard for malicious detections!")

if __name__ == "__main__":
    main()