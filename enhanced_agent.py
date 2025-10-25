import logging
import time
import json
from typing import Dict, Any, List, Optional
from enum import Enum
from agent_tools import AICRUDTools
import pandas as pd
from datetime import datetime, timedelta
from typing import  List

logger = logging.getLogger(__name__)

class AgentType(Enum):
    REACT_AGENT = "react"
    PLANNER = "planner"
    SUPERVISOR = "supervisor"
    ANALYTICS_AGENT = "analytics"
    RAG_AGENT = "rag"
    CRAG_AGENT = "crag"

class EnhancedAIAgent:
    def __init__(self, model: str = "llama3.1:latest"):
        self.model = model
        self.available = False
        self.client = None
        
        try:
            import ollama
            self.client = ollama.Client()
            self.available = self.test_connection()
            logger.info(f"✅ Enhanced AI Agent initialized: {self.available}")
        except Exception as e:
            logger.error(f"❌ Enhanced Agent initialization failed: {e}")
            self.available = False

    def test_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            # Get available models
            models_response = self.client.list()
            models = []
            
            # Handle different response formats
            if hasattr(models_response, 'models'):
                models = models_response.models
            elif isinstance(models_response, dict) and 'models' in models_response:
                models = models_response['models']
            elif isinstance(models_response, list):
                models = models_response
            
            # Extract model names
            available_models = []
            for model in models:
                if hasattr(model, 'model') and model.model:
                    available_models.append(model.model)
                elif hasattr(model, 'name') and model.name:
                    available_models.append(model.name)
                elif isinstance(model, dict):
                    available_models.append(model.get('model') or model.get('name', 'unknown'))
            
            # Use first available model
            if available_models:
                self.model = available_models[0]
                logger.info(f"✅ Enhanced Agent using model: {self.model}")
                
                # Test generation
                response = self.client.generate(
                    model=self.model,
                    prompt="Test connection",
                    stream=False
                )
                return bool(response and 'response' in response)
            return False
            
        except Exception as e:
            logger.error(f"❌ Enhanced Agent connection test failed: {e}")
            return False

    def safe_generate(self, prompt: str) -> str:
        """Safe LLM generation"""
        if not self.available or not self.client:
            return "AI service is currently unavailable."
        
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={'timeout': 300000}
            )
            return response.get('response', 'No response generated')
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            return f"Error generating response: {str(e)}"

    def supervisor_agent(self, query: str, user_role: str, conversation_history: List = None) -> Dict:
        """Orchestrates agent team based on query complexity with REAL data"""
        try:
            # Get comprehensive real data first
            real_data = self.get_comprehensive_business_data(query)
            
            # Analyze query to determine which agent to use
            agent_type = self.analyze_query_type(query)
            
            # Generate response using REAL data
            prompt = self.create_data_rich_prompt(query, user_role, agent_type, real_data)
            response = self.safe_generate(prompt)
            
            return {
                "response": response,
                "type": agent_type,
                "data": real_data,
                "reasoning": f"Used {agent_type} approach with comprehensive business data",
                "needs_human_review": False
            }
        except Exception as e:
            logger.error(f"❌ Supervisor agent error: {e}")
            return {
                "response": f"Error processing request: {str(e)}",
                "type": "error",
                "data": {},
                "reasoning": f"Error: {str(e)}",
                "needs_human_review": True
            }

    def get_comprehensive_business_data(self, query: str) -> Dict[str, Any]:
        """Get comprehensive real business data based on query context"""
        data = {}
        query_lower = query.lower()
        
        try:
            logger.info("🔄 Collecting comprehensive business data...")
            
            # ALWAYS get system health and user analytics for context
            data['system_health'] = AICRUDTools.get_system_health()
            data['user_analytics'] = AICRUDTools.analyze_user_behavior()
            data['sales_trends'] = AICRUDTools.get_sales_trends()
            data['category_insights'] = AICRUDTools.get_category_insights()
            
            # Product and inventory data - always include for business context
            data['products'] = AICRUDTools.search_products("")
            data['low_stock'] = AICRUDTools.get_low_stock_products()
            
            # Enhanced data based on query focus
            if any(term in query_lower for term in ['product', 'inventory', 'stock', 'item']):
                # Already included above
                pass
            
            if any(term in query_lower for term in ['user', 'team', 'employee', 'staff', 'performance', 'role']):
                # user_analytics already included above
                pass
                
            if any(term in query_lower for term in ['category', 'classification', 'group']):
                # category_insights already included above
                pass
            
            # Add data summaries for easier processing
            data['summary'] = self.create_data_summary(data)
            data['query_context'] = self.analyze_query_context(query_lower)
            
            logger.info(f"✅ Collected data with {len(data.get('products', []))} products, {len(data.get('low_stock', []))} low stock items")
            
        except Exception as e:
            logger.error(f"❌ Error getting business data: {e}")
            data['error'] = str(e)
            data['summary'] = {'error': str(e)}
        
        return data

    def create_data_summary(self, data: Dict) -> Dict[str, Any]:
        """Create meaningful summaries from the data"""
        summary = {}
        
        try:
            # System health summary
            if 'system_health' in data and data['system_health']:
                sys_health = data['system_health'].get('system_metrics', {})
                summary['system_status'] = sys_health.get('health_status', 'Unknown')
                summary['total_products'] = sys_health.get('products', 0)
                summary['total_categories'] = sys_health.get('categories', 0)
                summary['active_users'] = sys_health.get('active_users', 0)
                summary['low_stock_alerts'] = sys_health.get('low_stock_alerts', 0)
                summary['health_score'] = sys_health.get('health_score', 0)

            # User analytics summary
            if 'user_analytics' in data and data['user_analytics']:
                user_analytics = data['user_analytics'].get('user_analytics', {})
                summary['total_users'] = user_analytics.get('total_active_users', 0)
                summary['role_distribution'] = user_analytics.get('role_distribution', [])
                
                # Extract role counts
                role_counts = {}
                for role in user_analytics.get('role_distribution', []):
                    role_name = role.get('role_name', 'unknown')
                    role_count = role.get('user_count', 0)
                    role_counts[role_name] = role_count
                summary['role_counts'] = role_counts

            # Products summary
            if 'products' in data and data['products']:
                products = data['products']
                summary['total_products_count'] = len(products)
                
                # Calculate price statistics
                prices = [float(p.get('price', 0)) for p in products if p.get('price') is not None]
                if prices:
                    summary['avg_product_price'] = sum(prices) / len(prices)
                    summary['max_product_price'] = max(prices)
                    summary['min_product_price'] = min(prices)
                
                # Calculate stock statistics
                stock_levels = [p.get('stock_quantity', 0) for p in products]
                summary['total_stock_quantity'] = sum(stock_levels)
                summary['avg_stock_level'] = sum(stock_levels) / len(stock_levels) if stock_levels else 0
                
                # Calculate inventory value
                total_value = sum([float(p.get('price', 0)) * p.get('stock_quantity', 0) for p in products])
                summary['total_inventory_value'] = total_value

            # Low stock summary
            if 'low_stock' in data and data['low_stock']:
                low_stock = data['low_stock']
                summary['low_stock_count'] = len(low_stock)
                low_stock_products = [p.get('product_name', 'Unknown') for p in low_stock[:5]]
                summary['critical_products'] = low_stock_products
                
                # Low stock value
                low_stock_value = sum([float(p.get('price', 0)) * p.get('stock_quantity', 0) for p in low_stock])
                summary['low_stock_value'] = low_stock_value

            # Sales trends summary
            if 'sales_trends' in data and data['sales_trends']:
                trends = data['sales_trends']
                summary['total_products_trends'] = trends.get('total_products', 0)
                summary['low_stock_alerts_trends'] = trends.get('low_stock_alerts', 0)
                summary['health_score_trends'] = trends.get('health_score', 'Unknown')
                
                # Category statistics
                if 'category_statistics' in trends:
                    category_stats = trends['category_statistics']
                    summary['top_categories'] = [cat.get('category_name', 'Unknown') for cat in category_stats[:3]]
                    summary['category_count'] = len(category_stats)

            # Category insights summary
            if 'category_insights' in data and data['category_insights']:
                insights = data['category_insights']
                summary['total_categories_insights'] = insights.get('total_categories', 0)
                summary['categories_with_products'] = insights.get('categories_with_products', 0)
                summary['empty_categories'] = insights.get('empty_categories', 0)
                
        except Exception as e:
            logger.error(f"❌ Error creating data summary: {e}")
            summary['error'] = str(e)
        
        return summary

    def analyze_query_context(self, query_lower: str) -> Dict[str, Any]:
        """Analyze query context for better data targeting"""
        context = {
            'is_financial': any(term in query_lower for term in ['financial', 'revenue', 'cost', 'profit', 'money', 'price', 'budget']),
            'is_inventory': any(term in query_lower for term in ['inventory', 'stock', 'product', 'item', 'quantity']),
            'is_user_related': any(term in query_lower for term in ['user', 'team', 'employee', 'staff', 'role', 'performance']),
            'is_system_related': any(term in query_lower for term in ['system', 'health', 'performance', 'database', 'technical']),
            'is_strategic': any(term in query_lower for term in ['strategy', 'plan', 'roadmap', 'future', 'growth']),
            'is_analytical': any(term in query_lower for term in ['analyze', 'analysis', 'trend', 'pattern', 'insight']),
        }
        return context

    def analyze_query_type(self, query: str) -> str:
        """Analyze query to determine appropriate agent type"""
        query_lower = query.lower()
        
        # Planning queries
        if any(word in query_lower for word in ['plan', 'strategy', 'roadmap', 'timeline', 'schedule', 'develop']):
            return "planner"
        
        # Analytical queries
        elif any(word in query_lower for word in ['analyze', 'analysis', 'trend', 'pattern', 'insight', 'metric', 'statistic']):
            return "analytics"
        
        # Data retrieval queries
        elif any(word in query_lower for word in ['show', 'list', 'get', 'find', 'retrieve', 'display', 'what']):
            return "rag"
        
        # Complex multi-faceted queries
        elif any(word in query_lower for word in ['comprehensive', 'complete', 'overview', 'assessment', 'report', 'review']):
            return "supervisor"
        
        # Problem-solving queries
        elif any(word in query_lower for word in ['why', 'how', 'solve', 'fix', 'improve', 'problem', 'issue', 'trouble']):
            return "react"
        
        # Validation queries
        elif any(word in query_lower for word in ['validate', 'verify', 'check', 'review', 'assess', 'correct', 'validate']):
            return "crag"
        
        # Default to supervisor for complex queries
        else:
            return "supervisor"

    def create_data_rich_prompt(self, query: str, user_role: str, agent_type: str, real_data: Dict) -> str:
        """Create enhanced prompt with REAL business data"""
        
        data_summary = real_data.get('summary', {})
        query_context = real_data.get('query_context', {})
        data_context = self.format_data_for_prompt(real_data)
        
        base_context = f"""
        REAL BUSINESS DATA CONTEXT:

        CURRENT BUSINESS STATE:
        - System Status: {data_summary.get('system_status', 'Unknown')} (Score: {data_summary.get('health_score', 'N/A')})
        - Total Products: {data_summary.get('total_products', 0)} across {data_summary.get('total_categories', 0)} categories
        - Active Users: {data_summary.get('active_users', 0)} out of {data_summary.get('total_users', 0)} total users
        - Inventory Value: ${data_summary.get('total_inventory_value', 0):.2f}
        - Low Stock Alerts: {data_summary.get('low_stock_alerts', 0)} items need attention

        INVENTORY DETAILS:
        - Products in System: {data_summary.get('total_products_count', 0)}
        - Average Price: ${data_summary.get('avg_product_price', 0):.2f}
        - Total Stock Quantity: {data_summary.get('total_stock_quantity', 0)}
        - Critical Low Stock: {data_summary.get('low_stock_count', 0)} products
        - Low Stock Value: ${data_summary.get('low_stock_value', 0):.2f}

        USER DISTRIBUTION:
        - Role Breakdown: {data_summary.get('role_counts', {})}
        - Active vs Total: {data_summary.get('active_users', 0)}/{data_summary.get('total_users', 0)}

        ADDITIONAL CONTEXT:
        {data_context}

        QUERY CONTEXT: {query_context}
        """
        
        agent_specific_prompts = {
            "react": f"""
            {base_context}
            
            USER QUERY: {query}
            USER ROLE: {user_role}
            AGENT TYPE: REACT (Reasoning + Acting)
            
            Use REACT framework with ACTUAL DATA:
            
            REASONING PHASE:
            1. Analyze the current business situation using the real data above
            2. Identify root causes based on specific metrics and patterns
            3. Consider the user's role and permissions in your analysis
            4. Use actual numbers from the business data to support your reasoning
            
            ACTION PHASE:
            1. Provide 3-5 specific, actionable recommendations
            2. Base each action on the actual business metrics
            3. Consider implementation feasibility given current resources
            4. Prioritize actions by impact and urgency
            5. Reference specific products, categories, or metrics where relevant
            
            Format your response with clear reasoning followed by actionable steps.
            Use actual numbers from the data to make your recommendations credible.
            """,
            
            "planner": f"""
            {base_context}
            
            USER QUERY: {query}
            USER ROLE: {user_role}
            AGENT TYPE: PLANNER (Strategic Planning)
            
            Create REALISTIC EXECUTION PLAN using actual business context:
            
            CURRENT STATE ASSESSMENT:
            - Summarize key metrics relevant to the planning objective
            - Identify strengths and weaknesses from the data
            - Consider resource constraints (users, products, system capacity)
            
            PLANNING FRAMEWORK:
            PHASE 1: Foundation (Weeks 1-2)
            - Specific deliverables based on current capabilities
            - Resource allocation using actual user roles
            - Success metrics tied to existing business metrics
            
            PHASE 2: Implementation (Weeks 3-6)  
            - Action steps with clear ownership
            - Timeline based on current workload
            - Risk mitigation using system health data
            
            PHASE 3: Optimization (Weeks 7-12)
            - Performance monitoring using existing metrics
            - Adjustment strategies
            - Long-term sustainability planning
            
            Ensure the plan is actionable with current resources and data.
            Reference specific numbers from the business context.
            """,
            
            "supervisor": f"""
            {base_context}
            
            USER QUERY: {query}
            USER ROLE: {user_role}
            AGENT TYPE: SUPERVISOR (Multi-Agent Coordination)
            
            Provide COMPREHENSIVE BUSINESS ANALYSIS by coordinating multiple perspectives:
            
            CROSS-FUNCTIONAL ANALYSIS:
            - Connect inventory data with user activity patterns
            - Relate system health to business performance
            - Analyze financial implications of operational metrics
            - Consider strategic impact of tactical findings
            
            INTEGRATED INSIGHTS:
            - Identify patterns across different data sources
            - Highlight dependencies between business functions
            - Provide holistic recommendations that consider multiple aspects
            - Balance short-term actions with long-term strategy
            
            EXECUTIVE SUMMARY:
            - Key findings from the comprehensive analysis
            - Priority recommendations across business functions
            - Impact assessment based on actual metrics
            - Implementation roadmap considering all constraints
            
            Create a unified view that connects different business aspects.
            Use actual numbers to support cross-functional insights.
            """,
            
            "rag": f"""
            {base_context}
            
            USER QUERY: {query}
            USER ROLE: {user_role}
            AGENT TYPE: RAG (Retrieval Augmented Generation)
            
            RETRIEVE AND PRESENT SPECIFIC BUSINESS DATA:
            
            DATA RETRIEVAL:
            - Extract the most relevant information from the business data
            - Focus on accuracy and completeness
            - Present data in a clear, organized manner
            - Include context for understanding the numbers
            
            INFORMATION PRESENTATION:
            - Use tables or lists for multiple data points
            - Highlight key findings and patterns
            - Provide comparisons where relevant
            - Include summary statistics
            
            CONTEXTUAL INSIGHTS:
            - Explain what the data means for the business
            - Connect data points to business objectives
            - Suggest follow-up questions or analyses
            - Note any data limitations or gaps
            
            Focus on factual accuracy and clear presentation of business information.
            """,
            
            "analytics": f"""
            {base_context}
            
            USER QUERY: {query}
            USER ROLE: {user_role}
            AGENT TYPE: ANALYTICS (Data Analysis & Insights)
            
            Provide DATA-DRIVEN ANALYTICAL INSIGHTS:
            
            QUANTITATIVE ANALYSIS:
            - Calculate percentages, ratios, and trends from the data
            - Identify statistical patterns and correlations
            - Perform comparative analysis across categories or time periods
            - Use mathematical models where appropriate
            
            TREND IDENTIFICATION:
            - Spot emerging patterns in the business data
            - Identify seasonal or cyclical variations
            - Highlight performance outliers
            - Project future trends based on historical data
            
            ACTIONABLE INSIGHTS:
            - Translate data patterns into business intelligence
            - Provide metrics-based recommendations
            - Suggest KPIs for ongoing monitoring
            - Calculate potential impact of changes
            
            Use rigorous analytical approach with actual numbers.
            Provide both the analysis and the business implications.
            """,
            
            "crag": f"""
            {base_context}
            
            USER QUERY: {query}
            USER ROLE: {user_role}
            AGENT TYPE: CRAG (Corrective RAG with Validation)
            
            Use SELF-REFLECTIVE ANALYSIS with data validation:
            
            INITIAL ASSESSMENT:
            - Provide initial analysis based on available data
            - Identify key findings and recommendations
            - Note any assumptions made during analysis
            
            DATA VALIDATION:
            - Cross-reference findings with multiple data sources
            - Check for consistency across different metrics
            - Identify potential data quality issues
            - Validate assumptions against actual business context
            
            CORRECTIVE ANALYSIS:
            - Refine recommendations based on validation
            - Correct any inaccurate assumptions
            - Provide confidence levels for different findings
            - Suggest additional data needed for higher confidence
            
            IMPROVED RECOMMENDATIONS:
            - Final validated recommendations
            - Implementation considerations
            - Monitoring suggestions for ongoing validation
            - Risk assessment based on data quality
            
            Show your validation process and how it improved the analysis.
            Be transparent about data limitations and confidence levels.
            """
        }
        
        return agent_specific_prompts.get(agent_type, 
            base_context + f"\n\nQUERY: {query}\nUSER ROLE: {user_role}\n\nProvide a comprehensive response using the business data above.")

    def format_data_for_prompt(self, data: Dict) -> str:
        """Format data for inclusion in prompts"""
        formatted = []
        
        try:
            # Format products data
            if 'products' in data and data['products']:
                sample_products = data['products'][:3]
                product_info = []
                for product in sample_products:
                    name = product.get('product_name', 'Unknown')[:20]
                    stock = product.get('stock_quantity', 0)
                    price = product.get('price', 0)
                    product_info.append(f"{name} (Stock: {stock}, Price: ${price})")
                formatted.append(f"Sample Products: {', '.join(product_info)}")
            
            # Format low stock data
            if 'low_stock' in data and data['low_stock']:
                low_stock_names = [p.get('product_name', 'Unknown')[:15] for p in data['low_stock'][:3]]
                formatted.append(f"Critical Low Stock: {', '.join(low_stock_names)}")
            
            # Format user distribution
            if 'user_analytics' in data:
                user_data = data['user_analytics'].get('user_analytics', {})
                role_dist = user_data.get('role_distribution', [])
                roles = [f"{r.get('role_name', 'Unknown')}: {r.get('user_count', 0)}" for r in role_dist[:3]]
                if roles:
                    formatted.append(f"User Roles: {', '.join(roles)}")
            
            # Format category insights
            if 'category_insights' in data:
                cats = data['category_insights'].get('category_insights', [])
                if cats:
                    cat_names = [c.get('category_name', 'Unknown')[:15] for c in cats[:3]]
                    formatted.append(f"Top Categories: {', '.join(cat_names)}")
            
            # Format sales trends
            if 'sales_trends' in data:
                trends = data['sales_trends']
                formatted.append(f"Business Health Score: {trends.get('health_score', 'N/A')}")
                    
        except Exception as e:
            logger.error(f"❌ Error formatting data: {e}")
            formatted.append(f"Data formatting error: {str(e)}")
        
        return "\n".join(formatted)

    # Individual agent methods for direct access
    def react_agent(self, query: str, user_role: str, data: Dict = None) -> Dict:
        """Direct REACT agent access"""
        if data is None:
            data = self.get_comprehensive_business_data(query)
        
        prompt = self.create_data_rich_prompt(query, user_role, "react", data)
        response = self.safe_generate(prompt)
        
        return {
            "response": response,
            "type": "react",
            "data": data,
            "reasoning": "REACT pattern with step-by-step reasoning",
            "needs_human_review": False
        }

    def planner_agent(self, query: str, user_role: str, data: Dict = None) -> Dict:
        """Direct PLANNER agent access"""
        if data is None:
            data = self.get_comprehensive_business_data(query)
        
        prompt = self.create_data_rich_prompt(query, user_role, "planner", data)
        response = self.safe_generate(prompt)
        
        return {
            "response": response,
            "type": "planner",
            "data": data,
            "reasoning": "Strategic planning with phased approach",
            "needs_human_review": False
        }

    def analytics_agent(self, query: str, user_role: str, data: Dict = None) -> Dict:
        """Direct ANALYTICS agent access"""
        if data is None:
            data = self.get_comprehensive_business_data(query)
        
        prompt = self.create_data_rich_prompt(query, user_role, "analytics", data)
        response = self.safe_generate(prompt)
        
        return {
            "response": response,
            "type": "analytics",
            "data": data,
            "reasoning": "Data-driven analytical insights",
            "needs_human_review": False
        }

    def rag_agent(self, query: str, user_role: str, data: Dict = None) -> Dict:
        """Direct RAG agent access"""
        if data is None:
            data = self.get_comprehensive_business_data(query)
        
        prompt = self.create_data_rich_prompt(query, user_role, "rag", data)
        response = self.safe_generate(prompt)
        
        return {
            "response": response,
            "type": "rag",
            "data": data,
            "reasoning": "Data retrieval and presentation",
            "needs_human_review": False
        }

    def crag_agent(self, query: str, user_role: str, data: Dict = None) -> Dict:
        """Direct CRAG agent access"""
        if data is None:
            data = self.get_comprehensive_business_data(query)
        
        prompt = self.create_data_rich_prompt(query, user_role, "crag", data)
        response = self.safe_generate(prompt)
        
        return {
            "response": response,
            "type": "crag",
            "data": data,
            "reasoning": "Self-validating analysis with correction",
            "needs_human_review": False
        }

