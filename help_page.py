
import streamlit as st

def show_help_page():
    """Comprehensive help and documentation page"""
    
    st.title("🆘 Help & Documentation")
    
    # Quick Navigation
    st.sidebar.header("📚 Quick Navigation")
    help_sections = [
        "Getting Started",
        "AI Assistant Guide", 
        "Agent Patterns",
        "Response Styles",
        "Troubleshooting",
        "API Documentation"
    ]
    selected_section = st.sidebar.selectbox("Jump to Section", help_sections)
    
    # Getting Started Section
    if selected_section == "Getting Started":
        st.header("🚀 Getting Started")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Quick Setup")
            st.markdown("""
            1. **Start Backend**: `python main.py`
            2. **Start Frontend**: `streamlit run streamlit_app.py`
            3. **Access URLs**:
               - Frontend: `http://localhost:8501`
               - Backend API: `http://localhost:8000`
            4. **Login** with default credentials
            """)
            
            st.subheader("🔐 Default Credentials")
            st.markdown("""
            | Role | Username | Password | Access |
            |------|----------|----------|--------|
            | Admin | `admin` | `admin123` | Full system access |
            | Manager | `manager` | `manager123` | Products & categories |
            | User | `user1` | `password123` | Read-only + AI queries |
            """)
        
        with col2:
            st.subheader("🎯 First Steps")
            st.markdown("""
            **For Executives:**
            - Navigate to **🤖 AI Assistant**
            - Set expertise to **Executive**
            - Try: *"Give me business health overview"*
            
            **For Managers:**
            - Use **🛒 Inventory Opt** quick action
            - Set style to **Conversational** 
            - Try: *"Analyze team performance"*
            
            **For Analysts:**
            - Set expertise to **Analyst**
            - Use **Technical** response style
            - Try: *"Show system performance metrics"*
            """)
    
    # AI Assistant Guide Section
    elif selected_section == "AI Assistant Guide":
        st.header("🤖 AI Assistant Guide")
        
        st.subheader("🎨 Interface Features")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🎓 Expertise Levels**
            - **Executive**: Strategic overviews
            - **Manager**: Operational insights  
            - **Analyst**: Technical details
            - **Novice**: Simple explanations
            """)
        
        with col2:
            st.markdown("""
            **💬 Response Styles**
            - **Conversational**: Chat-like, friendly
            - **Formal**: Professional, structured
            - **Technical**: Data-focused, detailed
            - **Storytelling**: Narrative, engaging
            """)
        
        with col3:
            st.markdown("""
            **⚡ Interactive Features**
            - **Real-time Streaming**: Typing simulation
            - **Visual Storytelling**: Business narratives
            - **Data Metrics**: Live KPIs display
            - **Quick Actions**: One-click complex queries
            """)
        
        st.subheader("💡 Quick Actions Explained")
        st.markdown("""
        | Button | Purpose | Best For |
        |--------|---------|----------|
        | 📈 **Financial Health** | Comprehensive financial analysis | Executives, Managers |
        | 🛒 **Inventory Opt** | Stock optimization strategies | Operations, Managers |
        | 👥 **Team Performance** | User analytics & training needs | HR, Team Leads |
        | 🔮 **Predict Trends** | Sales forecasting & insights | Sales, Marketing |
        | 📊 **System Health** | Technical system assessment | IT, Administrators |
        | 🎯 **Strategic Plan** | Long-term business planning | Executives, Strategy |
        | 🔍 **Deep Analysis** | Cross-functional insights | Analysts, Consultants |
        | 🔄 **Process Review** | Operational efficiency | Operations, Managers |
        """)
    
    # Agent Patterns Section
    elif selected_section == "Agent Patterns":
        st.header("🤖 AI Agent Patterns")
        
        st.subheader("Intelligent Agent Orchestration")
        st.markdown("""
        The system automatically selects the best agent for your query based on complexity and content.
        """)
        
        agents = [
            {
                "name": "👨‍💼 Supervisor Agent",
                "purpose": "Master coordinator for complex queries",
                "triggers": "comprehensive, overview, assessment, report",
                "example": "*'Complete business health assessment'*"
            },
            {
                "name": "🤔 REACT Agent", 
                "purpose": "Step-by-step reasoning with actions",
                "triggers": "why, how, solve, fix, improve, problem",
                "example": "*'Why are sales decreasing and what should we do?'*"
            },
            {
                "name": "📋 Planner Agent",
                "purpose": "Strategic planning with timelines",
                "triggers": "plan, strategy, roadmap, timeline, develop",
                "example": "*'Create 6-month inventory optimization plan'*"
            },
            {
                "name": "🔍 RAG Agent",
                "purpose": "Data retrieval and presentation", 
                "triggers": "show, list, get, find, retrieve, display",
                "example": "*'Show me products with low stock'*"
            },
            {
                "name": "📊 Analytics Agent",
                "purpose": "Data analysis and trend identification",
                "triggers": "analyze, trend, pattern, insight, metric",
                "example": "*'Analyze sales performance trends'*"
            },
            {
                "name": "🔄 CRAG Agent",
                "purpose": "Self-validation and correction",
                "triggers": "validate, verify, check, review, assess",
                "example": "*'Validate our inventory strategy'*"
            }
        ]
        
        for agent in agents:
            with st.expander(agent["name"]):
                st.markdown(f"""
                **Purpose:** {agent["purpose"]}
                
                **Auto-Triggers:** `{agent["triggers"]}`
                
                **Example Query:** {agent["example"]}
                """)
    
    # Response Styles Section  
    elif selected_section == "Response Styles":
        st.header("💬 Response Styles Guide")
        
        st.subheader("Choosing the Right Style")
        st.markdown("""
        | Style | Best For | Audience | Example Use |
        |-------|----------|----------|-------------|
        | **🗣️ Conversational** | Daily operations, team meetings | Mixed teams, quick chats | Standup meetings, quick decisions |
        | **📋 Formal** | Executive reports, client comms | Executives, board members | Quarterly reports, presentations |
        | **🔧 Technical** | Data analysis, system admin | Technical teams, developers | Performance reviews, optimizations |
        | **📖 Storytelling** | Engagement, training, change mgmt | Stakeholders, entire company | All-hands meetings, onboarding |
        """)
        
        st.subheader("Style Combination Examples")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🏢 Executive Presentation**
            - Primary: **Formal** style
            - Enable: **Storytelling** for engagement
            - Expertise: **Executive** level
            - Use: Board meetings, investor updates
            
            **🔧 Technical Deep Dive**
            - Primary: **Technical** style  
            - Enable: **Data Metrics** display
            - Expertise: **Analyst** level
            - Use: System optimization, code reviews
            """)
        
        with col2:
            st.markdown("""
            **👥 Team Collaboration**
            - Primary: **Conversational** style
            - Enable: **Real-time Streaming**
            - Expertise: **Manager** level
            - Use: Daily standups, team planning
            
            **🎓 Training Session**
            - Primary: **Storytelling** style
            - Enable: **Visual Storytelling** 
            - Expertise: **Novice** level
            - Use: Onboarding, workshops
            """)
    
    # Troubleshooting Section
    elif selected_section == "Troubleshooting":
        st.header("🔧 Troubleshooting Guide")
        
        st.subheader("Common Issues & Solutions")
        
        issues = [
            {
                "problem": "❌ AI Agent not available",
                "symptoms": ["AI service unavailable messages", "No agent badges showing"],
                "solutions": [
                    "Check Ollama is running: `ollama serve`",
                    "Verify model: `ollama list`", 
                    "Test model: `ollama run llama3.1:latest`",
                    "Restart both application servers"
                ]
            },
            {
                "problem": "🐢 Slow response times", 
                "symptoms": ["Responses taking >2 minutes", "Spinner stuck for long time"],
                "solutions": [
                    "Use 'Conversational' style for faster responses",
                    "Keep queries focused and specific",
                    "Ensure adequate system resources",
                    "Check Ollama has sufficient RAM (4GB+)"
                ]
            },
            {
                "problem": "🔐 Login issues",
                "symptoms": ["Authentication errors", "Session timeouts"],
                "solutions": [
                    "Clear browser cache and cookies",
                    "Use default credentials for testing",
                    "Check backend authentication service",
                    "Verify JWT token in session state"
                ]
            },
            {
                "problem": "📊 No data in responses",
                "symptoms": ["Generic responses without numbers", "No business metrics"],
                "solutions": [
                    "Check if main.py backend is running",
                    "Verify database connectivity",
                    "Use RAG agent for data queries",
                    "Try specific data requests"
                ]
            }
        ]
        
        for issue in issues:
            with st.expander(issue["problem"]):
                st.markdown("**Symptoms:**")
                for symptom in issue["symptoms"]:
                    st.markdown(f"- {symptom}")
                
                st.markdown("**Solutions:**")
                for solution in issue["solutions"]:
                    st.markdown(f"- {solution}")
        
        st.subheader("Performance Optimization Tips")
        st.markdown("""
        - **For speed**: Use 'Conversational' style + disable streaming
        - **For engagement**: Use 'Storytelling' + enable streaming  
        - **For data analysis**: Use 'Technical' + enable data metrics
        - **For presentations**: Use 'Formal' + enable storytelling
        - **System resources**: Ensure 4GB+ RAM available for Ollama
        """)
    
    # API Documentation Section
    elif selected_section == "API Documentation":
        st.header("🔌 API Documentation")
        
        st.subheader("Available Endpoints")
        
        endpoints = [
            {
                "method": "POST",
                "endpoint": "/ai/enhanced-query",
                "description": "Enhanced AI agent query with multi-agent system",
                "parameters": '{"query": "string", "response_style": "string"}'
            },
            {
                "method": "POST", 
                "endpoint": "/ai/query",
                "description": "Basic AI query endpoint",
                "parameters": '{"query": "string"}'
            },
            {
                "method": "GET",
                "endpoint": "/ai/status", 
                "description": "Check AI agent and Ollama status",
                "parameters": "None"
            },
            {
                "method": "GET",
                "endpoint": "/admin/users",
                "description": "Get all users (Admin only)",
                "parameters": "None"
            },
            {
                "method": "POST",
                "endpoint": "/login",
                "description": "User authentication",
                "parameters": '{"username": "string", "password": "string"}'
            }
        ]
        
        for endpoint in endpoints:
            with st.expander(f"{endpoint['method']} {endpoint['endpoint']}"):
                st.markdown(f"""
                **Description:** {endpoint['description']}
                
                **Parameters:**
                ```json
                {endpoint['parameters']}
                ```
                
                **Access:** { "Admin only" if "admin" in endpoint['endpoint'] else "Authenticated users" }
                """)
        
        st.subheader("API Base URL")
        st.code("http://localhost:8000")
        
        st.subheader("Interactive API Docs")
        st.markdown("""
        For full interactive API documentation, visit:
        **[http://localhost:8000/docs](http://localhost:8000/docs)**
        
        Features:
        - Try endpoints directly from browser
        - View request/response schemas
        - Test authentication
        - See response examples
        """)
    
    # Quick Help Card at Bottom
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🚀 Need Immediate Help?**
        - Check if all services are running
        - Use default test credentials
        - Try quick action buttons first
        """)
    
    with col2:
        st.markdown("""
        **🎯 Best Practices**
        - Start with quick actions
        - Experiment with different styles
        - Use appropriate expertise levels
        - Enable features based on audience
        """)
    
    with col3:
        st.markdown("""
        **📞 Support**
        - Check application logs
        - Verify service status
        - Test with sample queries
        - Restart services if needed
        """)

# Add this to your streamlit_app.py navigation
def add_help_to_navigation():
    """Add help page to navigation"""
    # In your streamlit_app.py, modify the navigation options:
    """
    if user_role == "admin":
        nav_options = ["🤖 AI Assistant", "📁 Categories", "📦 Products", "👥 User Management", "📊 Analytics", "🆘 Help"]
    elif user_role == "manager":
        nav_options = ["🤖 AI Assistant", "📁 Categories", "📦 Products", "📊 Analytics", "🆘 Help"]
    else:  # user
        nav_options = ["🤖 AI Assistant", "📁 Categories", "📦 Products", "🆘 Help"]
    
    # Then handle the help page:
    if tab == "🆘 Help":
        show_help_page()
    """
