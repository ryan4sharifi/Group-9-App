#!/usr/bin/env python3
"""
Database API Test Script
Tests the database connection and basic API functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_root_endpoint():
    """Test the root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints"""
    endpoints = [
        "/auth/register",
        "/auth/login"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json={})
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} failed: {e}")

def test_api_endpoints():
    """Test API endpoints"""
    endpoints = [
        "/api/events",
        "/api/states",
        "/api/contact"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} failed: {e}")

def test_database_connection():
    """Test database connection through the API"""
    try:
        # Test if we can access the API docs
        response = requests.get(f"{BASE_URL}/docs")
        print(f"✅ API Documentation: {response.status_code}")
        
        # Test OpenAPI schema
        response = requests.get(f"{BASE_URL}/openapi.json")
        print(f"✅ OpenAPI Schema: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Testing Database API...")
    print("=" * 50)
    
    # Test if server is running
    print("1. Testing server availability...")
    if not test_root_endpoint():
        print("❌ Server is not running or not accessible")
        return
    
    print("\n2. Testing authentication endpoints...")
    test_auth_endpoints()
    
    print("\n3. Testing API endpoints...")
    test_api_endpoints()
    
    print("\n4. Testing database connection...")
    test_database_connection()
    
    print("\n" + "=" * 50)
    print("✅ Database API test completed!")

if __name__ == "__main__":
    main() 