# Create global instance
try:
    enhanced_ai_agent = EnhancedAIAgent()
    if enhanced_ai_agent.available:
        logger.info("✅ Enhanced AI Agent initialized successfully with full data integration")
    else:
        logger.warning("⚠️ Enhanced AI Agent initialized but not available - check Ollama")
except Exception as e:
    logger.error(f"💥 Failed to create Enhanced AI Agent: {e}")
    # Fallback
    class FallbackEnhancedAgent:
        def __init__(self):
            self.available = False
        def supervisor_agent(self, query, user_role, conversation_history=None):
            return {
                "response": "Enhanced AI service is currently unavailable. Please check:\n1. Ollama is installed and running\n2. llama3.1:latest model is available\n3. Backend services are running",
                "type": "error",
                "data": {},
                "reasoning": "Fallback mode - agent initialization failed",
                "needs_human_review": True
            }
        def react_agent(self, query, user_role, data=None):
            return self.supervisor_agent(query, user_role)
        def planner_agent(self, query, user_role, data=None):
            return self.supervisor_agent(query, user_role)
        def analytics_agent(self, query, user_role, data=None):
            return self.supervisor_agent(query, user_role)
        def rag_agent(self, query, user_role, data=None):
            return self.supervisor_agent(query, user_role)
        def crag_agent(self, query, user_role, data=None):
            return self.supervisor_agent(query, user_role)
    
    enhanced_ai_agent = FallbackEnhancedAgent()
