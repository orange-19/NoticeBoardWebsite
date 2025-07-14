# Notice Board Website

A comprehensive notice board web application built with Streamlit, featuring user authentication, database integration, and an admin dashboard.

## Features

### 🔐 Authentication System
- Secure login with database and fallback credentials
- Session management with Streamlit session state
- Role-based access control (admin/user)

### 🔧 Admin Dashboard
- **Add Notice**: Form to create new notices with title, content, priority, category
- **Manage Notices**: Table view with edit/delete functionality, search and filter options
- **Statistics**: Visual analytics with charts showing notice distribution by category, priority, and status

### 🎨 User Interface
- Clean, modern Streamlit interface
- Responsive design with proper validation
- Interactive forms and data tables
- Visual charts and statistics

## Database Schema

The database consists of two main tables:

### Users Table
- `id` (INT, Primary Key, Auto Increment)
- `username` (VARCHAR, Unique, Not Null)
- `email` (VARCHAR, Unique, Not Null)
- `password` (VARCHAR, Not Null)
- `role` (ENUM: 'admin', 'user', Default: 'user')
- `status` (ENUM: 'active', 'inactive', Default: 'active')
- `created_at` (TIMESTAMP, Default: CURRENT_TIMESTAMP)
- `last_login` (TIMESTAMP, NULL)

### Notices Table
- `id` (INT, Primary Key, Auto Increment)
- `title` (VARCHAR(255), Not Null)
- `content` (TEXT, Not Null)
- `category` (VARCHAR(50), Not Null)
- `priority` (ENUM: 'low', 'medium', 'high', Default: 'medium')
- `status` (ENUM: 'active', 'inactive', 'expired', Default: 'active')
- `user_id` (INT, Foreign Key to users.id)
- `created_at` (TIMESTAMP, Default: CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP, Default: CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
- `expires_at` (TIMESTAMP, NULL)

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
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
   
   Or alternatively:
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

### Application Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/orange-19/NoticeBoardWebsite.git
   cd NoticeBoardWebsite
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Database Connection**
   Update the database configuration in `db.py` or set environment variables:
   ```bash
   export DB_HOST=localhost
   export DB_PORT=3306
   export DB_USER=root
   export DB_PASSWORD=your_password
   export DB_NAME=notice_board
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```
   
   Or use the startup script:
   ```bash
   python run_app.py
   ```

5. **Access the Application**
   - Open your browser to `http://localhost:8501`
   - Use the demo accounts to log in

### Demo User Accounts

The application includes the following demo accounts:

- **admin** (Password: `admin123`) - Administrator with full access
- **user** (Password: `user123`) - Regular user account
- **john_doe** (Password: `password123`) - Demo user account
- **jane_admin** (Password: `admin456`) - Demo admin account

## File Structure

```
├── app.py              # Main Streamlit application
├── admin_dashboard.py  # Admin dashboard with tabs
├── auth.py             # Authentication module
├── db.py               # Database connection and operations
├── db_setup.sql        # Database schema and sample data
├── requirements.txt    # Python dependencies
├── run_app.py          # Application startup script
├── test_login.py       # Login functionality tests
└── README.md           # This file
```

## Admin Dashboard Features

### 📝 Add Notice Tab
- Form with title, content, priority, category fields
- Optional expiration date setting
- Status selection (active/inactive/expired)
- Form validation and success feedback

### 📋 Manage Notices Tab
- Searchable and filterable notice table
- Edit notices inline with modal forms
- Delete notices with confirmation
- Filter by category, priority, status
- Search in title and content

### 📊 Statistics Tab
- Key metrics dashboard
- Visual charts using Plotly:
  - Pie chart for category distribution
  - Bar charts for priority and status distribution
- Detailed statistics tables
- Recent notices counter (last 30 days)

## Security Features

1. **Password Security**: SHA-256 hashing for stored passwords
2. **Database Permissions**: Connection pooling with proper error handling
3. **Session Management**: Secure session state management
4. **Input Validation**: Comprehensive form validation
5. **Error Handling**: Graceful error handling with user-friendly messages

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Check MySQL service status and credentials
2. **Permission Denied**: Ensure MySQL user has proper privileges
3. **Module Not Found**: Install all requirements with `pip install -r requirements.txt`
4. **Port Already in Use**: Change Streamlit port with `streamlit run app.py --server.port 8502`

### Reset Database

To completely reset the database:

```sql
DROP DATABASE IF EXISTS notice_board;
source db_setup.sql;
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).
