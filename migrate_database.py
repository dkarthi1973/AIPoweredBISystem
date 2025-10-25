
import sqlite3
import os

def migrate_database():
    """Migrate existing database to add unique constraints"""
    DATABASE_URL = "crud_app.db"
    
    if not os.path.exists(DATABASE_URL):
        print("❌ Database file not found. Please run the application first to create it.")
        return
    
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("🔄 Starting database migration...")
        
        # Check if unique constraints already exist
        cursor.execute("PRAGMA index_list(product_category)")
        category_indexes = [index[1] for index in cursor.fetchall()]
        
        cursor.execute("PRAGMA index_list(product)")
        product_indexes = [index[1] for index in cursor.fetchall()]
        
        # Add unique constraint to category_name if not exists
        if 'sqlite_autoindex_product_category_3' not in category_indexes:
            print("📁 Adding unique constraint to category_name...")
            
            # Create a temporary table with the new schema
            cursor.execute('''
                CREATE TABLE product_category_new (
                    category_id INTEGER,
                    subcategory_id INTEGER,
                    category_name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    PRIMARY KEY (category_id, subcategory_id)
                )
            ''')
            
            # Copy data from old table
            cursor.execute('''
                INSERT INTO product_category_new 
                SELECT category_id, subcategory_id, category_name, description 
                FROM product_category
            ''')
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE product_category")
            cursor.execute("ALTER TABLE product_category_new RENAME TO product_category")
            print("✅ Added unique constraint to category_name")
        else:
            print("✅ category_name unique constraint already exists")
        
        # Add unique constraint to product_name if not exists
        if 'sqlite_autoindex_product_2' not in product_indexes:
            print("📦 Adding unique constraint to product_name...")
            
            # Create a temporary table with the new schema
            cursor.execute('''
                CREATE TABLE product_new (
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
            
            # Copy data from old table
            cursor.execute('''
                INSERT INTO product_new 
                SELECT product_id, category_id, subcategory_id, product_name, price, stock_quantity 
                FROM product
            ''')
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE product")
            cursor.execute("ALTER TABLE product_new RENAME TO product")
            print("✅ Added unique constraint to product_name")
        else:
            print("✅ product_name unique constraint already exists")
        
        conn.commit()
        print("🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()
