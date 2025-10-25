from typing import Dict, Any, List, Optional
from database import get_db_connection
import sqlite3
import logging

logger = logging.getLogger(__name__)

class AICRUDTools:
    """Tools for AI agent to perform CRUD operations"""
    
    @staticmethod
    def safe_float(value: Any) -> float:
        """Safely convert value to float, return 0.0 if invalid"""
        try:
            if value is None:
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def safe_int(value: Any) -> int:
        """Safely convert value to int, return 0 if invalid"""
        try:
            if value is None:
                return 0
            return int(value)
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def search_products(query: str, category_filter: Optional[str] = None) -> List[Dict]:
        """Search products with natural language understanding"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                base_query = """
                    SELECT p.*, pc.category_name 
                    FROM product p 
                    JOIN product_category pc ON p.category_id = pc.category_id AND p.subcategory_id = pc.subcategory_id
                    WHERE 1=1
                """
                params = []
                
                # Simple keyword-based search
                if query:
                    base_query += " AND (p.product_name LIKE ? OR p.product_name LIKE ? OR pc.category_name LIKE ?)"
                    params.extend([f'%{query}%', f'%{query.title()}%', f'%{query}%'])
                
                if category_filter:
                    base_query += " AND pc.category_name LIKE ?"
                    params.append(f'%{category_filter}%')
                
                base_query += " ORDER BY p.product_name"
                
                logger.info(f"Executing search query: {base_query} with params: {params}")
                cursor.execute(base_query, params)
                results = cursor.fetchall()
                
                products = []
                for row in results:
                    product_dict = dict(row)
                    # Convert price to float for JSON serialization
                    if 'price' in product_dict:
                        product_dict['price'] = AICRUDTools.safe_float(product_dict['price'])
                    # Ensure stock_quantity is int
                    if 'stock_quantity' in product_dict:
                        product_dict['stock_quantity'] = AICRUDTools.safe_int(product_dict['stock_quantity'])
                    products.append(product_dict)
                
                logger.info(f"Found {len(products)} products matching search")
                return products
                
        except Exception as e:
            logger.error(f"Error in search_products: {e}")
            return []
    
    @staticmethod
    def get_low_stock_products(threshold: int = 10) -> List[Dict]:
        """Get products with low stock"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.*, pc.category_name 
                    FROM product p 
                    JOIN product_category pc ON p.category_id = pc.category_id AND p.subcategory_id = pc.subcategory_id
                    WHERE p.stock_quantity < ?
                    ORDER BY p.stock_quantity ASC
                """, (threshold,))
                
                results = cursor.fetchall()
                products = []
                for row in results:
                    product_dict = dict(row)
                    # Safe conversion of numeric fields
                    if 'price' in product_dict:
                        product_dict['price'] = AICRUDTools.safe_float(product_dict['price'])
                    if 'stock_quantity' in product_dict:
                        product_dict['stock_quantity'] = AICRUDTools.safe_int(product_dict['stock_quantity'])
                    products.append(product_dict)
                
                logger.info(f"Found {len(products)} low stock products")
                return products
                
        except Exception as e:
            logger.error(f"Error in get_low_stock_products: {e}")
            return []
    
    @staticmethod
    def get_sales_trends() -> Dict[str, Any]:
        """Get basic sales trends and statistics"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Product count by category
                cursor.execute("""
                    SELECT 
                        pc.category_name, 
                        COUNT(p.product_id) as product_count,
                        AVG(p.price) as avg_price, 
                        SUM(p.stock_quantity) as total_stock,
                        MIN(p.stock_quantity) as min_stock,
                        MAX(p.stock_quantity) as max_stock
                    FROM product p 
                    JOIN product_category pc ON p.category_id = pc.category_id AND p.subcategory_id = pc.subcategory_id
                    GROUP BY pc.category_name
                    ORDER BY product_count DESC
                """)
                category_stats = []
                for row in cursor.fetchall():
                    stat_dict = dict(row)
                    # Safe conversion of numeric fields
                    if 'avg_price' in stat_dict:
                        stat_dict['avg_price'] = AICRUDTools.safe_float(stat_dict['avg_price'])
                    if 'total_stock' in stat_dict:
                        stat_dict['total_stock'] = AICRUDTools.safe_int(stat_dict['total_stock'])
                    if 'min_stock' in stat_dict:
                        stat_dict['min_stock'] = AICRUDTools.safe_int(stat_dict['min_stock'])
                    if 'max_stock' in stat_dict:
                        stat_dict['max_stock'] = AICRUDTools.safe_int(stat_dict['max_stock'])
                    if 'product_count' in stat_dict:
                        stat_dict['product_count'] = AICRUDTools.safe_int(stat_dict['product_count'])
                    category_stats.append(stat_dict)
                
                # Total statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_products,
                        AVG(price) as overall_avg_price,
                        SUM(stock_quantity) as total_inventory,
                        SUM(CASE WHEN stock_quantity < 10 THEN 1 ELSE 0 END) as low_stock_count
                    FROM product
                """)
                total_stats_row = cursor.fetchone()
                total_stats = {}
                if total_stats_row:
                    total_stats = dict(total_stats_row)
                    # Safe conversion
                    if 'overall_avg_price' in total_stats:
                        total_stats['overall_avg_price'] = AICRUDTools.safe_float(total_stats['overall_avg_price'])
                    if 'total_inventory' in total_stats:
                        total_stats['total_inventory'] = AICRUDTools.safe_int(total_stats['total_inventory'])
                    if 'low_stock_count' in total_stats:
                        total_stats['low_stock_count'] = AICRUDTools.safe_int(total_stats['low_stock_count'])
                    if 'total_products' in total_stats:
                        total_stats['total_products'] = AICRUDTools.safe_int(total_stats['total_products'])
                
                # Price range analysis
                cursor.execute("""
                    SELECT 
                        MIN(price) as min_price,
                        MAX(price) as max_price
                    FROM product
                """)
                price_stats_row = cursor.fetchone()
                price_stats = {}
                if price_stats_row:
                    price_stats = dict(price_stats_row)
                    if 'min_price' in price_stats:
                        price_stats['min_price'] = AICRUDTools.safe_float(price_stats['min_price'])
                    if 'max_price' in price_stats:
                        price_stats['max_price'] = AICRUDTools.safe_float(price_stats['max_price'])
                
                # Calculate low stock count safely
                low_stock_count = total_stats.get('low_stock_count', 0)
                if not isinstance(low_stock_count, int):
                    low_stock_count = 0
                
                health_score = "healthy" if low_stock_count < 5 else "needs_attention"
                
                return {
                    "category_statistics": category_stats,
                    "total_statistics": total_stats,
                    "price_statistics": price_stats,
                    "total_products": total_stats.get('total_products', 0),
                    "low_stock_alerts": low_stock_count,
                    "total_inventory_value": "N/A",
                    "health_score": health_score
                }
                
        except Exception as e:
            logger.error(f"Error in get_sales_trends: {e}")
            return {
                "category_statistics": [],
                "total_statistics": {},
                "price_statistics": {},
                "total_products": 0,
                "low_stock_alerts": 0,
                "health_score": "error",
                "error": str(e)
            }
    
    @staticmethod
    def create_product_suggestion(product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest product creation with validation"""
        try:
            logger.info(f"Creating product suggestion with data: {product_data}")
            
            # Validate required fields
            required_fields = ['product_name', 'category_id', 'subcategory_id', 'price', 'stock_quantity']
            missing_fields = [field for field in required_fields if field not in product_data or product_data[field] is None]
            
            if missing_fields:
                return {
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}",
                    "suggested_fields": required_fields,
                    "provided_data": product_data
                }
            
            # Validate data types
            validation_errors = []
            
            if not isinstance(product_data['product_name'], str) or len(product_data['product_name'].strip()) == 0:
                validation_errors.append("product_name must be a non-empty string")
            
            if not isinstance(product_data['category_id'], int) or product_data['category_id'] <= 0:
                validation_errors.append("category_id must be a positive integer")
            
            if not isinstance(product_data['subcategory_id'], int) or product_data['subcategory_id'] <= 0:
                validation_errors.append("subcategory_id must be a positive integer")
            
            try:
                price = float(product_data['price'])
                if price <= 0:
                    validation_errors.append("price must be positive")
            except (ValueError, TypeError):
                validation_errors.append("price must be a valid number")
            
            if not isinstance(product_data['stock_quantity'], int) or product_data['stock_quantity'] < 0:
                validation_errors.append("stock_quantity must be a non-negative integer")
            
            if validation_errors:
                return {
                    "status": "error",
                    "message": "Validation errors: " + "; ".join(validation_errors),
                    "validation_errors": validation_errors
                }
            
            # Check if category exists
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT category_name FROM product_category WHERE category_id = ? AND subcategory_id = ?",
                    (product_data['category_id'], product_data['subcategory_id'])
                )
                category = cursor.fetchone()
                
                if not category:
                    # Get available categories for suggestion
                    cursor.execute("SELECT DISTINCT category_id, subcategory_id, category_name FROM product_category LIMIT 10")
                    available_categories = [dict(row) for row in cursor.fetchall()]
                    
                    return {
                        "status": "error",
                        "message": f"Category not found: ID {product_data['category_id']}-{product_data['subcategory_id']}",
                        "suggestion": "Check available categories first",
                        "available_categories": available_categories
                    }
            
            # All validations passed
            return {
                "status": "success",
                "message": "Product data is valid and ready for creation",
                "suggested_action": "create_product",
                "validated_data": {
                    "product_name": product_data['product_name'].strip(),
                    "category_id": product_data['category_id'],
                    "subcategory_id": product_data['subcategory_id'],
                    "price": float(product_data['price']),
                    "stock_quantity": product_data['stock_quantity']
                },
                "category_info": dict(category) if category else None
            }
            
        except Exception as e:
            logger.error(f"Error in create_product_suggestion: {e}")
            return {
                "status": "error", 
                "message": f"Error validating product data: {str(e)}"
            }
    
    @staticmethod
    def analyze_user_behavior() -> Dict[str, Any]:
        """Analyze user patterns and behavior"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # User role distribution
                cursor.execute("""
                    SELECT 
                        r.role_name, 
                        COUNT(u.id) as user_count,
                        SUM(CASE WHEN u.is_active = TRUE THEN 1 ELSE 0 END) as active_users
                    FROM users u 
                    JOIN roles r ON u.role_id = r.role_id
                    GROUP BY r.role_name
                    ORDER BY user_count DESC
                """)
                role_distribution = []
                for row in cursor.fetchall():
                    role_dict = dict(row)
                    # Safe conversion
                    if 'user_count' in role_dict:
                        role_dict['user_count'] = AICRUDTools.safe_int(role_dict['user_count'])
                    if 'active_users' in role_dict:
                        role_dict['active_users'] = AICRUDTools.safe_int(role_dict['active_users'])
                    role_distribution.append(role_dict)
                
                # User activity analysis
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_users,
                        SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) as active_users_count,
                        SUM(CASE WHEN is_active = FALSE THEN 1 ELSE 0 END) as inactive_users_count,
                        MIN(created_at) as first_user_date,
                        MAX(created_at) as latest_user_date
                    FROM users
                """)
                user_activity_row = cursor.fetchone()
                user_activity = {}
                if user_activity_row:
                    user_activity = dict(user_activity_row)
                    # Safe conversion
                    for key in ['total_users', 'active_users_count', 'inactive_users_count']:
                        if key in user_activity:
                            user_activity[key] = AICRUDTools.safe_int(user_activity[key])
                
                # Recent user registrations
                cursor.execute("""
                    SELECT 
                        username, 
                        email, 
                        role_id,
                        created_at
                    FROM users 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                recent_users = [dict(row) for row in cursor.fetchall()]
                
                # Calculate totals safely
                total_active_users = user_activity.get('active_users_count', 0)
                total_inactive_users = user_activity.get('inactive_users_count', 0)
                
                admin_count = next((AICRUDTools.safe_int(role['user_count']) for role in role_distribution if role.get('role_name') == 'admin'), 0)
                manager_count = next((AICRUDTools.safe_int(role['user_count']) for role in role_distribution if role.get('role_name') == 'manager'), 0)
                user_count = next((AICRUDTools.safe_int(role['user_count']) for role in role_distribution if role.get('role_name') == 'user'), 0)
                
                return {
                    "user_analytics": {
                        "role_distribution": role_distribution,
                        "activity_summary": user_activity,
                        "recent_registrations": recent_users,
                        "total_active_users": total_active_users,
                        "total_inactive_users": total_inactive_users,
                        "admin_count": admin_count,
                        "manager_count": manager_count,
                        "user_count": user_count
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in analyze_user_behavior: {e}")
            return {
                "user_analytics": {
                    "role_distribution": [],
                    "activity_summary": {},
                    "recent_registrations": [],
                    "total_active_users": 0,
                    "total_inactive_users": 0,
                    "admin_count": 0,
                    "manager_count": 0,
                    "user_count": 0,
                    "error": str(e)
                }
            }
    
    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Basic counts with safe conversion
                cursor.execute("SELECT COUNT(*) as count FROM product_category")
                category_count = AICRUDTools.safe_int(cursor.fetchone()[0])
                
                cursor.execute("SELECT COUNT(*) as count FROM product")
                product_count = AICRUDTools.safe_int(cursor.fetchone()[0])
                
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = TRUE")
                user_count = AICRUDTools.safe_int(cursor.fetchone()[0])
                
                cursor.execute("SELECT COUNT(*) as count FROM roles")
                role_count = AICRUDTools.safe_int(cursor.fetchone()[0])
                
                # Low stock analysis
                low_stock_products = AICRUDTools.get_low_stock_products()
                low_stock_count = len(low_stock_products) if low_stock_products else 0
                
                # Database health check
                cursor.execute("PRAGMA integrity_check")
                db_health_result = cursor.fetchone()
                db_health = db_health_result[0] if db_health_result else "unknown"
                
                # Table sizes
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                table_sizes = {}
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    table_sizes[table] = AICRUDTools.safe_int(cursor.fetchone()[0])
                
                # Calculate health score
                health_indicators = {
                    'categories': category_count > 0,
                    'products': product_count > 0,
                    'users': user_count > 0,
                    'low_stock': low_stock_count < 10,
                    'database': db_health == 'ok'
                }
                
                health_score = sum(health_indicators.values()) / len(health_indicators) * 100
                
                health_status = "excellent" if health_score >= 80 else "good" if health_score >= 60 else "needs_attention"
                
                return {
                    "system_metrics": {
                        "categories": category_count,
                        "products": product_count,
                        "active_users": user_count,
                        "roles": role_count,
                        "low_stock_alerts": low_stock_count,
                        "database_health": db_health,
                        "table_sizes": table_sizes,
                        "health_score": round(health_score, 1),
                        "health_status": health_status
                    },
                    "health_indicators": health_indicators
                }
                
        except Exception as e:
            logger.error(f"Error in get_system_health: {e}")
            return {
                "system_metrics": {
                    "categories": 0,
                    "products": 0,
                    "active_users": 0,
                    "roles": 0,
                    "low_stock_alerts": 0,
                    "database_health": "unknown",
                    "health_score": 0,
                    "health_status": "error",
                    "error": str(e)
                }
            }
    
    @staticmethod
    def get_category_insights() -> Dict[str, Any]:
        """Get insights about product categories"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Categories with most products
                cursor.execute("""
                    SELECT 
                        pc.category_id,
                        pc.subcategory_id,
                        pc.category_name,
                        COUNT(p.product_id) as product_count,
                        AVG(p.price) as avg_price,
                        SUM(p.stock_quantity) as total_stock
                    FROM product_category pc
                    LEFT JOIN product p ON pc.category_id = p.category_id AND pc.subcategory_id = p.subcategory_id
                    GROUP BY pc.category_id, pc.subcategory_id, pc.category_name
                    ORDER BY product_count DESC
                """)
                category_insights = []
                for row in cursor.fetchall():
                    insight = dict(row)
                    # Safe conversion
                    if 'avg_price' in insight:
                        insight['avg_price'] = AICRUDTools.safe_float(insight['avg_price'])
                    if 'total_stock' in insight:
                        insight['total_stock'] = AICRUDTools.safe_int(insight['total_stock'])
                    if 'product_count' in insight:
                        insight['product_count'] = AICRUDTools.safe_int(insight['product_count'])
                    category_insights.append(insight)
                
                # Categories with low stock
                cursor.execute("""
                    SELECT 
                        pc.category_name,
                        COUNT(p.product_id) as low_stock_count
                    FROM product_category pc
                    JOIN product p ON pc.category_id = p.category_id AND pc.subcategory_id = p.subcategory_id
                    WHERE p.stock_quantity < 10
                    GROUP BY pc.category_name
                    ORDER BY low_stock_count DESC
                """)
                low_stock_categories = []
                for row in cursor.fetchall():
                    category_dict = dict(row)
                    if 'low_stock_count' in category_dict:
                        category_dict['low_stock_count'] = AICRUDTools.safe_int(category_dict['low_stock_count'])
                    low_stock_categories.append(category_dict)
                
                # Calculate statistics safely
                total_categories = len(category_insights)
                categories_with_products = len([c for c in category_insights if AICRUDTools.safe_int(c.get('product_count', 0)) > 0])
                empty_categories = len([c for c in category_insights if AICRUDTools.safe_int(c.get('product_count', 0)) == 0])
                
                return {
                    "category_insights": category_insights,
                    "low_stock_categories": low_stock_categories,
                    "total_categories": total_categories,
                    "categories_with_products": categories_with_products,
                    "empty_categories": empty_categories
                }
                
        except Exception as e:
            logger.error(f"Error in get_category_insights: {e}")
            return {
                "category_insights": [],
                "low_stock_categories": [],
                "total_categories": 0,
                "categories_with_products": 0,
                "empty_categories": 0,
                "error": str(e)
            }