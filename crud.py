from database import get_db_connection
from models import ProductCategoryCreate, ProductCategoryUpdate, ProductCreate, ProductUpdate
from schemas import CRUDException
from typing import List, Optional, Tuple

class ProductCategoryCRUD:
    @staticmethod
    def create_category(category: ProductCategoryCreate) -> dict:
        """Create a new product category"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if category already exists
            cursor.execute(
                "SELECT * FROM product_category WHERE category_id = ? AND subcategory_id = ?",
                (category.category_id, category.subcategory_id)
            )
            if cursor.fetchone():
                raise CRUDException("Category with this ID already exists", 400)
            
            # NEW: Check if category name already exists
            cursor.execute(
                "SELECT * FROM product_category WHERE category_name = ?",
                (category.category_name,)
            )
            if cursor.fetchone():
                raise CRUDException("Category name already exists. Please use a unique category name.", 400)
            
            cursor.execute(
                "INSERT INTO product_category (category_id, subcategory_id, category_name, description) VALUES (?, ?, ?, ?)",
                (category.category_id, category.subcategory_id, category.category_name, category.description)
            )
            conn.commit()
            
            return {**category.dict(), "message": "Category created successfully"}
    
    @staticmethod
    def get_category(category_id: int, subcategory_id: int) -> dict:
        """Get category by composite key"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM product_category WHERE category_id = ? AND subcategory_id = ?",
                (category_id, subcategory_id)
            )
            result = cursor.fetchone()
            if not result:
                raise CRUDException("Category not found", 404)
            return dict(result)
    
    @staticmethod
    def get_all_categories() -> List[dict]:
        """Get all categories"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM product_category")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update_category(category_id: int, subcategory_id: int, category: ProductCategoryUpdate) -> dict:
        """Update category"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if category exists
            cursor.execute(
                "SELECT * FROM product_category WHERE category_id = ? AND subcategory_id = ?",
                (category_id, subcategory_id)
            )
            if not cursor.fetchone():
                raise CRUDException("Category not found", 404)
            
            update_fields = []
            params = []
            
            if category.category_name is not None:
                # NEW: Check if new category name already exists (excluding current category)
                cursor.execute(
                    "SELECT * FROM product_category WHERE category_name = ? AND (category_id != ? OR subcategory_id != ?)",
                    (category.category_name, category_id, subcategory_id)
                )
                if cursor.fetchone():
                    raise CRUDException("Category name already exists. Please use a unique category name.", 400)
                
                update_fields.append("category_name = ?")
                params.append(category.category_name)
            if category.description is not None:
                update_fields.append("description = ?")
                params.append(category.description)
            
            if not update_fields:
                raise CRUDException("No fields to update", 400)
            
            params.extend([category_id, subcategory_id])
            query = f"UPDATE product_category SET {', '.join(update_fields)} WHERE category_id = ? AND subcategory_id = ?"
            
            cursor.execute(query, params)
            conn.commit()
            
            return {"message": "Category updated successfully"}
    
    @staticmethod
    def delete_category(category_id: int, subcategory_id: int) -> dict:
        """Delete category (will cascade to products)"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if category exists
            cursor.execute(
                "SELECT * FROM product_category WHERE category_id = ? AND subcategory_id = ?",
                (category_id, subcategory_id)
            )
            if not cursor.fetchone():
                raise CRUDException("Category not found", 404)
            
            cursor.execute(
                "DELETE FROM product_category WHERE category_id = ? AND subcategory_id = ?",
                (category_id, subcategory_id)
            )
            conn.commit()
            
            return {"message": "Category deleted successfully"}

class ProductCRUD:
    @staticmethod
    def create_product(product: ProductCreate) -> dict:
        """Create a new product"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if category exists
            cursor.execute(
                "SELECT * FROM product_category WHERE category_id = ? AND subcategory_id = ?",
                (product.category_id, product.subcategory_id)
            )
            if not cursor.fetchone():
                raise CRUDException("Referenced category not found", 400)
            
            # NEW: Check if product name already exists
            cursor.execute(
                "SELECT * FROM product WHERE product_name = ?",
                (product.product_name,)
            )
            if cursor.fetchone():
                raise CRUDException("Product name already exists. Please use a unique product name.", 400)

            cursor.execute(
                "INSERT INTO product (category_id, subcategory_id, product_name, price, stock_quantity) VALUES (?, ?, ?, ?, ?)",
                (product.category_id, product.subcategory_id, product.product_name, float(product.price), product.stock_quantity)
            )
            conn.commit()
            
            product_id = cursor.lastrowid
            return {**product.dict(), "product_id": product_id, "message": "Product created successfully"}
    
    @staticmethod
    def get_product(product_id: int) -> dict:
        """Get product by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM product WHERE product_id = ?", (product_id,))
            result = cursor.fetchone()
            if not result:
                raise CRUDException("Product not found", 404)
            return dict(result)
    
    @staticmethod
    def get_products_by_category(category_id: int, subcategory_id: int) -> List[dict]:
        """Get all products for a category"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM product WHERE category_id = ? AND subcategory_id = ?",
                (category_id, subcategory_id)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_all_products() -> List[dict]:
        """Get all products"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, pc.category_name 
                FROM product p 
                JOIN product_category pc ON p.category_id = pc.category_id AND p.subcategory_id = pc.subcategory_id
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update_product(product_id: int, product: ProductUpdate) -> dict:
        """Update product"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if product exists
            cursor.execute("SELECT * FROM product WHERE product_id = ?", (product_id,))
            if not cursor.fetchone():
                raise CRUDException("Product not found", 404)
            
            update_fields = []
            params = []
            
            if product.product_name is not None:
                # NEW: Check if new product name already exists (excluding current product)
                cursor.execute(
                    "SELECT * FROM product WHERE product_name = ? AND product_id != ?",
                    (product.product_name, product_id)
                )
                if cursor.fetchone():
                    raise CRUDException("Product name already exists. Please use a unique product name.", 400)
                update_fields.append("product_name = ?")
                params.append(product.product_name)
            if product.price is not None:
                update_fields.append("price = ?")
                params.append(float(product.price))
            if product.stock_quantity is not None:
                update_fields.append("stock_quantity = ?")
                params.append(product.stock_quantity)
            
            if not update_fields:
                raise CRUDException("No fields to update", 400)
            
            params.append(product_id)
            query = f"UPDATE product SET {', '.join(update_fields)} WHERE product_id = ?"
            
            cursor.execute(query, params)
            conn.commit()
            
            return {"message": "Product updated successfully"}
    
    @staticmethod
    def delete_product(product_id: int) -> dict:
        """Delete product"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if product exists
            cursor.execute("SELECT * FROM product WHERE product_id = ?", (product_id,))
            if not cursor.fetchone():
                raise CRUDException("Product not found", 404)
            
            cursor.execute("DELETE FROM product WHERE product_id = ?", (product_id,))
            conn.commit()
            
            return {"message": "Product deleted successfully"}