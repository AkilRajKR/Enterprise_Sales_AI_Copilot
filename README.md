# Enterprise Sales AI Analytics System

A production-grade multi-agent AI application for sales analytics using LangGraph, LangChain, FastAPI, React, SQLite, and Google Gemini 2.5.

## 🧠 Overview

This system answers natural-language questions over an E-commerce sales database using:
- **Planner Agent**: Classifies and decomposes user questions
- **SQL Agent**: Generates and executes safe READ-ONLY queries
- **Validator Agent**: Ensures SQL results match user intent
- **Supervisor**: Controls workflow and retry logic
- **Cache Agent**: Stores and retrieves validated responses
- **Response Agent**: Generates business-friendly answers

## 🏗️ Architecture

```
User Question
    ↓
[Planner Agent] → Classify & Decompose
    ↓
[Relevance Check] → Accept/Reject
    ↓
[Cache Lookup] → Cache Hit? Return : Continue
    ↓
[SQL Agent via MCP] → Generate SELECT Query
    ↓
[Validator Agent] → Validate Result
    ↓
[Retry Logic] → Failed? Retry (Max 4 times)
    ↓
[Cache Store] → Save validated response
    ↓
[Response Agent] → Generate business answer
    ↓
[FastAPI] → Return to UI
```

## ✅ Features

✅ Multi-agent agentic orchestration with LangGraph  
✅ Semantic question caching with confidence scoring  
✅ Validation-first architecture with automatic retries  
✅ Token-optimized prompts (<100 tokens for Planner)  
✅ Evidence tracking for every answer  
✅ MCP SQLite integration (READ-ONLY)  
✅ Comprehensive audit logging  
✅ React dashboard with real-time analytics  
✅ Docker & Docker Compose for easy deployment  
✅ Unit & integration tests  
✅ Production-ready security controls  

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- Google Gemini API Key

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/AkilRajKR/Enterprise_Sales_AI_Copilot.git
   cd Enterprise_Sales_AI_Copilot
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python database/seed.py  # Initialize database with e-commerce sales data
   ```

4. **Start MCP Server**
   ```bash
   python mcp/sqlite_server.py
   ```

5. **Start FastAPI Server** (in another terminal)
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Frontend setup** (in another terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`
   API available at `http://localhost:8000`

### Docker Deployment

```bash
docker-compose up -d
```

This will start:
- FastAPI backend on port 8000
- React frontend on port 5173
- SQLite database

## 📁 Project Structure

```
Enterprise_Sales_AI_Copilot/
├── backend/
│   ├── agents/              # Agent implementations
│   │   ├── planner.py
│   │   ├── sql_agent.py
│   │   ├── validator.py
│   │   ├── response.py
│   │   └── cache.py
│   ├── graph/               # LangGraph workflow
│   │   ├── state.py
│   │   └── workflow.py
│   ├── prompts/             # Agent prompts
│   │   ├── planner_prompt.py
│   │   ├── validator_prompt.py
│   │   └── response_prompt.py
│   ├── mcp/                 # MCP SQLite integration
│   │   ├── sqlite_server.py
│   │   └── mcp_client.py
│   ├── database/            # SQLite schema & seeding
│   │   ├── schema.py
│   │   ├── seed.py
│   │   └── sales.db
│   ├── api/                 # FastAPI endpoints
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── tests/               # Unit & integration tests
│   │   ├── test_agents.py
│   │   ├── test_workflow.py
│   │   ├── test_api.py
│   │   └── test_cache.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.mcp
├── .env.example
└── README.md
```

## 🔗 API Endpoints

### POST /ask
Submit a sales question
```json
{
  "question": "What were the total sales for Q1 2024?"
}
```

Response:
```json
{
  "question": "What were the total sales for Q1 2024?",
  "answer": "Total Q1 2024 sales were $2.5M",
  "sql_query": "SELECT SUM(amount) FROM orders WHERE...",
  "evidence": {...},
  "confidence": 0.95,
  "cache_hit": false,
  "retry_count": 0,
  "validation_status": "passed",
  "execution_time_ms": 245,
  "token_usage": {...}
}
```

### GET /health
Health check endpoint

### GET /history
Retrieve query history

### GET /schema (admin)
View database schema (requires admin key)

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
pytest tests/ -v --cov=agents --cov=graph
```

## 📊 Database Schema

### Tables
- **customers**: Customer information
- **products**: Product catalog
- **categories**: Product categories
- **employees**: Sales team
- **orders**: Order transactions
- **order_items**: Line items per order
- **qa_cache**: Cached questions and answers

All tables include proper PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE, and CHECK constraints.

## 🔐 Security

✅ Read-only database access (no UPDATE/DELETE/INSERT)  
✅ Prompt injection protection  
✅ No system prompt leakage  
✅ No API key exposure  
✅ Validator bypass prevention  
✅ Input sanitization  
✅ CORS configuration  

## 💹 Token Optimization

- **Planner**: <100 tokens (compact intent classification)
- **Validator**: <500 tokens (result validation)
- **Response**: <1000 tokens (answer generation)
- **Cache**: Reduces repeated question latency to <50ms

## 📝 Logging

All operations logged with:
- Latency (ms)
- SQL queries executed
- Token usage per agent
- Cache hit/miss
- Validation results
- Retry attempts

Logs available in `./logs/`

## 🛡️ LangSmith Integration

Optional tracing for debugging and monitoring. Set `LANGSMITH_API_KEY` in `.env`.

## 📚 Documentation

- [Architecture Documentation](./docs/ARCHITECTURE.md)
- [Agent Specifications](./docs/AGENTS.md)
- [Database Schema](./docs/DATABASE.md)
- [API Reference](./docs/API.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📄 License

MIT License - see LICENSE file

## 👨‍💼 Support

For issues or questions, please open a GitHub issue or contact the maintainers.
