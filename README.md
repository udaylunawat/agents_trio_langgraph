# 🤖 Multi-Agent AI System

A modern, modular AI system featuring three specialized agents with dynamic LLM provider selection. Built with FastAPI backend and Streamlit frontend for seamless interaction.

## ✨ Features

- **🔄 Three AI Agents:**
  - **AQI Agent**: Air quality analysis with health impact assessments
  - **PDF Agent**: RAG-powered document Q&A with citation support
  - **YouTube Agent**: Creative content recommendations and script outlines

- **🧠 Multiple LLM Support:**
  - OpenRouter (free models like minimax/minimax-m2:free)
  - OpenAI (GPT models)
  - User-selectable models and providers

- **🎨 Modern UI:**
  - Streamlit tabbed interface
  - Real-time LLM provider selection
  - Expandable citations and structured responses

- **⚡ Production Ready:**
  - LangChain integration for RAG
  - Proper error handling and fallbacks
  - Environment-based configuration

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git

### 1. Clone & Setup
```bash
git clone <repository-url>
cd plan-a-agents
cd repo
```

### 2. Install Dependencies
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt  # You'll need to create this
```

### 3. Configure API Keys

Edit `repo/.env` file:
```bash
# Choose your preferred provider
OPENROUTER_API_KEY=your_openrouter_key_here
# OR
OPENAI_API_KEY=your_openai_key_here
```

**Get API Keys:**
- **OpenRouter**: https://openrouter.ai/keys (Free tier available)
- **OpenAI**: https://platform.openai.com/api-keys

### 4. Start the Application

**Terminal 1 - FastAPI Backend:**
```bash
cd repo
.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/

**Terminal 2 - Streamlit Frontend:**
```bash
cd repo
.venv/bin/streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```
- Web Interface: http://localhost:8501

## 🎯 Usage Guide

### Web Interface (Streamlit)
1. **Select LLM Provider**: Choose OpenRouter or OpenAI from sidebar
2. **Enter API Key**: Input your API key securely
3. **Choose Model**: Select preferred model (defaults to free options)
4. **Use Agents**: Navigate between tabs to interact with each agent

### API Endpoints

#### AQI Agent
Analyze air quality data with intelligent health recommendations.

**Request:**
```bash
curl -X POST "http://localhost:8000/aqi/query" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Delhi",
    "date": "2025-10-23",
    "question": "Is it safe to run outside?",
    "llm_provider": "OpenRouter",
    "model_name": "minimax/minimax-m2:free",
    "api_key": "your-api-key"
  }'
```

**Sample Data:**
- Delhi: High pollution (AQI 312)
- Srinagar: Good air quality (AQI 82)

#### PDF Agent
Ask questions about documents using RAG with citations.

**Request:**
```bash
curl -X POST "http://localhost:8000/pdfs/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are agent workflows?",
    "top_k": 3,
    "llm_provider": "OpenRouter",
    "model_name": "minimax/minimax-m2:free",
    "api_key": "your-api-key"
  }'
```

**Document Sources:**
- `agent-workflows.txt`: AI agent architecture guide
- `langchain-guide.txt`: LangChain implementation primer

#### YouTube Agent
Get creative video recommendations and script outlines.

**Request:**
```bash
curl -X POST "http://localhost:8000/youtube/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "AI agents for productivity",
    "top_k": 3,
    "llm_provider": "OpenRouter",
    "model_name": "minimax/minimax-m2:free",
    "api_key": "your-api-key"
  }'
```

**Sample Data:** 5 YouTube scripts with engagement metrics.

## 🏗️ Architecture

```
├── utils.py                # Shared utilities and LLM creation functions
├── agents/                 # Agent implementations
│   ├── aqi.py             # Air quality analyzer
│   ├── pdfs.py            # RAG document Q&A
│   └── youtube.py         # Content recommender
├── data/                  # Sample datasets
│   ├── aqi/              # Air quality JSON files
│   ├── youtube.csv       # Video content data
│   └── pdfs/             # Text documents
├── app.py                 # FastAPI application
├── streamlit_app.py       # Web interface
├── pyproject.toml         # Dependencies
└── .env                   # Configuration
```

### 🧹 Code Organization

- **Shared Functions**: LLM creation logic is centralized in `utils.py`
- **Agent Separation**: Each agent focuses on its specific domain logic
- **Configuration Management**: Environment variables handle API keys and settings
- **Error Handling**: Consistent error handling across all agents

## 🔧 Configuration

### Environment Variables
```bash
# LLM Providers (choose one or both)
OPENROUTER_API_KEY=your_openrouter_key
OPENAI_API_KEY=your_openai_key

# Optional: Custom base URLs
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Adding Custom Data

**AQI Data:**
```bash
# Add JSON files to data/aqi/ with format:
{
  "city": "CityName",
  "date": "YYYY-MM-DD",
  "aqi": 150,
  "pm2_5": 75,
  "pm10": 100,
  "o3": 25,
  "no2": 30
}
```

**YouTube Data:**
```csv
title,script,likes,views
"Your Video Title","Script content here...",100,5000
```

**Documents:**
- Add `.txt` files to `data/pdfs/`
- Automatically indexed using TF-IDF similarity
- Supports RAG-based Q&A

## 🧪 Testing

### Unit Tests
```bash
cd repo
python -m pytest tests/  # Create tests directory
```

### Manual Testing
1. Start both servers
2. Open http://localhost:8501
3. Configure your LLM provider
4. Test each agent tab

## 🚀 Deployment

### Local Development
Follow the Quick Start guide above.

### Docker Deployment
```dockerfile
# Create Dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8000 8501
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment
- **Railway**: FastAPI + Procfile
- **Vercel**: API routes only
- **Streamlit Cloud**: Frontend only
- **AWS/Google Cloud**: Full containerized deployment

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/agent-enhancement`
3. Add tests and documentation
4. Submit pull request

### Development Guidelines
- Use type hints and Pydantic models
- Add comprehensive error handling
- Update documentation for API changes
- Test with multiple LLM providers

## 📋 Roadmap

- [ ] Voice input support
- [ ] Real-time chat interface
- [ ] Plugin system for custom agents
- [ ] Multi-modal content processing
- [ ] Advanced RAG with vector databases
- [ ] Agent collaboration workflows

## 📞 Support

**Issues & Features:**
- GitHub Issues: Report bugs and request features
- Documentation: Comprehensive API guides
- Community: Join discussions and share use cases

---

**Built with:** FastAPI, Streamlit, LangChain, OpenRouter, OpenAI
