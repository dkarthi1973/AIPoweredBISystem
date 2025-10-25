import streamlit as st
import requests
import pandas as pd
from decimal import Decimal
import time
import json
from admin_panel import show_admin_panel
from enhanced_streamlit import show_enhanced_ai_interface
from help_page import show_help_page
from typing import  List

# API base URL
API_BASE = "http://localhost:8000"

st.set_page_config(page_title="AI-Powered CRUD App", layout="wide")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Login"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def login_user(username: str, password: str):
    """Login user and get JWT token"""
    try:
        with st.spinner("Logging in..."):
            response = requests.post(
                f"{API_BASE}/login", 
                json={"username": username, "password": password},
                timeout=300  # Increased to 5 minutes
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.token = data["access_token"]
                st.session_state.user = data["user"]
                st.session_state.current_tab = "🤖 AI Assistant"
                st.session_state.chat_history = []
                st.success(f"Welcome {data['user']['username']}!")
                time.sleep(1)
                st.rerun()
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                st.error(f"Login failed: {error_detail}")
                
    except Exception as e:
        st.error(f"Login error: {e}")

def logout_user():
    """Logout user and clear session"""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.current_tab = "Login"
    st.session_state.chat_history = []
    st.rerun()

def register_user(username: str, email: str, password: str, full_name: str):
    """Register new user"""
    try:
        response = requests.post(
            f"{API_BASE}/register", 
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name
            },
            timeout=300  # Increased to 5 minutes
        )
        if response.status_code == 200:
            st.success("Registration successful! Please login.")
            st.session_state.current_tab = "Login"
            st.rerun()
        else:
            st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"Connection error: {e}")

def make_authenticated_request(method, endpoint, **kwargs):
    """Make authenticated API request with 5-minute timeout"""
    if not st.session_state.token:
        st.error("Not authenticated")
        return None
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    if 'headers' in kwargs:
        kwargs['headers'].update(headers)
    else:
        kwargs['headers'] = headers
    
    # Set default timeout to 300 seconds (5 minutes) for all requests
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 300
    
    try:
        response = method(f"{API_BASE}{endpoint}", **kwargs)
        if response.status_code == 401:
            st.error("Session expired. Please login again.")
            logout_user()
            return None
        return response
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out after 5 minutes. The server is taking longer than expected to respond.")
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def query_ai_agent(user_input: str):
    """Send query to AI agent with 5-minute timeout"""
    try:
        response = make_authenticated_request(
            requests.post, 
            "/ai/query",
            json={"query": user_input},
            timeout=300  # 5 minutes for AI queries
        )
        
        if response and response.status_code == 200:
            return response.json()
        else:
            return {"response": "Sorry, I couldn't process your request. The request may have timed out.", "data": {}}
    except requests.exceptions.Timeout:
        return {"response": "Request timed out after 5 minutes. The AI is taking longer than expected to respond.", "data": {}}
    except Exception as e:
        return {"response": f"Error: {str(e)}", "data": {}}

