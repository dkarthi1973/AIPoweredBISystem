from database import get_db_connection
from auth import AuthHandler
from schemas import CRUDException
import sqlite3
import re

class UserCRUD:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        if not email or '@' not in email:
            return False
        return True

    @staticmethod
    def get_role_name(role_id: int) -> str:
        """Get role name from role_id"""
        roles = {
            1: "admin",
            2: "manager", 
            3: "user"
        }
        return roles.get(role_id, "user")

    @staticmethod
    def init_users_table():
        """Initialize users table with some sample users"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Clear existing sample users to avoid conflicts
                cursor.execute("DELETE FROM users WHERE username IN ('admin', 'user1', 'manager', 'testuser')")
                
                # Create sample users with different roles
                sample_users = [
                    ("admin", "admin@example.com", AuthHandler.get_password_hash("admin123"), "Administrator", 1),  # admin
                    ("manager", "manager@example.com", AuthHandler.get_password_hash("manager123"), "Manager User", 2),  # manager
                    ("user1", "user1@example.com", AuthHandler.get_password_hash("password123"), "Regular User", 3),  # user
                    ("testuser", "test@example.com", AuthHandler.get_password_hash("test123"), "Test User", 3),  # user
                ]
                
                for username, email, hashed_password, full_name, role_id in sample_users:
                    try:
                        cursor.execute(
                            "INSERT INTO users (username, email, hashed_password, full_name, role_id) VALUES (?, ?, ?, ?, ?)",
                            (username, email, hashed_password, full_name, role_id)
                        )
                        print(f"✅ Created user: {username} with role_id: {role_id}")
                    except sqlite3.IntegrityError as e:
                        print(f"⚠️ User {username} already exists: {e}")
                        continue
                
                conn.commit()
                print("✅ Users initialized successfully!")
                
        except Exception as e:
            print(f"❌ User initialization error: {e}")
            raise

    @staticmethod
    def get_user_by_username(username: str):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.*, r.role_name 
                    FROM users u 
                    JOIN roles r ON u.role_id = r.role_id 
                    WHERE u.username = ? AND u.is_active = TRUE
                ''', (username,))
                user = cursor.fetchone()
                return dict(user) if user else None
        except Exception as e:
            print(f"❌ Error getting user {username}: {e}")
            return None

    @staticmethod
    def get_all_users():
        """Get all users with their roles"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.id, u.username, u.email, u.full_name, u.role_id, r.role_name, u.is_active, u.created_at
                    FROM users u 
                    JOIN roles r ON u.role_id = r.role_id
                    ORDER BY u.created_at DESC
                ''')
                users = cursor.fetchall()
                return [dict(user) for user in users]
        except Exception as e:
            print(f"❌ Error getting all users: {e}")
            return []

    @staticmethod
    def authenticate_user(username: str, password: str):
        try:
            print(f"🔐 Authenticating user: {username}")
            user = UserCRUD.get_user_by_username(username)
            if not user:
                print(f"❌ User not found: {username}")
                return False
            
            print(f"✅ User found: {username}, role: {user['role_name']}")
            is_valid = AuthHandler.verify_password(password, user["hashed_password"])
            print(f"🔑 Password valid: {is_valid}")
            
            return user if is_valid else False
        except Exception as e:
            print(f"❌ Authentication error for {username}: {e}")
            return False

    @staticmethod
    def create_user(username: str, email: str, password: str, full_name: str = None, role_id: int = 3):
        # Basic validation
        if not username or not email or not password:
            raise CRUDException("All fields are required", 400)
        
        if len(password) < 6:
            raise CRUDException("Password must be at least 6 characters long", 400)
        
        # Validate role_id
        if role_id not in [1, 2, 3]:
            raise CRUDException("Invalid role ID. Must be 1 (admin), 2 (manager), or 3 (user)", 400)
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check if user already exists
                cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
                if cursor.fetchone():
                    raise CRUDException("Username or email already exists", 400)
                
                hashed_password = AuthHandler.get_password_hash(password)
                cursor.execute(
                    "INSERT INTO users (username, email, hashed_password, full_name, role_id) VALUES (?, ?, ?, ?, ?)",
                    (username, email, hashed_password, full_name, role_id)
                )
                conn.commit()
                
                return {
                    "username": username, 
                    "email": email, 
                    "full_name": full_name,
                    "role_id": role_id,
                    "role_name": UserCRUD.get_role_name(role_id),
                    "message": "User created successfully"
                }
        except sqlite3.Error as e:
            raise CRUDException(f"Database error: {e}", 500)

    @staticmethod
    def update_user_role(username: str, role_id: int, current_user_role: str):
        """Update user role (only admin can do this)"""
        if current_user_role != "admin":
            raise CRUDException("Only administrators can update user roles", 403)
        
        if role_id not in [1, 2, 3]:
            raise CRUDException("Invalid role ID", 400)
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                if not cursor.fetchone():
                    raise CRUDException("User not found", 404)
                
                cursor.execute(
                    "UPDATE users SET role_id = ? WHERE username = ?",
                    (role_id, username)
                )
                conn.commit()
                
                return {
                    "message": f"User {username} role updated to {UserCRUD.get_role_name(role_id)}",
                    "username": username,
                    "new_role": UserCRUD.get_role_name(role_id)
                }
        except sqlite3.Error as e:
            raise CRUDException(f"Database error: {e}", 500)

    @staticmethod
    def delete_user(username: str, current_user_role: str):
        """Delete user (only admin can do this)"""
        if current_user_role != "admin":
            raise CRUDException("Only administrators can delete users", 403)
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                if not cursor.fetchone():
                    raise CRUDException("User not found", 404)
                
                # Prevent admin from deleting themselves
                if username == "admin":
                    raise CRUDException("Cannot delete the main admin user", 400)
                
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                conn.commit()
                
                return {"message": f"User {username} deleted successfully"}
        except sqlite3.Error as e:
            raise CRUDException(f"Database error: {e}", 500)