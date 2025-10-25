from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from crud import ProductCategoryCRUD, ProductCRUD
from models import ProductCategoryCreate, ProductCategoryUpdate, ProductCreate, ProductUpdate, UserCreate, UserLogin, UserResponse
from auth import AuthHandler
from user_crud import UserCRUD
from schemas import CRUDException
from ai_agent import ai_agent
from agent_tools import AICRUDTools
import uvicorn
import logging
from typing import  List
from enhanced_agent import enhanced_ai_agent
from enhanced_streamlit import show_enhanced_ai_interface


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    init_db()
    UserCRUD.init_users_table()
    logger.info("Application started successfully!")
    yield
    # Shutdown
    logger.info("Application shutting down...")

app = FastAPI(
    title="Master-Detail CRUD API with AI Agent", 
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
auth_handler = AuthHandler()

# Role-based dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = auth_handler.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = UserCRUD.get_user_by_username(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role_name"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def require_manager_or_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role_name"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Manager or admin access required")
    return current_user

async def require_user(current_user: dict = Depends(get_current_user)):
    return current_user

# Exception handler
@app.exception_handler(CRUDException)
async def crud_exception_handler(request, exc: CRUDException):
    logger.error(f"CRUDException: {exc.message}")
    raise HTTPException(status_code=exc.status_code, detail=exc.message)

# Auth Routes
@app.post("/register", summary="Register new user")
async def register(user: UserCreate):
    user_data = user.dict()
    if user_data.get('role_id', 3) != 3:
        user_data['role_id'] = 3
    return UserCRUD.create_user(**user_data)

@app.post("/login", summary="Login and get JWT token")
async def login(user_data: UserLogin):
    user = UserCRUD.authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = auth_handler.create_access_token(
        data={"sub": user["username"], "role": user["role_name"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role_name"]
        }
    }

@app.get("/verify-token", summary="Verify JWT token")
async def verify_token_endpoint(payload: dict = Depends(get_current_user)):
    return {"valid": True, "user": payload}

# NEW: AI Agent Endpoints
@app.post("/ai/query", summary="Query AI Agent")
async def query_ai_agent(
    query_data: dict, 
    current_user: dict = Depends(require_user)
):
    """Natural language query interface with AI agent"""
    try:
        user_input = query_data.get("query", "")
        if not user_input:
            raise HTTPException(status_code=400, detail="Query is required")
        
        result = ai_agent.process_query(
            user_input=user_input,
            user_role=current_user["role_name"]
        )
        
        return {
            "response": result["response"],
            "data": result.get("data", {}),
            "action_taken": result.get("action_taken", ""),
            "needs_human_review": result.get("needs_human_review", False)
        }
        
    except Exception as e:
        logger.error(f"AI query error: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

@app.get("/ai/analytics/low-stock", summary="Get Low Stock Analytics")
async def get_low_stock_analytics(current_user: dict = Depends(require_user)):
    """Get AI-powered low stock analysis"""
    low_stock_products = AICRUDTools.get_low_stock_products()
    
    # Use AI to generate insights
    insight_prompt = f"""
    Analyze these low stock products and provide business recommendations:
    {[f"{p['product_name']} (Stock: {p['stock_quantity']})" for p in low_stock_products]}
    
    Provide:
    1. Priority products to restock
    2. Potential revenue impact
    3. Recommended actions
    """
    
    ai_insights = ai_agent.process_query(
        user_input=insight_prompt,
        user_role=current_user["role_name"]
    )
    
    return {
        "low_stock_products": low_stock_products,
        "ai_insights": ai_insights["response"],
        "total_low_stock": len(low_stock_products)
    }

@app.get("/ai/analytics/system-health", summary="Get System Health with AI Insights")
async def get_system_health_ai(current_user: dict = Depends(require_user)):
    """Get system health with AI-powered insights"""
    system_health = AICRUDTools.get_system_health()
    user_analytics = AICRUDTools.analyze_user_behavior()
    
    # Generate AI insights
    insight_prompt = f"""
    Analyze this system health data and provide recommendations:
    System Metrics: {system_health}
    User Analytics: {user_analytics}
    
    Provide insights on:
    1. System performance and potential issues
    2. User engagement and role distribution
    3. Recommendations for improvement
    """
    
    ai_insights = ai_agent.process_query(
        user_input=insight_prompt,
        user_role=current_user["role_name"]
    )
    
    return {
        "system_health": system_health,
        "user_analytics": user_analytics,
        "ai_insights": ai_insights["response"]
    }

@app.get("/ai/analytics/sales-trends", summary="Get Sales Trends with AI Analysis")
async def get_sales_trends_ai(current_user: dict = Depends(require_user)):
    """Get sales trends with AI-powered analysis"""
    sales_trends = AICRUDTools.get_sales_trends()
    
    insight_prompt = f"""
    Analyze these sales trends and provide business insights:
    {sales_trends}
    
    Provide:
    1. Key performance indicators
    2. Category performance analysis
    3. Growth opportunities
    """
    
    ai_insights = ai_agent.process_query(
        user_input=insight_prompt,
        user_role=current_user["role_name"]
    )
    
    return {
        "sales_trends": sales_trends,
        "ai_insights": ai_insights["response"]
    }

# User Management Routes (Admin only)
@app.get("/admin/users", summary="Get all users", dependencies=[Depends(require_admin)])
async def get_all_users():
    return UserCRUD.get_all_users()

@app.post("/admin/users", summary="Create new user with role", dependencies=[Depends(require_admin)])
async def create_user_with_role(user: UserCreate):
    return UserCRUD.create_user(user.username, user.email, user.password, user.full_name, user.role_id)

@app.put("/admin/users/{username}/role", summary="Update user role", dependencies=[Depends(require_admin)])
async def update_user_role(username: str, role_update: dict):
    role_id = role_update.get("role_id")
    if not role_id:
        raise HTTPException(status_code=400, detail="role_id is required")
    
    return UserCRUD.update_user_role(username, role_id, "admin")

@app.delete("/admin/users/{username}", summary="Delete user", dependencies=[Depends(require_admin)])
async def delete_user(username: str):
    return UserCRUD.delete_user(username, "admin")

# Protected Routes with Role-Based Access

# Product Category Routes
@app.post("/categories/", summary="Create product category", dependencies=[Depends(require_manager_or_admin)])
async def create_category(category: ProductCategoryCreate):
    return ProductCategoryCRUD.create_category(category)

@app.get("/categories/{category_id}/{subcategory_id}", summary="Get category by composite key", dependencies=[Depends(require_user)])
async def get_category(category_id: int, subcategory_id: int):
    return ProductCategoryCRUD.get_category(category_id, subcategory_id)

@app.get("/categories/", summary="Get all categories", dependencies=[Depends(require_user)])
async def get_all_categories():
    return ProductCategoryCRUD.get_all_categories()

@app.put("/categories/{category_id}/{subcategory_id}", summary="Update category", dependencies=[Depends(require_manager_or_admin)])
async def update_category(category_id: int, subcategory_id: int, category: ProductCategoryUpdate):
    return ProductCategoryCRUD.update_category(category_id, subcategory_id, category)

@app.delete("/categories/{category_id}/{subcategory_id}", summary="Delete category", dependencies=[Depends(require_manager_or_admin)])
async def delete_category(category_id: int, subcategory_id: int):
    return ProductCategoryCRUD.delete_category(category_id, subcategory_id)

# Product Routes
@app.post("/products/", summary="Create product", dependencies=[Depends(require_manager_or_admin)])
async def create_product(product: ProductCreate):
    return ProductCRUD.create_product(product)

@app.get("/products/{product_id}", summary="Get product by ID", dependencies=[Depends(require_user)])
async def get_product(product_id: int):
    return ProductCRUD.get_product(product_id)

@app.get("/products/", summary="Get all products", dependencies=[Depends(require_user)])
async def get_all_products():
    return ProductCRUD.get_all_products()

@app.get("/products/category/{category_id}/{subcategory_id}", summary="Get products by category", dependencies=[Depends(require_user)])
async def get_products_by_category(category_id: int, subcategory_id: int):
    return ProductCRUD.get_products_by_category(category_id, subcategory_id)

@app.put("/products/{product_id}", summary="Update product", dependencies=[Depends(require_manager_or_admin)])
async def update_product(product_id: int, product: ProductUpdate):
    return ProductCRUD.update_product(product_id, product)

@app.delete("/products/{product_id}", summary="Delete product", dependencies=[Depends(require_manager_or_admin)])
async def delete_product(product_id: int):
    return ProductCRUD.delete_product(product_id)

# Public routes
@app.get("/")
async def root():
    return {"message": "AI-Powered Master-Detail CRUD API is running", "status": "healthy"}

@app.get("/roles")
async def get_roles():
    """Get available roles"""
    return {
        "roles": [
            {"id": 1, "name": "admin", "description": "Full system access"},
            {"id": 2, "name": "manager", "description": "Manage products and categories"},
            {"id": 3, "name": "user", "description": "Read-only access"}
        ]
    }

@app.get("/ai/status")
async def ai_status():
    """Check AI agent status"""
    try:
        # Test Ollama connection directly
        import ollama
        client = ollama.Client()
        
        try:
            models_response = client.list()
            
            # Handle different response formats
            if isinstance(models_response, dict) and 'models' in models_response:
                models = models_response['models']
            elif isinstance(models_response, list):
                models = models_response
            else:
                models = []
            
            model_names = []
            for model in models:
                if isinstance(model, dict):
                    model_names.append(model.get('name', 'unknown'))
                else:
                    model_names.append(str(model))
            
            agent_ready = ai_agent.is_available()
            current_model = ai_agent.model if hasattr(ai_agent, 'model') else "none"
            
            return {
                "status": "active" if agent_ready else "inactive",
                "model": current_model,
                "available_models": model_names,
                "agent_ready": agent_ready,
                "ollama_connected": True,
                "message": "AI status check completed"
            }
            
        except Exception as e:
            return {
                "status": "inactive",
                "error": str(e),
                "agent_ready": False,
                "ollama_connected": False,
                "message": "Ollama connection error"
            }
            
    except Exception as e:
        return {
            "status": "inactive", 
            "error": str(e), 
            "agent_ready": False,
            "ollama_connected": False,
            "message": "Ollama not installed or not running"
        }

@app.post("/ai/enhanced-query", summary="Enhanced AI Agent Query")
async def enhanced_ai_query(
    query_data: dict, 
    current_user: dict = Depends(require_user)
):
    """Enhanced natural language query with multi-agent system"""
    try:
        user_input = query_data.get("query", "")
        response_style = query_data.get("response_style", "Conversational")
        
        if not user_input:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Use enhanced agent with supervisor pattern
        result = enhanced_ai_agent.supervisor_agent(
            query=user_input,
            user_role=current_user["role_name"],
            conversation_history=[]  # You can add conversation memory here
        )
        
        # Enhance response based on style
        enhanced_response = apply_response_style(result["response"], response_style)
        
        return {
            "response": enhanced_response,
            "agent_type": result.get("type", "supervisor"),
            "data": result.get("data", {}),
            "reasoning": result.get("reasoning", ""),
            "actions": extract_actions_from_response(enhanced_response),
            "needs_human_review": result.get("needs_human_review", False)
        }
        
    except Exception as e:
        logger.error(f"Enhanced AI query error: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

def apply_response_style(response: str, style: str) -> str:
    """Apply different response styles to the AI output"""
    if style == "Formal":
        return f"**Formal Analysis:**\n\n{response}"
    elif style == "Technical":
        return f"**Technical Assessment:**\n\n{response}"
    elif style == "Storytelling":
        return f"**Narrative Insights:**\n\n{response}"
    else:  # Conversational
        return response

def extract_actions_from_response(response: str) -> List[str]:
    """Extract actionable items from the AI response"""
    actions = []
    lines = response.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith(('-', '•', '1.', '2.', '3.', '4.', '5.')):
            # Clean up the action item
            action = line.lstrip('-•12345. ').strip()
            if action and len(action) > 10:  # Meaningful actions only
                actions.append(action)
    
    return actions[:5]  # Return top 5 actions




if __name__ == "__main__":
    logger.info("Starting AI-Powered FastAPI server on http://0.0.0.0:8000")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info",
        timeout_keep_alive=300,  # 5 minutes
        timeout_graceful_shutdown=300,  # 5 minutes
    )