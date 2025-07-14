-- Notice Board Database Setup Script
-- This script creates the notice_board database and required tables

-- Create database
CREATE DATABASE IF NOT EXISTS notice_board;
USE notice_board;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user'
);

-- Create notices table
CREATE TABLE notices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    date_posted DATETIME DEFAULT CURRENT_TIMESTAMP,
    priority ENUM('High', 'Medium', 'Low') NOT NULL DEFAULT 'Medium',
    category VARCHAR(50) NOT NULL,
    posted_by INT NOT NULL,
    FOREIGN KEY (posted_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert two predefined users
INSERT INTO users (username, password_hash, role) VALUES 
('admin', '$2y$10$example_admin_password_hash_here', 'admin'),
('user1', '$2y$10$example_user_password_hash_here', 'user');

-- Optional: Insert some sample notices for testing
INSERT INTO notices (title, content, priority, category, posted_by) VALUES 
('Welcome to Notice Board', 'This is a sample notice to test the system.', 'High', 'General', 1),
('System Maintenance', 'Scheduled maintenance will occur this weekend.', 'Medium', 'IT', 1);
