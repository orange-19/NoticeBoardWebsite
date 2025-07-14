"""
Database module for Notice Board application.
Provides MySQL connection management and helper functions for database operations.
"""

import mysql.connector
from mysql.connector import Error, pooling
from typing import Optional, Dict, List, Any, Tuple
import os
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'notice_board'),
    'charset': 'utf8mb4',
    'use_unicode': True,
    'autocommit': False
}

# Connection pool configuration
POOL_CONFIG = {
    'pool_name': 'notice_board_pool',
    'pool_size': 5,
    'pool_reset_session': True,
    **DB_CONFIG
}

# Initialize connection pool
_connection_pool = None

def _initialize_pool():
    """Initialize the MySQL connection pool."""
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = pooling.MySQLConnectionPool(**POOL_CONFIG)
            logger.info("MySQL connection pool initialized successfully")
        except Error as e:
            logger.error(f"Error initializing connection pool: {e}")
            raise

def get_connection():
    """
    Get a database connection from the pool.
    
    Returns:
        mysql.connector.connection: Database connection object
        
    Raises:
        mysql.connector.Error: If connection cannot be established
    """
    if _connection_pool is None:
        _initialize_pool()
    
    try:
        connection = _connection_pool.get_connection()
        logger.debug("Database connection acquired from pool")
        return connection
    except Error as e:
        logger.error(f"Error getting database connection: {e}")
        raise

@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Ensures proper connection cleanup.
    
    Yields:
        mysql.connector.connection: Database connection object
    """
    connection = None
    try:
        connection = get_connection()
        yield connection
    except Error as e:
        if connection:
            connection.rollback()
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()
            logger.debug("Database connection returned to pool")

def fetch_notices(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Fetch notices from the database with optional filtering.
    
    Args:
        filters (dict, optional): Dictionary of filters to apply
            - category: Filter by category
            - status: Filter by status (active, inactive, expired)
            - date_from: Filter notices from this date
            - date_to: Filter notices until this date
            - user_id: Filter by user who created the notice
            - search: Search in title and content
            - limit: Maximum number of results
            - offset: Number of results to skip
    
    Returns:
        List[Dict[str, Any]]: List of notice dictionaries
    """
    query = """
        SELECT n.id, n.title, n.content, n.category, n.status, n.priority,
               n.created_at, n.updated_at, n.expires_at, n.user_id,
               u.username, u.email
        FROM notices n
        LEFT JOIN users u ON n.user_id = u.id
        WHERE 1=1
    """
    
    params = []
    
    if filters:
        if 'category' in filters:
            query += " AND n.category = %s"
            params.append(filters['category'])
        
        if 'status' in filters:
            query += " AND n.status = %s"
            params.append(filters['status'])
        
        if 'date_from' in filters:
            query += " AND n.created_at >= %s"
            params.append(filters['date_from'])
        
        if 'date_to' in filters:
            query += " AND n.created_at <= %s"
            params.append(filters['date_to'])
        
        if 'user_id' in filters:
            query += " AND n.user_id = %s"
            params.append(filters['user_id'])
        
        if 'search' in filters:
            query += " AND (n.title LIKE %s OR n.content LIKE %s)"
            search_term = f"%{filters['search']}%"
            params.extend([search_term, search_term])
    
    query += " ORDER BY n.created_at DESC"
    
    if filters and 'limit' in filters:
        query += " LIMIT %s"
        params.append(filters['limit'])
        
        if 'offset' in filters:
            query += " OFFSET %s"
            params.append(filters['offset'])
    
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            notices = cursor.fetchall()
            cursor.close()
            
            logger.info(f"Fetched {len(notices)} notices from database")
            return notices
            
    except Error as e:
        logger.error(f"Error fetching notices: {e}")
        raise

