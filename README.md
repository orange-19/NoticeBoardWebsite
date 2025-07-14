# Notice Board Database Setup

This project contains the MySQL database schema for a notice board application.

## Database Schema

The database consists of two main tables:

### Users Table
- `id` (INT, Primary Key, Auto Increment)
- `username` (VARCHAR, Unique, Not Null)
- `password_hash` (VARCHAR, Not Null)
- `role` (ENUM: 'admin', 'user', Default: 'user')

### Notices Table
- `id` (INT, Primary Key, Auto Increment)
- `title` (VARCHAR(200), Not Null)
- `content` (TEXT, Not Null)
- `date_posted` (DATETIME, Default: CURRENT_TIMESTAMP)
- `priority` (ENUM: 'High', 'Medium', 'Low', Default: 'Medium')
- `category` (VARCHAR(50), Not Null)
- `posted_by` (INT, Foreign Key to users.id)

## Setup Instructions

### Prerequisites
- MySQL Server 5.7 or higher
- MySQL client or MySQL Workbench

### Database Setup

1. **Start MySQL Service**
   ```bash
   # On Windows
   net start mysql

   # On Linux/Mac
   sudo systemctl start mysql
   # or
   sudo service mysql start
   ```

2. **Connect to MySQL**
   ```bash
   mysql -u root -p
   ```

3. **Run the Setup Script**
   ```sql
   source db_setup.sql;
   ```
   
   Or alternatively, you can run the script directly:
   ```bash
   mysql -u root -p < db_setup.sql
   ```

4. **Verify Installation**
   ```sql
   USE notice_board;
   SHOW TABLES;
   SELECT * FROM users;
   SELECT * FROM notices;
   ```

### Default Users

The setup script creates two default users:

1. **Admin User**
   - Username: `admin`
   - Role: `admin`
   - Password Hash: `$2y$10$example_admin_password_hash_here`

2. **Regular User**
   - Username: `user1`
   - Role: `user`
   - Password Hash: `$2y$10$example_user_password_hash_here`

**Important:** The password hashes in the setup script are examples. In a real application, you should:
- Generate proper bcrypt hashes for actual passwords
- Use a secure password hashing library in your application
- Never store plain text passwords

### Configuration for Applications

When connecting to this database from your application, use the following connection parameters:

```
Database: notice_board
Host: localhost (or your MySQL server host)
Port: 3306 (default MySQL port)
Username: [your MySQL username]
Password: [your MySQL password]
```

## Database Relationships

- The `notices` table has a foreign key relationship with the `users` table
- `notices.posted_by` references `users.id`
- When a user is deleted, all their notices are also deleted (CASCADE)

## Sample Data

The setup script includes sample notices for testing purposes. You can remove these by running:

```sql
DELETE FROM notices WHERE id IN (1, 2);
```

## Security Notes

1. **Password Security**: Replace the example password hashes with properly generated hashes
2. **Database Permissions**: Create specific database users with limited permissions for your application
3. **Backup**: Regular database backups are recommended
4. **Environment Variables**: Store database credentials in environment variables, not in code

## Troubleshooting

### Common Issues

1. **"Database already exists" error**: The script uses `CREATE DATABASE IF NOT EXISTS`, so this shouldn't occur
2. **Permission denied**: Ensure your MySQL user has CREATE and INSERT privileges
3. **Foreign key constraint fails**: Ensure the users table is created before the notices table

### Reset Database

To completely reset the database:

```sql
DROP DATABASE IF EXISTS notice_board;
source db_setup.sql;
```

## Streamlit UI Application

This project now includes a complete Streamlit web application with user authentication.

### Running the Application

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   streamlit run app.py
   ```
   
   Or use the startup script:
   ```bash
   python run_app.py
   ```

3. **Access the Application**
   - Open your browser to `http://localhost:8501`
   - Use the demo accounts to log in

### Demo User Accounts

The application includes the following demo accounts:

- **admin** (Password: `admin123`) - Administrator with full access
- **user** (Password: `user123`) - Regular user account
- **john_doe** (Password: `password123`) - Demo user account
- **jane_admin** (Password: `admin456`) - Demo admin account

### Features

- **Authentication System**: Secure login with database and fallback credentials
- **Session Management**: Streamlit session state management
- **Role-based Access**: Different interfaces for admin and regular users
- **Responsive UI**: Clean, modern interface with proper validation
- **Error Handling**: Comprehensive error messages and validation

### File Structure

```
├── app.py              # Main Streamlit application
├── auth.py             # Authentication module
├── db.py               # Database connection module
├── requirements.txt    # Python dependencies
├── run_app.py          # Application startup script
├── test_login.py       # Login functionality tests
└── README.md           # This file
```

## Next Steps

After setting up the database, you can:
1. Create your application's database connection layer
2. Implement user authentication using the password hashes
3. Build CRUD operations for notices
4. Add additional tables as needed for your application
