"""
Admin Dashboard for Notice Board System.
Provides interface for managing notices, users, and viewing statistics.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import plotly.express as px
import plotly.graph_objects as go
import db
import auth
from mysql.connector import Error

# Constants
CATEGORIES = ["General", "Academic", "Administrative", "Events", "Emergency", "Maintenance", "Other"]
PRIORITIES = ["low", "medium", "high"]
STATUSES = ["active", "inactive", "expired"]

def show_admin_dashboard():
    """Main admin dashboard interface."""
    
    # Check if user is admin
    if not auth.require_admin():
        st.error("Access denied. Admin privileges required.")
        return
    
    # Back to main dashboard button
    if st.button("← Back to Main Dashboard"):
        st.session_state.show_admin_dashboard = False
        st.rerun()
    
    st.title("🔧 Admin Dashboard")
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["➕ Add Notice", "📋 Manage Notices", "📊 Statistics"])
    
    with tab1:
        show_add_notice_tab()
    
    with tab2:
        show_manage_notices_tab()
    
    with tab3:
        show_statistics_tab()

def show_add_notice_tab():
    """Tab for adding new notices."""
    
    st.header("Add New Notice")
    
    with st.form("add_notice_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "Title *",
                placeholder="Enter notice title",
                help="Brief, descriptive title for the notice"
            )
            
            category = st.selectbox(
                "Category *",
                options=CATEGORIES,
                help="Select the appropriate category"
            )
            
            priority = st.selectbox(
                "Priority",
                options=PRIORITIES,
                index=1,  # Default to "medium"
                help="Set notice priority level"
            )
        
        with col2:
            status = st.selectbox(
                "Status",
                options=STATUSES,
                index=0,  # Default to "active"
                help="Set notice status"
            )
            
            # Optional expiration date
            expires_at = st.date_input(
                "Expiration Date (Optional)",
                value=None,
                help="Leave empty for no expiration"
            )
            
            # Convert expires_at to datetime if provided
            expires_datetime = None
            if expires_at:
                expires_datetime = datetime.combine(expires_at, datetime.min.time())
        
        # Content field (full width)
        content = st.text_area(
            "Content *",
            placeholder="Enter notice content...",
            height=150,
            help="Detailed content of the notice"
        )
        
        # Form submission
        submitted = st.form_submit_button("🚀 Create Notice", use_container_width=True)
        
        if submitted:
            if title and content and category:
                try:
                    # Get current user
                    user = auth.get_current_user()
                    
                    notice_data = {
                        'title': title,
                        'content': content,
                        'category': category,
                        'priority': priority,
                        'status': status,
                        'expires_at': expires_datetime,
                        'user_id': user['user_id']
                    }
                    
                    # Insert notice into database
                    notice_id = db.insert_notice(notice_data)
                    
                    st.success(f"✅ Notice created successfully! ID: {notice_id}")
                    st.balloons()
                    
                    # Clear form by rerunning
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error creating notice: {str(e)}")
            else:
                st.error("⚠️ Please fill in all required fields (Title, Content, Category)")

def show_manage_notices_tab():
    """Tab for managing existing notices."""
    
    st.header("Manage Notices")
    
    # Filters section
    with st.expander("🔍 Search & Filter Options", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            search_term = st.text_input(
                "Search",
                placeholder="Search in title/content...",
                help="Search for notices by title or content"
            )
        
        with col2:
            filter_category = st.selectbox(
                "Filter by Category",
                options=["All"] + CATEGORIES,
                help="Filter notices by category"
            )
        
        with col3:
            filter_priority = st.selectbox(
                "Filter by Priority",
                options=["All"] + PRIORITIES,
                help="Filter notices by priority"
            )
        
        with col4:
            filter_status = st.selectbox(
                "Filter by Status",
                options=["All"] + STATUSES,
                help="Filter notices by status"
            )
    
    # Build filters dictionary
    filters = {}
    if search_term:
        filters['search'] = search_term
    if filter_category != "All":
        filters['category'] = filter_category
    if filter_priority != "All":
        filters['priority'] = filter_priority
    if filter_status != "All":
        filters['status'] = filter_status
    
    try:
        # Fetch notices from database
        notices = db.fetch_notices(filters)
        
        if notices:
            # Display notices count
            st.info(f"Found {len(notices)} notice(s)")
            
            # Convert to DataFrame for better display
            df = pd.DataFrame(notices)
            
            # Format datetime columns
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            if 'updated_at' in df.columns:
                df['updated_at'] = pd.to_datetime(df['updated_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Display notices in a more user-friendly format
            for i, notice in enumerate(notices):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Notice header
                        priority_color = {
                            'high': '🔴',
                            'medium': '🟡',
                            'low': '🟢'
                        }
                        
                        status_color = {
                            'active': '✅',
                            'inactive': '⏸️',
                            'expired': '❌'
                        }
                        
                        st.markdown(
                            f"**{priority_color.get(notice['priority'], '🟡')} {notice['title']}** "
                            f"({status_color.get(notice['status'], '❓')} {notice['status'].title()})"
                        )
                        
                        # Notice details
                        st.markdown(f"**Category:** {notice['category']} | **Priority:** {notice['priority'].title()}")
                        st.markdown(f"**Created:** {notice['created_at']} | **Author:** {notice['username']}")
                        
                        # Content preview
                        content_preview = notice['content'][:200] + "..." if len(notice['content']) > 200 else notice['content']
                        st.markdown(f"**Content:** {content_preview}")
                    
                    with col2:
                        # Action buttons
                        col2a, col2b = st.columns(2)
                        
                        with col2a:
                            if st.button("✏️ Edit", key=f"edit_{notice['id']}"):
                                st.session_state.edit_notice_id = notice['id']
                                st.rerun()
                        
                        with col2b:
                            if st.button("🗑️ Delete", key=f"delete_{notice['id']}"):
                                if st.session_state.get(f"confirm_delete_{notice['id']}", False):
                                    # Actually delete
                                    try:
                                        db.delete_notice(notice['id'])
                                        st.success(f"Notice '{notice['title']}' deleted successfully!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error deleting notice: {str(e)}")
                                else:
                                    # Show confirmation
                                    st.session_state[f"confirm_delete_{notice['id']}"] = True
                                    st.warning("Click again to confirm deletion")
                    
                    st.markdown("---")
            
            # Handle edit notice
            if 'edit_notice_id' in st.session_state:
                show_edit_notice_modal(st.session_state.edit_notice_id)
        
        else:
            st.info("No notices found. Try adjusting your filters or create a new notice.")
    
    except Exception as e:
        st.error(f"Error loading notices: {str(e)}")

def show_edit_notice_modal(notice_id: int):
    """Modal for editing an existing notice."""
    
    st.markdown("---")
    st.subheader("✏️ Edit Notice")
    
    try:
        # Get notice data
        notice = db.get_notice_by_id(notice_id)
        
        if not notice:
            st.error("Notice not found!")
            if st.button("Cancel"):
                del st.session_state.edit_notice_id
                st.rerun()
            return
        
        with st.form("edit_notice_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Title *", value=notice['title'])
                category = st.selectbox(
                    "Category *",
                    options=CATEGORIES,
                    index=CATEGORIES.index(notice['category']) if notice['category'] in CATEGORIES else 0
                )
                priority = st.selectbox(
                    "Priority",
                    options=PRIORITIES,
                    index=PRIORITIES.index(notice['priority']) if notice['priority'] in PRIORITIES else 1
                )
            
            with col2:
                status = st.selectbox(
                    "Status",
                    options=STATUSES,
                    index=STATUSES.index(notice['status']) if notice['status'] in STATUSES else 0
                )
                
                # Handle expiration date
                current_expires = None
                if notice['expires_at']:
                    current_expires = notice['expires_at'].date() if hasattr(notice['expires_at'], 'date') else notice['expires_at']
                
                expires_at = st.date_input(
                    "Expiration Date (Optional)",
                    value=current_expires,
                    help="Leave empty for no expiration"
                )
            
            content = st.text_area("Content *", value=notice['content'], height=150)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    if title and content and category:
                        try:
                            expires_datetime = None
                            if expires_at:
                                expires_datetime = datetime.combine(expires_at, datetime.min.time())
                            
                            update_data = {
                                'title': title,
                                'content': content,
                                'category': category,
                                'priority': priority,
                                'status': status,
                                'expires_at': expires_datetime
                            }
                            
                            success = db.update_notice(notice_id, update_data)
                            
                            if success:
                                st.success("✅ Notice updated successfully!")
                                del st.session_state.edit_notice_id
                                st.rerun()
                            else:
                                st.error("❌ Failed to update notice")
                        
                        except Exception as e:
                            st.error(f"❌ Error updating notice: {str(e)}")
                    else:
                        st.error("⚠️ Please fill in all required fields")
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    del st.session_state.edit_notice_id
                    st.rerun()
    
    except Exception as e:
        st.error(f"Error loading notice for editing: {str(e)}")

def show_statistics_tab():
    """Tab for displaying notice statistics."""
    
    st.header("📊 Notice Statistics")
    
    try:
        # Get statistics from database
        stats = db.get_notice_statistics()
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Notices",
                value=stats['total_notices'],
                help="Total number of notices in the system"
            )
        
        with col2:
            st.metric(
                label="Recent Notices",
                value=stats['recent_notices'],
                help="Notices created in the last 30 days"
            )
        
        with col3:
            active_count = sum(item['count'] for item in stats['by_status'] if item['status'] == 'active')
            st.metric(
                label="Active Notices",
                value=active_count,
                help="Currently active notices"
            )
        
        with col4:
            categories_count = len(stats['by_category'])
            st.metric(
                label="Categories",
                value=categories_count,
                help="Number of notice categories"
            )
        
        st.markdown("---")
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Notices by Category")
            if stats['by_category']:
                # Create pie chart for categories
                categories_df = pd.DataFrame(stats['by_category'])
                fig_category = px.pie(
                    categories_df,
                    values='count',
                    names='category',
                    title='Distribution by Category'
                )
                st.plotly_chart(fig_category, use_container_width=True)
            else:
                st.info("No category data available")
        
        with col2:
            st.subheader("🎯 Notices by Priority")
            if stats['by_priority']:
                # Create bar chart for priorities
                priorities_df = pd.DataFrame(stats['by_priority'])
                fig_priority = px.bar(
                    priorities_df,
                    x='priority',
                    y='count',
                    title='Distribution by Priority',
                    color='priority',
                    color_discrete_map={
                        'high': '#ff4444',
                        'medium': '#ffaa44',
                        'low': '#44ff44'
                    }
                )
                st.plotly_chart(fig_priority, use_container_width=True)
            else:
                st.info("No priority data available")
        
        # Status distribution
        st.subheader("📊 Notices by Status")
        if stats['by_status']:
            status_df = pd.DataFrame(stats['by_status'])
            fig_status = px.bar(
                status_df,
                x='status',
                y='count',
                title='Distribution by Status',
                color='status',
                color_discrete_map={
                    'active': '#44ff44',
                    'inactive': '#ffaa44',
                    'expired': '#ff4444'
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No status data available")
        
        # Detailed statistics table
        st.subheader("📋 Detailed Statistics")
        
        tab1, tab2, tab3 = st.tabs(["By Category", "By Priority", "By Status"])
        
        with tab1:
            if stats['by_category']:
                st.dataframe(
                    pd.DataFrame(stats['by_category']),
                    use_container_width=True
                )
            else:
                st.info("No category statistics available")
        
        with tab2:
            if stats['by_priority']:
                st.dataframe(
                    pd.DataFrame(stats['by_priority']),
                    use_container_width=True
                )
            else:
                st.info("No priority statistics available")
        
        with tab3:
            if stats['by_status']:
                st.dataframe(
                    pd.DataFrame(stats['by_status']),
                    use_container_width=True
                )
            else:
                st.info("No status statistics available")
    
    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")
        st.info("This might be due to database connection issues or empty data.")

def main():
    """Main function for testing the admin dashboard."""
    
    st.set_page_config(
        page_title="Admin Dashboard - Notice Board",
        page_icon="🔧",
        layout="wide"
    )
    
    # Initialize session state
    auth.initialize_session_state()
    
    # For testing, set admin session state
    if not auth.is_authenticated():
        st.session_state.logged_in = True
        st.session_state.username = "admin"
        st.session_state.role = "admin"
        st.session_state.user_id = 1
    
    show_admin_dashboard()

if __name__ == "__main__":
    main()
