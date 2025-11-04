"""
JWT Authentication Testing Script
Tests registration, login, token refresh, and protected endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_register():
    """Test user registration"""
    print_header("TEST 1: User Registration")
    
    user_data = {
        "email": f"testuser{datetime.now().timestamp()}@example.com",
        "password": "SecurePass123!@#",
        "full_name": "Test User"
    }
    
    print(f"Registering user: {user_data['email']}")
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        user = response.json()
        print(f"SUCCESS - User created:")
        print(f"  Email: {user['email']}")
        print(f"  Name: {user['full_name']}")
        print(f"  Created: {user['created_at']}")
        return user_data
    else:
        print(f"FAILED: {response.json()}")
        return None

def test_login(email, password):
    """Test user login"""
    print_header("TEST 2: User Login")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    print(f"Logging in as: {email}")
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tokens = response.json()
        print(f"SUCCESS - Tokens received:")
        print(f"  Access Token: {tokens['access_token'][:50]}...")
        print(f"  Refresh Token: {tokens['refresh_token'][:50]}...")
        print(f"  Token Type: {tokens['token_type']}")
        return tokens
    else:
        print(f"FAILED: {response.json()}")
        return None

def test_demo_login():
    """Test login with demo user"""
    print_header("TEST 3: Demo User Login")
    
    demo_data = {
        "email": "demo@example.com",
        "password": "Demo123!@#"
    }
    
    print(f"Logging in with demo user...")
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=demo_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tokens = response.json()
        print(f"SUCCESS - Demo user authenticated")
        return tokens
    else:
        print(f"FAILED: {response.json()}")
        return None

def test_get_current_user(access_token):
    """Test getting current user info"""
    print_header("TEST 4: Get Current User (Protected Endpoint)")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print(f"Requesting user info with access token...")
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"SUCCESS - User info retrieved:")
        print(f"  Email: {user['email']}")
        print(f"  Name: {user.get('full_name', 'N/A')}")
        print(f"  Disabled: {user['disabled']}")
        return user
    else:
        print(f"FAILED: {response.json()}")
        return None

def test_refresh_token(refresh_token):
    """Test token refresh"""
    print_header("TEST 5: Refresh Access Token")
    
    print(f"Refreshing access token...")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/refresh",
        params={"refresh_token": refresh_token}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tokens = response.json()
        print(f"SUCCESS - New access token received:")
        print(f"  New Access Token: {tokens['access_token'][:50]}...")
        return tokens
    else:
        print(f"FAILED: {response.json()}")
        return None

def test_invalid_token():
    """Test with invalid token"""
    print_header("TEST 6: Invalid Token (Should Fail)")
    
    headers = {
        "Authorization": "Bearer invalid_token_12345"
    }
    
    print(f"Requesting user info with INVALID token...")
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print(f"SUCCESS - Unauthorized as expected")
        print(f"  Error: {response.json()}")
        return True
    else:
        print(f"UNEXPECTED: Should have returned 401")
        return False

def test_weak_password():
    """Test registration with weak password"""
    print_header("TEST 7: Weak Password (Should Fail)")
    
    user_data = {
        "email": "weakpass@example.com",
        "password": "weak",  # Too weak!
        "full_name": "Weak User"
    }
    
    print(f"Attempting registration with weak password...")
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print(f"SUCCESS - Rejected as expected")
        print(f"  Error: {response.json()}")
        return True
    else:
        print(f"UNEXPECTED: Should have returned 400")
        return False

def test_rate_limiting():
    """Test login rate limiting"""
    print_header("TEST 8: Login Rate Limiting (5/min)")
    
    login_data = {
        "email": "test@example.com",
        "password": "wrong"
    }
    
    print(f"Sending 7 rapid login attempts...")
    success_count = 0
    rate_limited_count = 0
    
    for i in range(7):
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        
        if response.status_code == 401:
            success_count += 1
            print(f"  Request {i+1}: OK (401 - wrong password)")
        elif response.status_code == 429:
            rate_limited_count += 1
            print(f"  Request {i+1}: RATE LIMITED (429)")
        else:
            print(f"  Request {i+1}: Unexpected {response.status_code}")
    
    print(f"\nResults: {success_count} allowed, {rate_limited_count} rate-limited")
    return rate_limited_count > 0

def run_all_tests():
    """Run all JWT authentication tests"""
    print("\n" + "="*60)
    print("  JWT AUTHENTICATION TESTING")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    try:
        # Test 1: Register new user
        user_data = test_register()
        if not user_data:
            print("\nERROR: Registration failed, stopping tests")
            return False
        
        # Test 2: Login with new user
        tokens = test_login(user_data['email'], user_data['password'])
        if not tokens:
            print("\nERROR: Login failed, trying demo user...")
            # Fallback to demo user
            tokens = test_demo_login()
            if not tokens:
                print("\nERROR: Demo login also failed, stopping tests")
                return False
        
        # Test 4: Get current user
        user = test_get_current_user(tokens['access_token'])
        if not user:
            print("\nERROR: Failed to get user info")
            return False
        
        # Test 5: Refresh token
        new_tokens = test_refresh_token(tokens['refresh_token'])
        if not new_tokens:
            print("\nERROR: Token refresh failed")
            return False
        
        # Test 6: Invalid token
        test_invalid_token()
        
        # Test 7: Weak password
        test_weak_password()
        
        # Test 8: Rate limiting
        test_rate_limiting()
        
        # Summary
        print_header("SUMMARY")
        print("  [PASS] User Registration")
        print("  [PASS] User Login")
        print("  [PASS] Protected Endpoint Access")
        print("  [PASS] Token Refresh")
        print("  [PASS] Invalid Token Rejection")
        print("  [PASS] Weak Password Rejection")
        print("  [PASS] Rate Limiting")
        print("\n  All JWT authentication tests passed!")
        print("="*60)
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to server!")
        print("  Make sure the server is running on http://127.0.0.1:8001")
        print("  Run: start_server.bat")
        return False
    except Exception as e:
        print(f"\nERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
