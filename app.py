"""
Main Streamlit application for Notice Board system.
Handles user authentication and routing based on login status.
"""

import streamlit as st
import auth

def main():
    """Main application entry point."""
    
    # Initialize session state
    auth.initialize_session_state()
    
    # Configure page
    st.set_page_config(
        page_title="Notice Board System",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main application logic
    if not st.session_state.logged_in:
        # Show login page if user is not logged in
        show_login_page()
    else:
        # Show main application if user is logged in
        show_main_app()

def show_login_page():
    """Display the login page with authentication form."""
    
    st.title("🔐 Notice Board System")
    st.markdown("---")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Please log in to continue")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                help="Use 'admin' or 'user' for demo accounts"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                help="Use 'admin123' or 'user123' for demo accounts"
            )
            
            submit_button = st.form_submit_button(
                "🔓 Login",
                use_container_width=True
            )
            
            if submit_button:
                if username and password:
                    # Call auth.login() and handle validation
                    role = auth.login(username, password)
                    if role:
                        st.success(f"✅ Successfully logged in as {username} ({role})")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password. Please try again.")
                else:
                    st.error("⚠️ Please enter both username and password.")
        
        # Show available demo users
        with st.expander("🔍 Demo User Accounts", expanded=False):
            st.markdown("**Available test accounts:**")
            
            demo_users = [
                ("admin", "admin123", "Administrator with full access"),
                ("user", "user123", "Regular user account"),
                ("john_doe", "password123", "Demo user account"),
                ("jane_admin", "admin456", "Demo admin account")
            ]
            
            for username, password, description in demo_users:
                st.markdown(f"- **{username}** (Password: `{password}`) - {description}")

def show_main_app():
    """Display the main application interface for logged-in users."""
    
    # Show user info in sidebar
    auth.show_user_info()
    
    # Main content area
    st.title("📋 Notice Board System")
    st.markdown("---")
    
    # Get current user info
    user = auth.get_current_user()
    
    if user:
        st.success(f"Welcome back, {user['username']}! 👋")
        st.info(f"Role: {user['role']} | Email: {user['email']}")
        
        # Main application content (placeholder)
        st.subheader("📝 Main Dashboard")
        st.write("This is where the main notice board functionality would go.")
        
        # Admin-specific content
        if auth.is_admin():
            st.subheader("🔧 Admin Panel")
            st.write("Access admin features below.")
            
            # Admin actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Admin Dashboard"):
                    st.session_state.show_admin_dashboard = True
                    st.rerun()
            
            with col2:
                if st.button("👥 Manage Users"):
                    st.info("User management interface would open here")
            
            # Show admin dashboard if requested
            if st.session_state.get('show_admin_dashboard', False):
                from admin_dashboard import show_admin_dashboard
                show_admin_dashboard()
        
        # User-specific content
        else:
            st.subheader("📖 Your Notices")
            st.write("Your personal notices would be displayed here.")
            
            if st.button("➕ Create New Notice"):
                st.info("Notice creation form would open here")
        
        # Common actions
        st.subheader("⚙️ Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Search Notices"):
                st.info("Search functionality would open here")
        
        with col2:
            if st.button("📊 View Statistics"):
                st.info("Statistics dashboard would open here")
        
        with col3:
            if st.button("⚙️ Settings"):
                st.info("User settings would open here")
    
    else:
        st.error("Error: Unable to retrieve user information")
        if st.button("🔄 Refresh"):
            st.rerun()

if __name__ == "__main__":
    main()
