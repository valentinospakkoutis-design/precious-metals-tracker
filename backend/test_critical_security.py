"""
Test Critical Security Features
- Account Lockout
- Token Blacklist (Logout)
- CSRF Protection (if implemented)
"""

import requests
import time
import json

BASE_URL = "http://localhost:8001"

def print_test(name):
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {name}")
    print(f"{'='*60}")

def print_result(passed, message):
    if passed:
        print(f"✅ PASSED: {message}")
    else:
        print(f"❌ FAILED: {message}")
    return passed

def test_account_lockout():
    """Test account lockout after 5 failed login attempts"""
    print_test("Account Lockout (Brute Force Protection)")
    
    test_email = f"lockout_test_{int(time.time())}@test.com"
    
    # Try to login 6 times with wrong password
    print(f"\n📝 Attempting 6 failed logins for: {test_email}")
    
    failed_count = 0
    locked = False
    
    for i in range(1, 7):
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"email": test_email, "password": "WrongPassword123!"},
                timeout=5
            )
            
            print(f"\nAttempt {i}: Status {response.status_code}")
            
            if response.status_code == 401:
                failed_count += 1
                print(f"  ➜ Failed login (expected)")
            elif response.status_code == 423:
                locked = True
                print(f"  ➜ Account LOCKED! ✅")
                print(f"  ➜ Response: {response.json()}")
                break
            
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Request error: {e}")
            return False
    
    # Verify account was locked
    result = print_result(
        locked and failed_count >= 5,
        f"Account locked after {failed_count} failed attempts"
    )
    
    if not result:
        print(f"⚠️  Expected: Locked after 5 attempts")
        print(f"⚠️  Got: {failed_count} failed attempts, locked={locked}")
    
    return result

def test_token_blacklist():
    """Test token blacklist (logout functionality)"""
    print_test("Token Blacklist (Logout Security)")
    
    # First, login to get a valid token
    print("\n📝 Step 1: Login to get token")
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": "demo@example.com",
                "password": "Demo123!@#"
            },
            timeout=5
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        
        print(f"✅ Login successful, got token")
        
        # Test token works
        print("\n📝 Step 2: Verify token works")
        me_response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5
        )
        
        if me_response.status_code != 200:
            print(f"❌ Token validation failed: {me_response.status_code}")
            return False
        
        print(f"✅ Token works, user: {me_response.json()['email']}")
        
        # Logout (revoke token)
        print("\n📝 Step 3: Logout (revoke token)")
        logout_response = requests.post(
            f"{BASE_URL}/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5
        )
        
        if logout_response.status_code != 200:
            print(f"❌ Logout failed: {logout_response.status_code}")
            print(f"   Response: {logout_response.text}")
            return False
        
        print(f"✅ Logout successful")
        
        # Try to use the same token (should fail)
        print("\n📝 Step 4: Try to use revoked token")
        revoked_response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5
        )
        
        if revoked_response.status_code == 401:
            print(f"✅ Revoked token rejected (401)")
            detail = revoked_response.json().get('detail', '')
            print(f"   Response: {detail}")
            
            return print_result(
                "revoked" in detail.lower() or "invalid" in detail.lower(),
                "Token successfully blacklisted after logout"
            )
        else:
            print(f"❌ Revoked token still works! Status: {revoked_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting is still working"""
    print_test("Rate Limiting (Existing Feature)")
    
    print("\n📝 Sending 10 login requests rapidly...")
    
    rate_limited = False
    success_count = 0
    
    for i in range(10):
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={
                    "email": "rate_test@test.com",
                    "password": "Test123!@#"
                },
                timeout=5
            )
            
            if response.status_code == 429:
                rate_limited = True
                print(f"  Request {i+1}: 429 Too Many Requests ✅")
                break
            else:
                success_count += 1
                
        except requests.exceptions.RequestException:
            pass
    
    return print_result(
        rate_limited and success_count <= 5,
        f"Rate limiting active (allowed {success_count}/10, then blocked)"
    )

def test_password_strength():
    """Test password strength validation"""
    print_test("Password Strength Validation")
    
    weak_passwords = [
        ("123", "Too short"),
        ("password", "No uppercase, no numbers, no special chars"),
        ("Password", "No numbers, no special chars"),
        ("Password123", "No special chars"),
    ]
    
    all_rejected = True
    
    for password, reason in weak_passwords:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/register",
                json={
                    "email": f"weak_{int(time.time())}@test.com",
                    "password": password,
                    "full_name": "Test User"
                },
                timeout=5
            )
            
            if response.status_code == 400:
                print(f"✅ Rejected '{password}' - {reason}")
            else:
                print(f"❌ Accepted weak password '{password}'")
                all_rejected = False
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Request error: {e}")
            all_rejected = False
    
    return print_result(all_rejected, "All weak passwords rejected")

def run_all_tests():
    """Run all critical security tests"""
    print("\n" + "="*60)
    print("🔒 CRITICAL SECURITY FEATURES TEST SUITE")
    print("="*60)
    print(f"\nServer: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        health = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        if health.status_code != 200:
            print(f"\n❌ Server not healthy! Status: {health.status_code}")
            return
    except requests.exceptions.RequestException:
        print(f"\n❌ Server not running at {BASE_URL}")
        print("   Start server with: start_server.bat")
        return
    
    print("✅ Server is running\n")
    
    # Run tests
    results = []
    
    results.append(("Account Lockout", test_account_lockout()))
    time.sleep(1)  # Small delay between tests
    
    results.append(("Token Blacklist", test_token_blacklist()))
    time.sleep(1)
    
    results.append(("Rate Limiting", test_rate_limiting()))
    time.sleep(1)
    
    results.append(("Password Strength", test_password_strength()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"Coverage: {(passed/total)*100:.0f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Security features working correctly.")
    else:
        print(f"⚠️  {total-passed} test(s) failed. Review implementation.")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    run_all_tests()