def insert_notice(notice_data: Dict[str, Any]) -> int:
    """
    Insert a new notice into the database.
    
    Args:
        notice_data (dict): Dictionary containing notice data
            - title: Notice title (required)
            - content: Notice content (required)
            - category: Notice category (required)
            - priority: Notice priority (default: 'medium')
            - status: Notice status (default: 'active')
            - expires_at: Expiration date (optional)
            - user_id: ID of user creating the notice (required)
    
    Returns:
        int: ID of the inserted notice
    """
    required_fields = ['title', 'content', 'category', 'user_id']
    for field in required_fields:
        if field not in notice_data:
            raise ValueError(f"Missing required field: {field}")
    
    query = """
        INSERT INTO notices (title, content, category, priority, status, expires_at, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    params = (
        notice_data['title'],
        notice_data['content'],
        notice_data['category'],
        notice_data.get('priority', 'medium'),
        notice_data.get('status', 'active'),
        notice_data.get('expires_at'),
        notice_data['user_id']
    )
    
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            notice_id = cursor.lastrowid
            connection.commit()
            cursor.close()
            
            logger.info(f"Inserted notice with ID: {notice_id}")
            return notice_id
            
    except Error as e:
        logger.error(f"Error inserting notice: {e}")
        raise

def update_notice(notice_id: int, update_data: Dict[str, Any]) -> bool:
    """
    Update an existing notice in the database.
    
    Args:
        notice_id (int): ID of the notice to update
        update_data (dict): Dictionary containing fields to update
            - title: Updated title
            - content: Updated content
            - category: Updated category
            - priority: Updated priority
            - status: Updated status
            - expires_at: Updated expiration date
    
    Returns:
        bool: True if update was successful, False if no rows were affected
    """
    if not update_data:
        raise ValueError("No update data provided")
    
    # Build dynamic query based on provided fields
    set_clauses = []
    params = []
    
    allowed_fields = ['title', 'content', 'category', 'priority', 'status', 'expires_at']
    
    for field in allowed_fields:
        if field in update_data:
            set_clauses.append(f"{field} = %s")
            params.append(update_data[field])
    
    if not set_clauses:
        raise ValueError("No valid fields to update")
    
    # Add updated_at timestamp
    set_clauses.append("updated_at = NOW()")
    params.append(notice_id)
    
    query = f"UPDATE notices SET {', '.join(set_clauses)} WHERE id = %s"
    
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            rows_affected = cursor.rowcount
            connection.commit()
            cursor.close()
            
            success = rows_affected > 0
            logger.info(f"Updated notice {notice_id}: {success}")
            return success
            
    except Error as e:
        logger.error(f"Error updating notice {notice_id}: {e}")
        raise

def delete_notice(notice_id: int) -> bool:
    """
    Delete a notice from the database.
    
    Args:
        notice_id (int): ID of the notice to delete
    
    Returns:
        bool: True if deletion was successful, False if no rows were affected
    """
    query = "DELETE FROM notices WHERE id = %s"
    
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (notice_id,))
            rows_affected = cursor.rowcount
            connection.commit()
            cursor.close()
            
            success = rows_affected > 0
            logger.info(f"Deleted notice {notice_id}: {success}")
            return success
            
    except Error as e:
        logger.error(f"Error deleting notice {notice_id}: {e}")
        raise

def verify_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verify user credentials and return user information.
    
    Args:
        username (str): Username to verify
        password (str): Password to verify (should be hashed)
    
    Returns:
        dict or None: User information if credentials are valid, None otherwise
    """
    query = """
        SELECT id, username, email, role, created_at, last_login
        FROM users
        WHERE username = %s AND password = %s AND status = 'active'
    """
    
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                logger.info(f"User {username} verified successfully")
                return user
            else:
                logger.warning(f"Failed verification for user {username}")
                return None
                
    except Error as e:
        logger.error(f"Error verifying user {username}: {e}")
        raise

