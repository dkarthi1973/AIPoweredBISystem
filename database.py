import sqlite3
from contextlib import contextmanager
import os

DATABASE_URL = "crud_app.db"

def init_db():
    """Initialize database with tables"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Roles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                role_id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_name TEXT UNIQUE NOT NULL,
                description TEXT
            )
        ''')
        
        # Master table - Product Category (composite primary key)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_category (
                category_id INTEGER,
                subcategory_id INTEGER,
                category_name TEXT UNIQUE NOT NULL,
                description TEXT,
                PRIMARY KEY (category_id, subcategory_id)
            )
        ''')
        
        # Detail table - Product (foreign key to master)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                subcategory_id INTEGER NOT NULL,
                product_name TEXT UNIQUE NOT NULL,
                price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL,
                FOREIGN KEY (category_id, subcategory_id) 
                REFERENCES product_category(category_id, subcategory_id)
                ON DELETE CASCADE
            )
        ''')
        
        # Updated Users table with role_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                role_id INTEGER NOT NULL DEFAULT 3, -- Default to 'user' role
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES roles(role_id)
            )
        ''')
        
        # Insert default roles
        cursor.execute('''
            INSERT OR IGNORE INTO roles (role_id, role_name, description) VALUES
            (1, 'admin', 'Full system access'),
            (2, 'manager', 'Manage products and categories'),
            (3, 'user', 'Read-only access')
        ''')
        
        conn.commit()
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        raise
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_connection():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()