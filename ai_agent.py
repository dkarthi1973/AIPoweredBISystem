import logging
import time
import json
from typing import Dict, Any, List, Optional
from agent_tools import AICRUDTools

logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self, model: str = "llama3.1:latest"):
        self.model = model
        self.available = False
        self.client = None
        
        try:
            logger.info("🚀 Initializing AI Agent...")
            import ollama
            self.client = ollama.Client()
            
            # Test the connection
            self.test_ollama_connection()
            
        except ImportError:
            logger.error("❌ Ollama package not installed. Run: pip install ollama")
            self.available = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama client: {e}")
            self.available = False

    def test_ollama_connection(self):
        """Test connection to Ollama with proper model name extraction"""
        try:
            # Get model list
            models_response = self.client.list()
            logger.info(f"📋 Raw models response type: {type(models_response)}")
            
            # Handle ListResponse object
            models = []
            if hasattr(models_response, 'models'):
                models = models_response.models
                logger.info(f"📋 Using models from .models attribute, count: {len(models)}")
            elif isinstance(models_response, list):
                models = models_response
                logger.info(f"📋 Using models as plain list, count: {len(models)}")
            elif isinstance(models_response, dict) and 'models' in models_response:
                models = models_response['models']
                logger.info(f"📋 Using models from dict key, count: {len(models)}")
            else:
                logger.warning(f"⚠️ Unexpected models response format: {type(models_response)}")
                models = []
            
            logger.info(f"📋 Final models count: {len(models)}")
            
            # Extract model names from the models list - CRITICAL FIX HERE
            available_models = []
            for i, model in enumerate(models):
                try:
                    model_name = None
                    
                    # Method 1: Check for model attribute (most common)
                    if hasattr(model, 'model') and model.model:
                        model_name = model.model
                        logger.info(f"  ✅ Model {i} name from .model: {model_name}")
                    
                    # Method 2: Check for name attribute
                    elif hasattr(model, 'name') and model.name:
                        model_name = model.name
                        logger.info(f"  ✅ Model {i} name from .name: {model_name}")
                    
                    # Method 3: If it's a dict, get from 'model' or 'name' key
                    elif isinstance(model, dict):
                        model_name = model.get('model') or model.get('name')
                        if model_name:
                            logger.info(f"  ✅ Model {i} name from dict: {model_name}")
                    
                    # Method 4: Last resort - string representation
                    if not model_name:
                        model_str = str(model)
                        # Try to extract model name from string representation
                        if "model='" in model_str:
                            import re
                            match = re.search(r"model='([^']*)'", model_str)
                            if match:
                                model_name = match.group(1)
                                logger.info(f"  ✅ Model {i} name extracted from string: {model_name}")
                        else:
                            model_name = model_str.split()[0] if model_str else f"unknown_{i}"
                            logger.info(f"  ⚠️ Model {i} name from string fallback: {model_name}")
                    
                    if model_name:
                        available_models.append(model_name)
                    else:
                        logger.warning(f"  ❌ Could not extract model name for model {i}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing model {i}: {e}")
                    continue
            
            logger.info(f"📋 Available model names: {available_models}")
            
            if not available_models:
                logger.error("❌ No models could be extracted from the response")
                self.available = False
                return
            
            # Check if our target model exists
            target_model_found = False
            actual_model_name = None
            
            for model_name in available_models:
                # Clean the model name - remove any extra quotes or spaces
                clean_model_name = model_name.strip().strip("'\"")
                
                # Check for exact match or contains (case insensitive)
                if (self.model.lower() == clean_model_name.lower() or 
                    self.model.lower() in clean_model_name.lower()):
                    target_model_found = True
                    actual_model_name = clean_model_name
                    logger.info(f"✅ Found matching model: '{clean_model_name}' for target '{self.model}'")
                    break
            
            if target_model_found and actual_model_name:
                self.model = actual_model_name
                logger.info(f"🎯 Final model to use: '{self.model}'")
                self.available = True
                
                # Test the model with a simple generation
                self.test_model_generation()
                
            else:
                logger.warning(f"⚠️ Target model '{self.model}' not found in available models")
                logger.info(f"📋 Available models: {available_models}")
                
                # Try to use any available model
                if available_models:
                    self.model = available_models[0].strip().strip("'\"")
                    logger.info(f"🔄 Using first available model: '{self.model}'")
                    self.available = True
                    self.test_model_generation()
                else:
                    logger.error("❌ No models available in Ollama")
                    self.available = False
                        
        except Exception as e:
            logger.error(f"❌ Error testing Ollama connection: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            self.available = False

    def test_model_generation(self):
        """Test if the selected model can generate responses"""
        try:
            logger.info(f"🧪 Testing model generation with: '{self.model}'")
            
            # Ensure we're using a clean model name
            clean_model = self.model.strip().strip("'\"")
            logger.info(f"🧪 Using clean model name: '{clean_model}'")
            
            test_response = self.client.generate(
                model=clean_model,
                prompt="Hello, please respond with 'AI Agent is working' to confirm everything is working.",
                stream=False,
                options={'timeout': 60000}  # 1 minute timeout for test
            )
            
            if test_response and 'response' in test_response:
                response_text = test_response['response'].strip()
                logger.info(f"✅ Model test successful! Response: '{response_text}'")
                self.available = True
            else:
                logger.warning("⚠️ Model test: Empty response received")
                self.available = False
                
        except Exception as e:
            logger.error(f"❌ Model generation test failed: {e}")
            self.available = False

    def is_available(self):
        return self.available

    def safe_generate(self, prompt: str, max_retries: int = 2) -> str:
        """Generate response with comprehensive error handling"""
        if not self.available or not self.client:
            return "AI service is currently unavailable. Please check if Ollama is running."
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🤖 Generating response (attempt {attempt + 1}) with model: '{self.model}'")
                
                # Use clean model name
                clean_model = self.model.strip().strip("'\"")
                
                response = self.client.generate(
                    model=clean_model,
                    prompt=prompt,
                    stream=False,
                    options={
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'timeout': 300000  # 5 minutes
                    }
                )
                
                if response and 'response' in response:
                    return response['response']
                else:
                    logger.warning(f"⚠️ Empty response from model on attempt {attempt + 1}")
                    
            except Exception as e:
                logger.error(f"❌ Generation error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"💥 All generation attempts failed")
        
        return "I apologize, but I'm having trouble generating a response right now. Please try again later or check the Ollama service."

    def process_query(self, user_input: str, user_role: str = "user") -> Dict[str, Any]:
        """Process user queries with the AI agent"""
        if not self.available:
            return self.get_unavailable_response()
        
        try:
            # Enhanced prompt for better responses
            prompt = f"""
            You are a helpful AI assistant for a business inventory management system.
            
            User Role: {user_role}
            User Query: {user_input}
            
            Available data and functions:
            - Product inventory and categories
            - Sales trends and analytics
            - User management (if admin/manager)
            - System health monitoring
            
            Please provide a helpful, concise response. If the user is asking about data you can't access,
            suggest what they can do with their current permissions.
            
            Response:
            """
            
            response_text = self.safe_generate(prompt)
            
            # Get relevant data based on query type
            data = self.get_relevant_data(user_input, user_role)
            
            return {
                "response": response_text,
                "data": data,
                "reasoning": "Processed using direct LLM call",
                "action_taken": "llm_generation",
                "needs_human_review": False
            }
            
        except Exception as e:
            logger.error(f"💥 Error processing query: {e}")
            return {
                "response": "I encountered an error while processing your request. Please try again.",
                "data": {},
                "reasoning": f"Processing error: {str(e)}",
                "action_taken": "error",
                "needs_human_review": True
            }

    def get_relevant_data(self, user_input: str, user_role: str) -> Dict[str, Any]:
        """Get relevant data based on user query"""
        user_input_lower = user_input.lower()
        data = {}
        
        try:
            # Product-related queries
            if any(keyword in user_input_lower for keyword in ['product', 'inventory', 'stock']):
                if 'low' in user_input_lower or 'out of stock' in user_input_lower:
                    data['low_stock'] = AICRUDTools.get_low_stock_products()
                else:
                    data['products'] = AICRUDTools.search_products(user_input)
            
            # Category-related queries
            elif any(keyword in user_input_lower for keyword in ['category', 'categories']):
                data['categories'] = AICRUDTools.get_category_insights()
            
            # Analytics queries
            elif any(keyword in user_input_lower for keyword in ['analytics', 'trend', 'report', 'statistics']):
                data['trends'] = AICRUDTools.get_sales_trends()
                data['system_health'] = AICRUDTools.get_system_health()
            
            # User-related queries (only for admin/manager)
            elif any(keyword in user_input_lower for keyword in ['user', 'users']) and user_role in ['admin', 'manager']:
                data['user_analytics'] = AICRUDTools.analyze_user_behavior()
            
            # System health queries
            elif any(keyword in user_input_lower for keyword in ['health', 'status', 'system']):
                data['system_health'] = AICRUDTools.get_system_health()
                
        except Exception as e:
            logger.error(f"Error getting relevant data: {e}")
            data['error'] = str(e)
        
        return data

    def get_unavailable_response(self) -> Dict[str, Any]:
        """Get response when AI service is unavailable"""
        return {
            "response": "🔧 AI Assistant is currently unavailable.\n\nPlease ensure:\n1. Ollama is running: `ollama serve`\n2. Models are available: `ollama list`\n3. Restart the application\n\nIf issues persist, check the server logs for detailed error information.",
            "data": {},
            "reasoning": "AI service not available",
            "action_taken": "unavailable",
            "needs_human_review": True
        }

# Create agent instance with comprehensive error handling
try:
    logger.info("🚀 Initializing AI Agent...")
    ai_agent = AIAgent(model="llama3.1:latest")
    
    if ai_agent.is_available():
        logger.info("✅ AI Agent initialized successfully!")
        logger.info(f"📋 Using model: '{ai_agent.model}'")
    else:
        logger.warning("⚠️ AI Agent initialized but not available")
        logger.warning("💡 Please check Ollama installation and model availability")
        
except Exception as e:
    logger.error(f"💥 Failed to initialize AI Agent: {e}")
    import traceback
    logger.error(f"💥 Traceback: {traceback.format_exc()}")
    
    # Create fallback agent
    class FallbackAgent:
        def __init__(self):
            self.available = False
            self.model = "none"
        
        def is_available(self):
            return False
            
        def process_query(self, user_input, user_role="user"):
            return {
                "response": "🔧 AI Assistant is currently unavailable. Please check:\n1. Ollama service is running\n2. Models are available via `ollama list`\n3. Restart the application",
                "data": {},
                "reasoning": "Fallback agent - initialization failed",
                "action_taken": "fallback",
                "needs_human_review": True
            }
    
    ai_agent = FallbackAgent()
