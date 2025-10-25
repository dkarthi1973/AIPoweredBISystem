# 🚀 AI-Powered Business Intelligence System

## 📖 Overview

An advanced enterprise application that transforms traditional inventory management into intelligent, data-driven decision support using multiple AI agent patterns. This system combines sophisticated AI orchestration with real-time business data analysis to deliver actionable insights across all organizational levels.


## 🎯 Key Features

### 🤖 Intelligent AI Agents
- **👨‍💼 Supervisor Agent**: Master coordinator for complex queries
- **🤔 REACT Agent**: Step-by-step reasoning with actionable recommendations
- **📋 Planner Agent**: Strategic planning with phased execution
- **🔍 RAG Agent**: Data retrieval with contextual understanding
- **📊 Analytics Agent**: Data analysis and trend identification
- **🔄 CRAG Agent**: Self-validating analysis with correction

### 🎨 Adaptive User Experience
- **🎓 Progressive Disclosure**: Information tailored to expertise levels
- **💬 Multiple Response Styles**: Conversational, Formal, Technical, Storytelling
- **⚡ Real-time Features**: Streaming responses, live data metrics
- **🚀 Quick Actions**: One-click complex business analysis

### 📊 Business Intelligence
- Real-time inventory analytics and optimization
- Financial health monitoring and ROI calculations
- User performance metrics and team analytics
- System health dashboard with proactive alerts

## 🛠️ Tech Stack

**Frontend:** Streamlit + Plotly + Pandas  
**Backend:** FastAPI + SQLite + JWT Auth + Argon2  
**AI Engine:** Ollama + Llama 3.1 + LangGraph  
**Agents:** REACT, Planner, Supervisor, RAG, Analytics, CRAG patterns

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Ollama installed
- 4GB+ RAM for AI processing

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Setup AI engine
ollama serve
ollama pull llama3.1:latest

# Launch application
python main.py                    # Terminal 1 - Backend
streamlit run streamlit_app.py    # Terminal 2 - Frontend