def initialize_database():
    """
    Initialize the database by creating necessary tables if they don't exist.
    This function should be called during application startup.
    """
    create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('admin', 'user') DEFAULT 'user',
            status ENUM('active', 'inactive') DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL
        )
    """
    
    create_notices_table = """
        CREATE TABLE IF NOT EXISTS notices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            category VARCHAR(50) NOT NULL,
            priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
            status ENUM('active', 'inactive', 'expired') DEFAULT 'active',
            user_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_category (category),
            INDEX idx_status (status),
            INDEX idx_created_at (created_at)
        )
    """
    
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            
            # Create users table
            cursor.execute(create_users_table)
            logger.info("Users table created/verified")
            
            # Create notices table
            cursor.execute(create_notices_table)
            logger.info("Notices table created/verified")
            
            connection.commit()
            cursor.close()
            
    except Error as e:
        logger.error(f"Error initializing database: {e}")
        raise

def get_notice_statistics() -> Dict[str, Any]:
    """
    Get statistics about notices (count by category, priority, status).
    
    Returns:
        Dict[str, Any]: Dictionary containing various statistics
    """
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            
            # Get total notice count
            cursor.execute("SELECT COUNT(*) as total FROM notices")
            total_notices = cursor.fetchone()['total']
            
            # Get count by category
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM notices 
                GROUP BY category 
                ORDER BY count DESC
            """)
            by_category = cursor.fetchall()
            
            # Get count by priority
            cursor.execute("""
                SELECT priority, COUNT(*) as count 
                FROM notices 
                GROUP BY priority 
                ORDER BY FIELD(priority, 'high', 'medium', 'low')
            """)
            by_priority = cursor.fetchall()
            
            # Get count by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM notices 
                GROUP BY status 
                ORDER BY count DESC
            """)
            by_status = cursor.fetchall()
            
            # Get recent notices count (last 30 days)
            cursor.execute("""
                SELECT COUNT(*) as recent_count 
                FROM notices 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """)
            recent_notices = cursor.fetchone()['recent_count']
            
            cursor.close()
            
            return {
                'total_notices': total_notices,
                'by_category': by_category,
                'by_priority': by_priority,
                'by_status': by_status,
                'recent_notices': recent_notices
            }
            
    except Error as e:
        logger.error(f"Error getting notice statistics: {e}")
        raise

def get_notice_by_id(notice_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific notice by ID.
    
    Args:
        notice_id (int): ID of the notice to retrieve
    
    Returns:
        Dict[str, Any] or None: Notice data if found, None otherwise
    """
    query = """
        SELECT n.id, n.title, n.content, n.category, n.status, n.priority,
               n.created_at, n.updated_at, n.expires_at, n.user_id,
               u.username, u.email
        FROM notices n
        LEFT JOIN users u ON n.user_id = u.id
        WHERE n.id = %s
    """
    
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (notice_id,))
            notice = cursor.fetchone()
            cursor.close()
            
            if notice:
                logger.info(f"Retrieved notice with ID: {notice_id}")
                return notice
            else:
                logger.warning(f"Notice with ID {notice_id} not found")
                return None
                
    except Error as e:
        logger.error(f"Error retrieving notice {notice_id}: {e}")
        raise

def close_connection_pool():
    """
    Close the connection pool.
    This should be called during application shutdown.
    """
    global _connection_pool
    if _connection_pool:
        _connection_pool.close()
        _connection_pool = None
        logger.info("Connection pool closed")

# Health check function
def check_database_health() -> Dict[str, Any]:
    """
    Check database connectivity and return health status.
    
    Returns:
        dict: Health status information
    """
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            
            return {
                'status': 'healthy',
                'database': DB_CONFIG['database'],
                'host': DB_CONFIG['host'],
                'port': DB_CONFIG['port']
            }
            
    except Error as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'database': DB_CONFIG['database'],
            'host': DB_CONFIG['host'],
            'port': DB_CONFIG['port']
        }