# NEW: AI Chat Interface Component
def show_ai_assistant():
    """AI Assistant chat interface"""
    st.header("🤖 AI Assistant")
    
    # Check AI status with increased timeout
    try:
        status_response = requests.get(f"{API_BASE}/ai/status", timeout=300)  # 5 minutes
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "active":
                st.success("✅ AI Agent is active and ready")
                st.info(f"Using model: {status_data.get('model', 'Unknown')}")
                st.success("⏱️ 5-minute timeouts configured for all operations")
            else:
                st.warning("⚠️ AI Agent is currently unavailable")
                if status_data.get('error'):
                    st.error(f"Error: {status_data.get('error')}")
        else:
            st.error("❌ Cannot connect to AI service")
    except requests.exceptions.Timeout:
        st.warning("⏱️ AI status check timed out after 5 minutes.")
    except:
        st.error("❌ Cannot check AI service status")
    
    # Chat container
    chat_container = st.container()
    with chat_container:
        # Display chat history
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                with st.chat_message("user"):
                    st.write(chat["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(chat["content"])
                    
                    # Show data if available
                    if chat.get("data"):
                        with st.expander("📊 View Detailed Data"):
                            if isinstance(chat["data"], dict) and any(chat["data"].values()):
                                st.json(chat["data"])
                            else:
                                st.info("No additional data available")
    
    # Chat input
    user_input = st.chat_input("Ask me anything about your data...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        with st.spinner("🤔 Thinking... (this may take several minutes)"):
            ai_response = query_ai_agent(user_input)
            
            # Add AI response to history
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": ai_response.get("response", "No response"),
                "data": ai_response.get("data", {})
            })
        
        st.rerun()
    
    # Quick action buttons
    st.subheader("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 System Health", use_container_width=True):
            with st.spinner("Analyzing system health... (may take several minutes)"):
                response = make_authenticated_request(requests.get, "/ai/analytics/system-health", timeout=300)
                if response and response.status_code == 200:
                    data = response.json()
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"**System Health Report:**\n{data['ai_insights']}",
                        "data": data
                    })
                    st.rerun()
    
    with col2:
        if st.button("📦 Low Stock", use_container_width=True):
            with st.spinner("Checking inventory... (may take several minutes)"):
                response = make_authenticated_request(requests.get, "/ai/analytics/low-stock", timeout=300)
                if response and response.status_code == 200:
                    data = response.json()
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"**Low Stock Analysis:**\n{data['ai_insights']}",
                        "data": data
                    })
                    st.rerun()
    
    with col3:
        if st.button("📈 Sales Trends", use_container_width=True):
            with st.spinner("Analyzing trends... (may take several minutes)"):
                response = make_authenticated_request(requests.get, "/ai/analytics/sales-trends", timeout=300)
                if response and response.status_code == 200:
                    data = response.json()
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"**Sales Trends Analysis:**\n{data['ai_insights']}",
                        "data": data
                    })
                    st.rerun()
    
    with col4:
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    # Example queries
    with st.expander("💡 Example Queries"):
        st.write("""
        Try asking:
        - "Show me products with low stock"
        - "What's our system health status?"
        - "Analyze sales trends by category"
        - "Help me create a new product"
        - "Which categories have the most products?"
        - "Give me user activity insights"
        
        ⚠️ Note: AI responses may take 2-5 minutes due to model processing.
        """)

# Login/Register UI
if not st.session_state.token:
    st.title("🔐 AI-Powered CRUD Application - Login")
    
    # Connection test
    with st.expander("🔧 Connection Test", expanded=True):
        try:
            health_response = requests.get(f"{API_BASE}/", timeout=300)  # 5 minutes
            if health_response.status_code == 200:
                st.success("✅ Backend server is running and accessible")
                
                # Check AI status
                try:
                    ai_status_response = requests.get(f"{API_BASE}/ai/status", timeout=300)  # 5 minutes
                    if ai_status_response.status_code == 200:
                        ai_status = ai_status_response.json()
                        if ai_status.get('agent_ready'):
                            st.success("✅ AI Agent is ready")
                        else:
                            st.warning("⚠️ AI Agent is not available")
                except requests.exceptions.Timeout:
                    st.warning("⏱️ AI status check timed out after 5 minutes")
                except:
                    st.warning("⚠️ Cannot check AI Agent status")
            else:
                st.error("❌ Backend server responded with error")
        except requests.exceptions.Timeout:
            st.error("❌ Backend server connection timed out after 5 minutes")
        except:
            st.error("❌ Cannot connect to backend server at http://localhost:8000")
            st.info("Please make sure:")
            st.info("1. FastAPI server is running with: `python main.py`")
            st.info("2. The server is accessible at http://localhost:8000")
            st.info("3. Ollama is installed and running with: `ollama pull llama3.1:latest`")
    
    # Tabs for Login and Register
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.header("Login to Application")
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_btn:
                if username and password:
                    login_user(username, password)
                else:
                    st.error("Please enter both username and password")
        
        # Quick login buttons
        st.subheader("Quick Test Logins")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Admin", use_container_width=True):
                login_user("admin", "admin123")
        with col2:
            if st.button("Manager", use_container_width=True):
                login_user("manager", "manager123")
        with col3:
            if st.button("User", use_container_width=True):
                login_user("user1", "password123")
    
    with tab2:
        st.header("Create New Account")
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("👤 Username", key="reg_username")
                new_email = st.text_input("📧 Email", key="reg_email")
            with col2:
                new_full_name = st.text_input("👤 Full Name", key="reg_fullname")
                new_password = st.text_input("🔒 Password", type="password", key="reg_password")
            
            register_btn = st.form_submit_button("📝 Register", use_container_width=True)
            
            if register_btn:
                if new_username and new_email and new_password:
                    register_user(new_username, new_email, new_password, new_full_name)
                else:
                    st.error("Please fill all required fields")
    
    # Sample credentials
    with st.expander("📋 Sample Credentials"):
        st.write("""
        **Pre-registered users:**
        
        | Username | Password | Role | Permissions |
        |----------|----------|------|-------------|
        | `admin` | `admin123` | Admin | Full access + User management + AI |
        | `manager` | `manager123` | Manager | Manage products & categories + AI |
        | `user1` | `password123` | User | Read-only access + AI queries |
        """)
    
    st.stop()

