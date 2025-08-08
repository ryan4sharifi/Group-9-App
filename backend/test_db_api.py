#!/usr/bin/env python3
"""
Live API Integration Test Script
Tests the running FastAPI server and database connectivity
Usage: python test_db_api.py (requires server running on localhost:8000)
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_server_availability():
    """Test if the server is running and accessible"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server is running: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Features: {len(data.get('features', []))} listed")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        print("   Please start the server with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Server availability test failed: {e}")
        return False

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Health endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Database: {data.get('database', {}).get('status', 'N/A')}")
            print(f"   WebSocket connections: {data.get('websocket_connections', 0)}")
        return True
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False

def test_api_documentation():
    """Test API documentation endpoints"""
    try:
        # Test interactive docs
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"✅ API Documentation (/docs): {response.status_code}")
        
        # Test OpenAPI schema
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        print(f"✅ OpenAPI Schema: {response.status_code}")
        if response.status_code == 200:
            schema = response.json()
            paths_count = len(schema.get('paths', {}))
            print(f"   API endpoints documented: {paths_count}")
        
        return True
    except Exception as e:
        print(f"❌ API documentation test failed: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints (structure only)"""
    print("\n🔐 Testing Authentication Endpoints...")
    
    auth_tests = [
        {"endpoint": "/auth/register", "method": "POST", "expected": [422, 400]},  # Missing data
        {"endpoint": "/auth/login", "method": "POST", "expected": [422, 400]},    # Missing data
    ]
    
    for test in auth_tests:
        try:
            if test["method"] == "POST":
                response = requests.post(f"{BASE_URL}{test['endpoint']}", json={}, timeout=5)
            else:
                response = requests.get(f"{BASE_URL}{test['endpoint']}", timeout=5)
            
            if response.status_code in test["expected"]:
                print(f"✅ {test['endpoint']}: {response.status_code} (expected)")
            else:
                print(f"⚠️ {test['endpoint']}: {response.status_code} (unexpected)")
                
        except Exception as e:
            print(f"❌ {test['endpoint']} failed: {e}")

def test_api_endpoints():
    """Test main API endpoints"""
    print("\n🌐 Testing Main API Endpoints...")
    
    api_tests = [
        {"endpoint": "/api/events", "method": "GET", "expected": [200, 401, 403]},
        {"endpoint": "/api/states", "method": "GET", "expected": [200]},
        {"endpoint": "/api/health/distance", "method": "GET", "expected": [200]},
    ]
    
    for test in api_tests:
        try:
            if test["method"] == "POST":
                response = requests.post(f"{BASE_URL}{test['endpoint']}", json={}, timeout=5)
            else:
                response = requests.get(f"{BASE_URL}{test['endpoint']}", timeout=5)
            
            if response.status_code in test["expected"]:
                print(f"✅ {test['endpoint']}: {response.status_code}")
            else:
                print(f"⚠️ {test['endpoint']}: {response.status_code} (unexpected)")
                
        except Exception as e:
            print(f"❌ {test['endpoint']} failed: {e}")

def test_websocket_endpoint():
    """Test WebSocket endpoint availability"""
    print("\n🔌 Testing WebSocket Endpoint...")
    try:
        # We can't easily test WebSocket with requests, but we can check if the endpoint exists
        # by trying to connect and seeing if we get the right error
        response = requests.get(f"{BASE_URL}/ws/test123", timeout=5)
        # WebSocket endpoints typically return 426 Upgrade Required for HTTP requests
        if response.status_code in [426, 400, 405]:
            print(f"✅ WebSocket endpoint exists: {response.status_code}")
        else:
            print(f"⚠️ WebSocket endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

def main():
    """Main test function"""
    print("� LIVE API INTEGRATION TEST")
    print("=" * 50)
    print("Testing Group 9 App Backend API...")
    
    # Test 1: Server availability
    print("\n1️⃣ Testing server availability...")
    if not test_server_availability():
        print("\n❌ Cannot proceed - server is not running")
        print("Start the server with: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Test 2: Health check
    print("\n2️⃣ Testing health endpoint...")
    test_health_endpoint()
    
    # Test 3: API documentation
    print("\n3️⃣ Testing API documentation...")
    test_api_documentation()
    
    # Test 4: Authentication endpoints
    test_auth_endpoints()
    
    # Test 5: Main API endpoints
    test_api_endpoints()
    
    # Test 6: WebSocket endpoint
    test_websocket_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ Live API integration test completed!")
    print("📊 Summary: Server is operational and responding to requests")
    print("💡 For full functionality testing, run the pytest suite")

if __name__ == "__main__":
    main() 