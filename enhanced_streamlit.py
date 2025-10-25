
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import requests
import json
from typing import  List
# Import the enhanced agent
try:
    from enhanced_agent import enhanced_ai_agent
except ImportError:
    # Fallback if import fails
    class FallbackAgent:
        def __init__(self):
            self.available = False
        def supervisor_agent(self, query, user_role, conversation_history=None):
            return {
                "response": "Enhanced agent not available. Please check enhanced_agent.py",
                "type": "error", 
                "data": {},
                "reasoning": "Import failed",
                "needs_human_review": True
            }
    enhanced_ai_agent = FallbackAgent()

def show_enhanced_ai_interface():
    """Enhanced AI interface with advanced features"""
    
    st.header("🎯 Intelligent Business Assistant")
    
    # Initialize enhanced chat in session state
    if 'enhanced_chat' not in st.session_state:
        st.session_state.enhanced_chat = []
    
    # Initialize quick action state
    if 'quick_action_query' not in st.session_state:
        st.session_state.quick_action_query = ""
    
    # User expertise level
    expertise = st.sidebar.selectbox(
        "🎓 Your Expertise Level",
        ["Executive", "Manager", "Analyst", "Novice"],
        help="Adjusts the technical depth of responses"
    )
    
    # Response style
    response_style = st.sidebar.selectbox(
        "💬 Response Style", 
        ["Conversational", "Formal", "Technical", "Storytelling"],
        help="Changes how information is presented"
    )
    
    # Real-time features toggle
    real_time = st.sidebar.toggle("⏱️ Real-time Streaming", True)
    visual_stories = st.sidebar.toggle("📊 Visual Storytelling", True)
    
    # Display agent status
    if hasattr(enhanced_ai_agent, 'available'):
        if enhanced_ai_agent.available:
            st.sidebar.success("✅ Enhanced Agent: Active")
        else:
            st.sidebar.error("❌ Enhanced Agent: Unavailable")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.enhanced_chat:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant"):
                    # Display agent type badge
                    agent_type = msg.get("agent_type", "unknown")
                    agent_emoji = get_agent_emoji(agent_type)
                    st.write(f"{agent_emoji} **{agent_type.upper()} Agent**")
                    
                    # Display response content
                    if real_time and len(msg.get("content", "")) > 100:
                        display_streaming_text(msg["content"])
                    else:
                        st.write(msg["content"])
                    
                    # Enhanced response features
                    if msg.get("tiered_responses"):
                        with st.expander("🔍 Detailed Analysis"):
                            for tier in msg["tiered_responses"]:
                                st.write(f"**{tier['level'].title()} Summary:**")
                                st.write(tier["content"])
                    
                    if msg.get("visual_narrative") and visual_stories:
                        with st.expander("📖 Story View"):
                            st.write(msg["visual_narrative"])
                    
                    if msg.get("actions"):
                        st.write("**🎯 Recommended Actions:**")
                        for action in msg["actions"]:
                            st.write(f"• {action}")
                    
                    # Show data insights if available
                    if msg.get("data_insights"):
                        with st.expander("📊 Data Insights"):
                            st.json(msg["data_insights"])
    
    # Enhanced chat input with suggestions
    st.subheader("💡 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    # Quick action buttons
    quick_actions = {
        "📈 Financial Health": "Analyze our current financial health, revenue trends, cost structure, and suggest specific improvements with ROI estimates",
        "🛒 Inventory Opt": "Optimize our inventory levels, identify slow-moving products, suggest restocking strategies, and calculate potential cost savings", 
        "👥 Team Performance": "Analyze team performance metrics, identify skill gaps, suggest training programs, and recommend productivity improvements",
        "🔮 Predict Trends": "Predict sales trends for next quarter, identify growth opportunities, analyze seasonal patterns, and provide actionable insights",
        "📊 System Health": "Comprehensive system health analysis including database performance, user activity, API usage, and optimization recommendations",
        "🎯 Strategic Plan": "Develop a 6-month strategic plan with quarterly milestones, resource allocation, risk assessment, and success metrics",
        "🔍 Deep Analysis": "Conduct deep analysis of all business operations including cross-departmental insights and integrated recommendations", 
        "🔄 Process Review": "Review and optimize business processes, identify bottlenecks, suggest automation opportunities, and calculate efficiency gains"
    }
    
    # First row of quick actions
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📈 Financial Health", use_container_width=True, key="fin_health"):
            st.session_state.quick_action_query = quick_actions["📈 Financial Health"]
            st.rerun()
    with col2:
        if st.button("🛒 Inventory Opt", use_container_width=True, key="inv_opt"):
            st.session_state.quick_action_query = quick_actions["🛒 Inventory Opt"]
            st.rerun()
    with col3:
        if st.button("👥 Team Performance", use_container_width=True, key="team_perf"):
            st.session_state.quick_action_query = quick_actions["👥 Team Performance"]
            st.rerun()
    with col4:
        if st.button("🔮 Predict Trends", use_container_width=True, key="pred_trends"):
            st.session_state.quick_action_query = quick_actions["🔮 Predict Trends"]
            st.rerun()
    
    # Second row of quick actions  
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        if st.button("📊 System Health", use_container_width=True, key="sys_health"):
            st.session_state.quick_action_query = quick_actions["📊 System Health"]
            st.rerun()
    with col6:
        if st.button("🎯 Strategic Plan", use_container_width=True, key="strat_plan"):
            st.session_state.quick_action_query = quick_actions["🎯 Strategic Plan"]
            st.rerun()
    with col7:
        if st.button("🔍 Deep Analysis", use_container_width=True, key="deep_analysis"):
            st.session_state.quick_action_query = quick_actions["🔍 Deep Analysis"]
            st.rerun()
    with col8:
        if st.button("🔄 Process Review", use_container_width=True, key="process_review"):
            st.session_state.quick_action_query = quick_actions["🔄 Process Review"]
            st.rerun()
    
    # Handle quick action queries
    if st.session_state.quick_action_query:
        process_query(st.session_state.quick_action_query, expertise, visual_stories, response_style)
        st.session_state.quick_action_query = ""  # Reset after processing
    
    # Regular chat input
    user_input = st.chat_input("Ask me anything about your business...")
    
    if user_input:
        process_query(user_input, expertise, visual_stories, response_style)

def display_streaming_text(text: str):
    """Display text with streaming effect"""
    placeholder = st.empty()
    displayed_text = ""
    
    for char in text:
        displayed_text += char
        placeholder.write(displayed_text)
        time.sleep(0.01)  # Adjust speed as needed

def process_query(user_input: str, expertise: str, visual_stories: bool, response_style: str):
    """Process user query and generate enhanced response"""
    # Add user message to chat
    st.session_state.enhanced_chat.append({"role": "user", "content": user_input})
    
    # Generate enhanced response
    with st.spinner("🤔 Analyzing with multi-agent system..."):
        try:
            # Use the enhanced AI agent directly
            response_data = enhanced_ai_agent.supervisor_agent(
                query=user_input,
                user_role=st.session_state.user.get('role', 'user'),
                conversation_history=st.session_state.enhanced_chat
            )
            
            # Apply response style
            styled_response = apply_response_style(response_data["response"], response_style)
            
            # Create enhanced response object
            enhanced_response = {
                "role": "assistant", 
                "content": styled_response,
                "agent_type": response_data.get("type", "supervisor"),
                "tiered_responses": create_tiered_responses(
                    styled_response, 
                    response_data.get("data", {}),
                    expertise
                ),
                "visual_narrative": create_visual_narrative(
                    response_data.get("data", {}), 
                    user_input,
                    styled_response
                ) if visual_stories else None,
                "actions": extract_actions_from_response(styled_response),
                "data_insights": response_data.get("data", {}),
                "reasoning": response_data.get("reasoning", "")
            }
            
            st.session_state.enhanced_chat.append(enhanced_response)
            
        except Exception as e:
            # Fallback response
            st.session_state.enhanced_chat.append({
                "role": "assistant",
                "content": f"I encountered an error: {str(e)}. Please check the enhanced agent setup.",
                "agent_type": "error"
            })
        
        st.rerun()

def apply_response_style(response: str, style: str) -> str:
    """Apply different response styles"""
    if style == "Formal":
        return f"**Formal Analysis**\n\n{response}"
    elif style == "Technical":
        return f"**Technical Assessment**\n\n{response}"
    elif style == "Storytelling":
        return f"**Narrative Insights**\n\n{response}"
    else:  # Conversational
        return response

def extract_actions_from_response(response: str) -> List[str]:
    """Extract actionable items from response"""
    actions = []
    lines = response.split('\n')
    
    for line in lines:
        line = line.strip()
        # Look for bullet points or numbered items that seem like actions
        if (line.startswith(('-', '•', '1.', '2.', '3.', '4.', '5.', 'Recommend', 'Action', 'Step')) 
            and len(line) > 15):
            # Clean up the action item
            action = line.lstrip('-•12345. ').strip()
            if action and not action.startswith('**'):  # Avoid headers
                actions.append(action)
    
    return actions[:5]  # Return top 5 actions

def get_agent_emoji(agent_type: str) -> str:
    """Get emoji for different agent types"""
    emoji_map = {
        "react": "🤔",
        "planner": "📋", 
        "supervisor": "👨‍💼",
        "rag": "🔍",
        "crag": "🔄", 
        "analytics": "📊",
        "error": "❌"
    }
    return emoji_map.get(agent_type, "🤖")

def create_tiered_responses(response: str, data: dict, expertise: str) -> list:
    """Create tiered information based on expertise level"""
    
    if expertise == "Executive":
        return [
            {"level": "executive", "content": f"**Executive Summary:** Key strategic insights and high-impact recommendations from the analysis."},
            {"level": "managerial", "content": f"**Management View:** Operational implications and implementation considerations."},
            {"level": "detailed", "content": response}
        ]
    
    elif expertise == "Manager":
        return [
            {"level": "managerial", "content": f"**Management Overview:** Balanced analysis of strategic and operational aspects."},
            {"level": "detailed", "content": response}
        ]
    
    elif expertise == "Analyst":
        return [
            {"level": "analytical", "content": f"**Technical Context:** Data-driven insights and implementation details."},
            {"level": "detailed", "content": response}
        ]
    
    else:  # Novice
        return [
            {"level": "simple", "content": f"**Simple Explanation:** Easy-to-understand overview of the situation."},
            {"level": "detailed", "content": response}
        ]

def create_visual_narrative(data: dict, query: str, response: str) -> str:
    """Create visual storytelling narrative"""
    
    narrative = f"📖 **Business Story**\n\n"
    
    # Custom narratives based on query type
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['inventory', 'stock', 'product']):
        narrative += "Imagine our inventory as a dynamic ecosystem where each product has its lifecycle. "
        narrative += "Like a skilled gardener, we nurture fast-growing items while pruning slow-movers to maintain a healthy balance. "
        narrative += "This careful cultivation ensures optimal growth and sustainability.\n\n"
    
    elif any(word in query_lower for word in ['financial', 'revenue', 'cost']):
        narrative += "Picture our finances as a flowing river where revenue streams converge. "
        narrative += "Strategic dams (investments) and channels (expenses) guide the flow toward prosperity lakes. "
        narrative += "Our analysis helps navigate these waters for maximum benefit.\n\n"
    
    elif any(word in query_lower for word in ['team', 'user', 'performance']):
        narrative += "Envision our team as a symphony orchestra where each member plays a crucial part. "
        narrative += "Harmonious coordination creates beautiful music (results), while our conductor (management) ensures perfect timing and rhythm. "
        narrative += "This symphony drives our business forward.\n\n"
    
    else:
        narrative += "Think of our business as a well-oiled machine where every component works in harmony. "
        narrative += "Regular maintenance (optimization) and upgrades (innovation) keep the machine running smoothly, "
        narrative += "delivering exceptional performance and driving us toward our goals.\n\n"
    
    narrative += "**The Path Forward:** Continuous improvement and data-driven decisions will guide our success journey."
    
    return narrative