# Main Application (Authenticated)
user_role = st.session_state.user.get('role', 'user')
st.title(f"🏠 AI-Powered CRUD Application - Welcome {st.session_state.user['username']}!")

# Sidebar with user info and navigation
st.sidebar.title("🧭 Navigation")
st.sidebar.success(f"✅ Logged in as: **{st.session_state.user['username']}**")
st.sidebar.info(f"📧 Email: {st.session_state.user['email']}")
st.sidebar.info(f"🎯 Role: **{user_role.capitalize()}**")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    logout_user()

st.sidebar.markdown("---")

# Enhanced navigation with AI Assistant
if user_role == "admin":
    nav_options = ["🤖 AI Assistant", "📁 Categories", "📦 Products", "👥 User Management", "📊 Analytics", "🆘 Help"]
elif user_role == "manager":
    nav_options = ["🤖 AI Assistant", "📁 Categories", "📦 Products", "📊 Analytics", "🆘 Help"]
else:  # user
    nav_options = ["🤖 AI Assistant", "📁 Categories", "📦 Products", "🆘 Help"]



tab = st.sidebar.radio("Go to", nav_options)

# AI Assistant Tab
if tab == "🤖 AI Assistant":
    show_enhanced_ai_interface()

# Analytics Tab (for admin/manager)
elif tab == "📊 Analytics" and user_role in ["admin", "manager"]:
    st.header("📊 Advanced Analytics")
    
    st.warning("⚠️ Analytics operations may take 2-5 minutes due to AI processing. Please be patient.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Full System Report", use_container_width=True):
            with st.spinner("Generating comprehensive report... (this may take 5 minutes)"):
                # System health
                health_response = make_authenticated_request(requests.get, "/ai/analytics/system-health", timeout=300)
                # Low stock
                stock_response = make_authenticated_request(requests.get, "/ai/analytics/low-stock", timeout=300)
                # Sales trends
                sales_response = make_authenticated_request(requests.get, "/ai/analytics/sales-trends", timeout=300)
                
                if health_response and stock_response and sales_response:
                    health_data = health_response.json()
                    stock_data = stock_response.json()
                    sales_data = sales_response.json()
                    
                    # Display in tabs
                    tab1, tab2, tab3 = st.tabs(["System Health", "Inventory", "Sales"])
                    
                    with tab1:
                        st.subheader("System Health Metrics")
                        st.json(health_data['system_health'])
                        
                        st.subheader("User Analytics")
                        st.json(health_data['user_analytics'])
                        
                        st.subheader("AI Insights")
                        st.info(health_data['ai_insights'])
                    
                    with tab2:
                        st.subheader("Low Stock Products")
                        if stock_data['low_stock_products']:
                            df_stock = pd.DataFrame(stock_data['low_stock_products'])
                            st.dataframe(df_stock, use_container_width=True)
                            
                            st.metric("Total Low Stock Items", len(stock_data['low_stock_products']))
                        else:
                            st.success("No low stock items!")
                        
                        st.subheader("AI Recommendations")
                        st.info(stock_data['ai_insights'])
                    
                    with tab3:
                        st.subheader("Sales Trends")
                        st.json(sales_data['sales_trends'])
                        
                        st.subheader("Category Performance")
                        if sales_data['sales_trends'].get('category_statistics'):
                            df_categories = pd.DataFrame(sales_data['sales_trends']['category_statistics'])
                            st.dataframe(df_categories, use_container_width=True)
                        
                        st.subheader("AI Analysis")
                        st.info(sales_data['ai_insights'])
                else:
                    st.error("Failed to generate full report. Some services timed out after 5 minutes.")
    
    with col2:
        if st.button("👥 User Analytics", use_container_width=True):
            with st.spinner("Analyzing user patterns... (may take 2-5 minutes)"):
                response = make_authenticated_request(requests.get, "/ai/analytics/system-health", timeout=300)
                if response:
                    data = response.json()
                    user_analytics = data['user_analytics']
                    
                    st.subheader("User Distribution by Role")
                    if user_analytics['user_analytics']['role_distribution']:
                        user_df = pd.DataFrame(user_analytics['user_analytics']['role_distribution'])
                        st.dataframe(user_df, use_container_width=True)
                        
                        # Display metrics
                        total_users = user_analytics['user_analytics']['total_active_users']
                        admin_count = next((role['user_count'] for role in user_analytics['user_analytics']['role_distribution'] if role['role_name'] == 'admin'), 0)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total Active Users", total_users)
                        with col2:
                            st.metric("Admin Users", admin_count)
    
    with col3:
        if st.button("📈 Performance Dashboard", use_container_width=True):
            with st.spinner("Loading performance data... (may take 2-5 minutes)"):
                health_response = make_authenticated_request(requests.get, "/ai/analytics/system-health", timeout=300)
                if health_response:
                    data = health_response.json()
                    system_health = data['system_health']['system_metrics']
                    
                    # Display key metrics
                    st.subheader("Key Performance Indicators")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Categories", system_health['categories'])
                    with col2:
                        st.metric("Total Products", system_health['products'])
                    with col3:
                        st.metric("Active Users", system_health['active_users'])
                    with col4:
                        st.metric("Low Stock Alerts", system_health['low_stock_alerts'])
                    
                    # Health status
                    health_status = system_health['health_status']
                    health_score = system_health.get('health_score', 0)
                    
                    if health_status == "healthy" or health_score >= 80:
                        st.success(f"✅ System Health: {health_status} ({health_score}%)")
                    elif health_status == "good" or health_score >= 60:
                        st.warning(f"⚠️ System Health: {health_status} ({health_score}%)")
                    else:
                        st.error(f"❌ System Health: {health_status} ({health_score}%)")

