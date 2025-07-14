"""
Authentication module for Notice Board application.
Provides login functionality with hard-coded credentials fallback, 
database integration, and Streamlit session state management.
"""

import streamlit as st
import hashlib
from typing import Optional, Dict, Any
import logging
from db import verify_user, get_db_connection
from mysql.connector import Error

# Configure logging
logger = logging.getLogger(__name__)

# Hard-coded credentials for fallback/testing
HARDCODED_USERS = {
    'admin': {
        'password': 'admin123',  # In production, this should be hashed
        'role': 'admin',
        'email': 'admin@noticeboard.com',
        'id': 1
    },
    'user': {
        'password': 'user123',   # In production, this should be hashed
        'role': 'user',
        'email': 'user@noticeboard.com',
        'id': 2
    },
    'john_doe': {
        'password': 'password123',
        'role': 'user',
        'email': 'john.doe@example.com',
        'id': 3
    },
    'jane_admin': {
        'password': 'admin456',
        'role': 'admin',
        'email': 'jane.admin@example.com',
        'id': 4
    }
}

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_hardcoded_credentials(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verify credentials against hard-coded users.
    
    Args:
        username (str): Username to verify
        password (str): Password to verify
        
    Returns:
        dict or None: User information if credentials are valid, None otherwise
    """
    if username in HARDCODED_USERS:
        stored_user = HARDCODED_USERS[username]
        if stored_user['password'] == password:
            logger.info(f"Hard-coded user {username} verified successfully")
            return {
                'id': stored_user['id'],
                'username': username,
                'email': stored_user['email'],
                'role': stored_user['role'],
                'created_at': None,
                'last_login': None
            }
    
    logger.warning(f"Failed hard-coded verification for user {username}")
    return None

def login(username: str, password: str) -> Optional[str]:
    """
    Authenticate user and return their role.
    First tries database authentication, then falls back to hard-coded credentials.
    
    Args:
        username (str): Username to authenticate
        password (str): Password to authenticate
        
    Returns:
        str or None: User role if authentication successful, None otherwise
    """
    if not username or not password:
        logger.warning("Login attempted with empty username or password")
        return None
    
    user_info = None
    
    # Try database authentication first
    try:
        hashed_password = hash_password(password)
        user_info = verify_user(username, hashed_password)
        
        if user_info:
            logger.info(f"Database authentication successful for user {username}")
        else:
            logger.info(f"Database authentication failed for user {username}, trying hard-coded credentials")
            # Fallback to hard-coded credentials
            user_info = verify_hardcoded_credentials(username, password)
            
    except Error as e:
        logger.error(f"Database error during authentication: {e}")
        logger.info("Falling back to hard-coded credentials due to database error")
        # Fallback to hard-coded credentials on database error
        user_info = verify_hardcoded_credentials(username, password)
    
    if user_info:
        # Update session state
        st.session_state.logged_in = True
        st.session_state.username = user_info['username']
        st.session_state.role = user_info['role']
        st.session_state.user_id = user_info['id']
        st.session_state.email = user_info.get('email', '')
        
        logger.info(f"User {username} logged in successfully with role {user_info['role']}")
        return user_info['role']
    
    logger.warning(f"Authentication failed for user {username}")
    return None

def logout():
    """
    Log out the current user by clearing session state.
    """
    username = st.session_state.get('username', 'Unknown')
    
    # Clear all authentication-related session state
    keys_to_clear = ['logged_in', 'username', 'role', 'user_id', 'email']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    logger.info(f"User {username} logged out successfully")

def is_authenticated() -> bool:
    """
    Check if user is currently authenticated.
    
    Returns:
        bool: True if user is logged in, False otherwise
    """
    return st.session_state.get('logged_in', False)

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get current user information from session state.
    
    Returns:
        dict or None: Current user information if logged in, None otherwise
    """
    if is_authenticated():
        return {
            'username': st.session_state.get('username'),
            'role': st.session_state.get('role'),
            'user_id': st.session_state.get('user_id'),
            'email': st.session_state.get('email', '')
        }
    return None

def get_user_role() -> Optional[str]:
    """
    Get current user's role.
    
    Returns:
        str or None: Current user's role if logged in, None otherwise
    """
    return st.session_state.get('role')

def is_admin() -> bool:
    """
    Check if current user is an admin.
    
    Returns:
        bool: True if current user is admin, False otherwise
    """
    return st.session_state.get('role') == 'admin'

def require_auth(redirect_to_login=True):
    """
    Decorator/function to require authentication.
    
    Args:
        redirect_to_login (bool): Whether to show login form if not authenticated
        
    Returns:
        bool: True if user is authenticated, False otherwise
    """
    if not is_authenticated():
        if redirect_to_login:
            st.warning("Please log in to access this page.")
            show_login_form()
        return False
    return True

def require_admin():
    """
    Require admin privileges. Shows error message if user is not admin.
    
    Returns:
        bool: True if user is admin, False otherwise
    """
    if not is_authenticated():
        st.error("Please log in to access this page.")
        return False
    
    if not is_admin():
        st.error("Admin privileges required to access this page.")
        return False
    
    return True

def show_login_form():
    """
    Display login form in Streamlit.
    """
    st.subheader("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:
                role = login(username, password)
                if role:
                    st.success(f"Successfully logged in as {username} ({role})")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter both username and password")

def show_user_info():
    """
    Display current user information in sidebar.
    """
    if is_authenticated():
        user = get_current_user()
        if user:
            st.sidebar.success(f"Logged in as: {user['username']}")
            st.sidebar.info(f"Role: {user['role']}")
            
            if st.sidebar.button("Logout"):
                logout()
                st.rerun()
    else:
        st.sidebar.warning("Not logged in")

def initialize_session_state():
    """
    Initialize session state variables if they don't exist.
    """
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    if 'role' not in st.session_state:
        st.session_state.role = None
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    if 'email' not in st.session_state:
        st.session_state.email = None

def preload_demo_users():
    """
    Preload demo users into database if they don't exist.
    This is useful for development/testing purposes.
    """
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            
            # Check if users already exist
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                logger.info("Preloading demo users into database")
                
                # Insert demo users
                demo_users = [
                    ('admin', 'admin@noticeboard.com', hash_password('admin123'), 'admin'),
                    ('user', 'user@noticeboard.com', hash_password('user123'), 'user'),
                    ('john_doe', 'john.doe@example.com', hash_password('password123'), 'user'),
                    ('jane_admin', 'jane.admin@example.com', hash_password('admin456'), 'admin')
                ]
                
                insert_query = """
                    INSERT INTO users (username, email, password, role)
                    VALUES (%s, %s, %s, %s)
                """
                
                cursor.executemany(insert_query, demo_users)
                connection.commit()
                
                logger.info(f"Preloaded {len(demo_users)} demo users into database")
            
            cursor.close()
            
    except Error as e:
        logger.error(f"Error preloading demo users: {e}")
        # Don't raise the error, just log it - hard-coded credentials will work as fallback

# Available users information for documentation/testing
AVAILABLE_USERS = {
    'admin': {
        'password': 'admin123',
        'role': 'admin',
        'description': 'Administrator with full access'
    },
    'user': {
        'password': 'user123',
        'role': 'user',
        'description': 'Regular user'
    },
    'john_doe': {
        'password': 'password123',
        'role': 'user',
        'description': 'Demo user account'
    },
    'jane_admin': {
        'password': 'admin456',
        'role': 'admin',
        'description': 'Demo admin account'
    }
}

def show_available_users():
    """
    Display available users for testing/demo purposes.
    """
    st.subheader("Available Demo Users")
    st.write("Use these credentials for testing:")
    
    for username, info in AVAILABLE_USERS.items():
        st.write(f"**{username}** (Password: `{info['password']}`) - {info['description']}")
