"""
Test script to validate the login functionality works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import auth

def test_login_functionality():
    """Test the login functionality with various scenarios."""
    
    print("Testing Login Functionality")
    print("=" * 40)
    
    # Test cases
    test_cases = [
        ("admin", "admin123", True, "admin"),
        ("user", "user123", True, "user"),
        ("john_doe", "password123", True, "user"),
        ("jane_admin", "admin456", True, "admin"),
        ("invalid_user", "wrong_password", False, None),
        ("admin", "wrong_password", False, None),
        ("", "password", False, None),
        ("username", "", False, None),
    ]
    
    for username, password, expected_success, expected_role in test_cases:
        print(f"\nTesting: username='{username}', password='{password}'")
        
        # Reset any previous session state
        import streamlit as st
        if hasattr(st, 'session_state'):
            for key in ['logged_in', 'username', 'role', 'user_id', 'email']:
                if key in st.session_state:
                    del st.session_state[key]
        
        # Initialize session state
        auth.initialize_session_state()
        
        # Test login
        result = auth.login(username, password)
        
        if expected_success:
            if result == expected_role:
                print(f"✅ PASS: Login successful, role = {result}")
            else:
                print(f"❌ FAIL: Expected role {expected_role}, got {result}")
        else:
            if result is None:
                print(f"✅ PASS: Login correctly rejected")
            else:
                print(f"❌ FAIL: Expected login rejection, but got role {result}")
    
    print("\n" + "=" * 40)
    print("Test completed!")

if __name__ == "__main__":
    test_login_functionality()