# Categories Management
elif tab == "📁 Categories":
    st.header("📁 Product Categories Management")
    
    # Show/hide create based on role
    if user_role in ["admin", "manager"]:
        with st.expander("➕ Create New Category", expanded=False):
            with st.form("create_category"):
                col1, col2 = st.columns(2)
                with col1:
                    cat_id = st.number_input("Category ID", min_value=1, step=1, key="cat_id")
                    cat_name = st.text_input("Category Name*", key="cat_name", 
                               help="Must be unique across all categories")
                with col2:
                    subcat_id = st.number_input("Subcategory ID", min_value=1, step=1, key="subcat_id")
                    description = st.text_area("Description", key="cat_desc")
                
                if st.form_submit_button("✅ Create Category", use_container_width=True):
                    if not cat_name.strip():
                        st.error("Category name is required")
                    else:
                        with st.spinner("Creating category..."):
                            try:
                                response = make_authenticated_request(
                                    requests.post, "/categories/", 
                                    json={
                                        "category_id": cat_id,
                                        "subcategory_id": subcat_id,
                                        "category_name": cat_name.strip(),
                                        "description": description
                                    },
                                    timeout=300
                                )
                                if response and response.status_code == 200:
                                    st.success("✅ Category created successfully!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    error_detail = response.json().get('detail', 'Unknown error') if response else 'No response'
                                    st.error(f"❌ Failed to create category: {error_detail}")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
    else:
        st.info("ℹ️ You have read-only access to categories. Contact an admin or manager for modifications.")
    
    # Display Categories (all roles can view)
    st.subheader("📋 Existing Categories")
    with st.spinner("Loading categories... (may take a few minutes)"):
        response = make_authenticated_request(requests.get, "/categories/", timeout=300)  # 5 minutes
    if response and response.status_code == 200:
        categories = response.json()
        if categories:
            df_categories = pd.DataFrame(categories)
            st.dataframe(df_categories, use_container_width=True)
            
            # Update/Delete Category (only for admin/manager)
            if user_role in ["admin", "manager"]:
                st.subheader("🛠️ Update/Delete Category")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("✏️ Update Category")
                    with st.form("update_category"):
                        update_cat_id = st.number_input("Category ID to update", min_value=1, step=1, key="update_cat_id")
                        update_subcat_id = st.number_input("Subcategory ID to update", min_value=1, step=1, key="update_subcat_id")
                        new_cat_name = st.text_input("New Category Name", key="new_cat_name")
                        new_description = st.text_area("New Description", key="new_desc")
                        
                        if st.form_submit_button("🔄 Update Category", use_container_width=True):
                            update_data = {}
                            if new_cat_name:
                                update_data["category_name"] = new_cat_name
                            if new_description:
                                update_data["description"] = new_description
                            
                            if update_data:
                                with st.spinner("Updating category... (may take a few minutes)"):
                                    response = make_authenticated_request(
                                        requests.put, f"/categories/{update_cat_id}/{update_subcat_id}",
                                        json=update_data,
                                        timeout=300  # 5 minutes
                                    )
                                    if response and response.status_code == 200:
                                        st.success("✅ Category updated successfully!")
                                        time.sleep(1)
                                        st.rerun()
                
                with col2:
                    st.write("🗑️ Delete Category")
                    with st.form("delete_category"):
                        del_cat_id = st.number_input("Category ID to delete", min_value=1, step=1, key="del_cat_id")
                        del_subcat_id = st.number_input("Subcategory ID to delete", min_value=1, step=1, key="del_subcat_id")
                        
                        if st.form_submit_button("❌ Delete Category", use_container_width=True):
                            with st.spinner("Deleting category... (may take a few minutes)"):
                                response = make_authenticated_request(
                                    requests.delete, f"/categories/{del_cat_id}/{del_subcat_id}",
                                    timeout=300  # 5 minutes
                                )
                                if response and response.status_code == 200:
                                    st.success("✅ Category deleted successfully!")
                                    time.sleep(1)
                                    st.rerun()
        else:
            st.info("ℹ️ No categories found.")

# Products Management
elif tab == "📦 Products":
    st.header("📦 Products Management")
    
    # Show/hide create based on role
    if user_role in ["admin", "manager"]:
        with st.expander("➕ Create New Product", expanded=False):
            with st.form("create_product"):
                col1, col2 = st.columns(2)
                with col1:
                    prod_cat_id = st.number_input("Category ID", min_value=1, step=1, key="prod_cat_id")
                    prod_subcat_id = st.number_input("Subcategory ID", min_value=1, step=1, key="prod_subcat_id")
                    product_name = st.text_input("Product Name*", key="product_name",
                                   help="Must be unique across all products")
                with col2:
                    price = st.number_input("Price", min_value=0.01, step=0.01, format="%.2f", key="price")
                    stock_quantity = st.number_input("Stock Quantity", min_value=0, step=1, key="stock_quantity")
                
                if st.form_submit_button("✅ Create Product", use_container_width=True):
                    if not product_name.strip():
                        st.error("Product name is required")
                    else:
                        with st.spinner("Creating product..."):
                            try:
                                response = make_authenticated_request(
                                    requests.post, "/products/", 
                                    json={
                                        "category_id": prod_cat_id,
                                        "subcategory_id": prod_subcat_id,
                                        "product_name": product_name.strip(),
                                        "price": float(price),
                                        "stock_quantity": stock_quantity
                                    },
                                    timeout=300
                                )
                                if response and response.status_code == 200:
                                    st.success("✅ Product created successfully!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    error_detail = response.json().get('detail', 'Unknown error') if response else 'No response'
                                    st.error(f"❌ Failed to create product: {error_detail}")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
    else:
        st.info("ℹ️ You have read-only access to products. Contact an admin or manager for modifications.")
    
    # Display Products (all roles can view)
    st.subheader("📋 Existing Products")
    with st.spinner("Loading products... (may take a few minutes)"):
        response = make_authenticated_request(requests.get, "/products/", timeout=300)  # 5 minutes
    if response and response.status_code == 200:
        products = response.json()
        if products:
            df_products = pd.DataFrame(products)
            st.dataframe(df_products, use_container_width=True)
            
            # Update/Delete Product (only for admin/manager)
            if user_role in ["admin", "manager"]:
                st.subheader("🛠️ Update/Delete Product")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("✏️ Update Product")
                    with st.form("update_product"):
                        update_prod_id = st.number_input("Product ID to update", min_value=1, step=1, key="update_prod_id")
                        new_product_name = st.text_input("New Product Name", key="new_product_name")
                        new_price = st.number_input("New Price", min_value=0.01, step=0.01, format="%.2f", key="new_price")
                        new_stock = st.number_input("New Stock Quantity", min_value=0, step=1, key="new_stock")
                        
                        if st.form_submit_button("🔄 Update Product", use_container_width=True):
                            update_data = {}
                            if new_product_name:
                                update_data["product_name"] = new_product_name
                            if new_price > 0:
                                update_data["price"] = float(new_price)
                            if new_stock >= 0:
                                update_data["stock_quantity"] = new_stock
                            
                            if update_data:
                                with st.spinner("Updating product... (may take a few minutes)"):
                                    response = make_authenticated_request(
                                        requests.put, f"/products/{update_prod_id}",
                                        json=update_data,
                                        timeout=300  # 5 minutes
                                    )
                                    if response and response.status_code == 200:
                                        st.success("✅ Product updated successfully!")
                                        time.sleep(1)
                                        st.rerun()
                
                with col2:
                    st.write("🗑️ Delete Product")
                    with st.form("delete_product"):
                        del_prod_id = st.number_input("Product ID to delete", min_value=1, step=1, key="del_prod_id")
                        
                        if st.form_submit_button("❌ Delete Product", use_container_width=True):
                            with st.spinner("Deleting product... (may take a few minutes)"):
                                response = make_authenticated_request(
                                    requests.delete, f"/products/{del_prod_id}",
                                    timeout=300  # 5 minutes
                                )
                                if response and response.status_code == 200:
                                    st.success("✅ Product deleted successfully!")
                                    time.sleep(1)
                                    st.rerun()
        else:
            st.info("ℹ️ No products found.")

# User Management (Admin only)
elif tab == "👥 User Management":
    if user_role == "admin":
        show_admin_panel(API_BASE, st.session_state.token)
    else:
        st.error("🚫 Access Denied: You need admin privileges to access user management.")

elif tab == "🆘 Help":
    show_help_page()


# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"""
**Enhanced Tech Stack:**
- Python 3.13.3 + FastAPI
- Streamlit UI
- Ollama + Llama 3.1
- LangGraph Agentic AI
- JWT Auth + RBAC
- SQLite Database

**⚠️ Performance Note:**
- All operations have 5-minute timeouts
- AI processing may be slow
- Please be patient with responses
""")