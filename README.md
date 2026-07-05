# Enterprise Sales AI Analytics System

A production-grade multi-agent AI application for sales analytics using LangGraph, LangChain, FastAPI, React, SQLite, and Google Gemini 2.5.

## 🧠 Overview

This system answers natural-language questions over an E-commerce sales database using:
- **Planner Agent**: Classifies and decomposes user questions into structured intent
- **SQL Agent**: Generates and executes safe READ-ONLY queries via MCP
- **Validator Agent**: Ensures SQL results match user intent (with up to 4 retries)
- **Supervisor**: Controls workflow and retry logic (LangGraph state machine)
- **Cache Agent**: Stores and retrieves validated responses (TTL: 24 hours)
- **Response Agent**: Generates business-friendly answers from SQL data

## 🏗️ Architecture

```
┌─────────────────┐
│ User Question   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│ [Planner Agent]                 │
│ Classify & Decompose Intent     │
│ (Gemini 2.5 Flash, <100 tokens) │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Relevance Check     │
│ Sales-related? Y/N  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Cache Lookup                    │
│ TTL: 24 hours                   │
│ ├─ Cache Hit? Return cached     │
│ └─ Cache Miss? Continue ▼       │
└────────┬────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ [SQL Agent via MCP]                  │
│ Generate SELECT Query                │
│ + Injection Protection               │
│ (Gemini 2.5 Flash)                  │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ [Validator Agent]                    │
│ Validate SQL Results                 │
│ (Gemini 2.5 Pro)                    │
│ ├─ Valid? Continue ▼                │
│ └─ Invalid? Retry (max 4)           │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ [Response Agent]                     │
│ Generate Business-Friendly Answer    │
│ (Gemini 2.5 Flash)                  │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Cache Store                          │
│ Save validated response              │
└────────┬─────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ FastAPI Response                │
│ ├─ Answer                       │
│ ├─ SQL Query                    │
│ ├─ Evidence & Confidence        │
│ ├─ Token Usage                  │
│ ├─ Execution Time               │
│ └─ Validation Status            │
└─────────────────────────────────┘
```

## ✅ Features

✅ **Multi-agent orchestration** with LangGraph state machine  
✅ **Semantic question caching** with confidence scoring (TTL-based)  
✅ **Validation-first architecture** with automatic retries (up to 4)  
✅ **Token-optimized prompts** (<100 tokens for Planner)  
✅ **Evidence tracking** for every answer  
✅ **MCP SQLite integration** (READ-ONLY, injection-protected)  
✅ **Comprehensive audit logging** (latency, SQL, tokens, retries)  
✅ **React dashboard** with real-time analytics  
✅ **Docker & Docker Compose** for one-command deployment  
✅ **Unit & integration tests** with pytest  
✅ **Production-ready security controls**  

## 📁 Project Structure

```
Enterprise_Sales_AI_Copilot/
├── backend/
│   ├── agents/
│   │   ├── planner.py          # Planner Agent (intent classification)
│   │   ├── sql_agent.py        # SQL Agent (query generation)
│   │   ├── validator.py        # Validator Agent (result validation)
│   │   ├── response.py         # Response Agent (answer generation)
│   │   ├── cache.py            # Cache Agent (Q&A caching)
│   │   └── __init__.py
│   ├── graph/
│   │   ├── state.py            # SalesState TypedDict
│   │   ├── workflow.py         # LangGraph workflow (8 nodes)
│   │   └── __init__.py
│   ├── prompts/
│   │   ├── planner_prompt.py   # Planner system & user prompts
│   │   ├── validator_prompt.py # Validator prompts
│   │   ├── response_prompt.py  # Response generator prompts
│   │   └── __init__.py
│   ├── mcp/
│   │   ├── sqlite_server.py    # MCP server (port 8001)
│   │   ├── mcp_client.py       # MCP client for agents
│   │   └── __init__.py
│   ├── database/
│   │   ├── schema.py           # SQLite schema + constraints
│   │   ├── seed.py             # Database initialization
│   │   └── __init__.py
│   ├── api/
│   │   ├── main.py             # FastAPI app (port 8000)
│   │   ├── schemas.py          # Pydantic request/response models
│   │   └── __init__.py
│   ├── tests/
│   │   ├── test_agents.py      # Agent unit tests
│   │   ├── test_cache.py       # Cache integration tests
│   │   ├── test_api.py         # API endpoint tests
│   │   └── __init__.py
│   ├── requirements.txt        # Python dependencies
│   └── logs/                   # Application logs (generated)
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API client services
│   │   ├── App.tsx             # Main app component
│   │   └── main.tsx            # Entry point
│   ├── package.json            # Node dependencies
│   ├── vite.config.ts          # Vite configuration
│   └── Dockerfile              # Frontend container
├── Dockerfile.backend          # Backend FastAPI container
├── Dockerfile.mcp              # MCP SQLite server container
├── docker-compose.yml          # Orchestration (3 services)
├── .env.example                # Environment template
├── .gitignore                  # Git exclusions
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- Google Gemini API Key (free tier: https://makersuite.google.com/app/apikey)

### Option 1: Local Development (Recommended)

#### 1️⃣ Clone and Setup Environment
```bash
git clone https://github.com/AkilRajKR/Enterprise_Sales_AI_Copilot.git
cd Enterprise_Sales_AI_Copilot
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your_api_key_here
```

#### 2️⃣ Backend Setup
```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database with e-commerce sales data
python database/seed.py
```

#### 3️⃣ Start MCP Server (Terminal 1)
```bash
cd backend
python mcp/sqlite_server.py
```

Expect: `INFO:     Uvicorn running on http://0.0.0.0:8001`

#### 4️⃣ Start FastAPI Server (Terminal 2)
```bash
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Expect: `INFO:     Uvicorn running on http://0.0.0.0:8000`

#### 5️⃣ Test the Backend
```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the total sales?"}'

# View query history
curl http://localhost:8000/history
```

#### 6️⃣ Frontend Setup (Terminal 3)
```bash
cd frontend
npm install
npm run dev
```

Expect: `Local: http://localhost:5173`

**Frontend is now available at `http://localhost:5173`**

---

### Option 2: Docker Deployment (One Command)

```bash
# Make sure .env is set with GEMINI_API_KEY
docker-compose up -d
```

This starts 3 services:
- **Backend** (FastAPI): http://localhost:8000
- **MCP Server**: http://localhost:8001
- **Frontend** (React): http://localhost:5173

View logs:
```bash
docker-compose logs -f backend
docker-compose logs -f mcp_server
docker-compose logs -f frontend
```

Stop everything:
```bash
docker-compose down
```

---

## 🔗 API Endpoints

### POST `/ask`
Submit a sales question

**Request:**
```json
{
  "question": "What were the total sales in Q1 2024?"
}
```

**Response:**
```json
{
  "question": "What were the total sales in Q1 2024?",
  "answer": "Based on the database, the total sales for Q1 2024 were $245,750.",
  "sql_query": "SELECT SUM(total_amount) FROM orders WHERE strftime('%Y', order_date) = '2024' AND strftime('%m', order_date) IN ('01', '02', '03')",
  "evidence": {
    "total_amount": 245750,
    "order_count": 45
  },
  "confidence": 0.94,
  "cache_hit": false,
  "retry_count": 0,
  "validation_status": "passed",
  "execution_time_ms": 156,
  "token_usage": {
    "planner_input": 45,
    "planner_output": 28,
    "sql_input": 220,
    "sql_output": 12,
    "validator_input": 410,
    "validator_output": 85,
    "response_input": 180,
    "response_output": 32
  }
}
```

### GET `/health`
Health check

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-07-04T12:30:00.000000",
  "version": "1.0.0"
}
```

### GET `/history?limit=50`
Retrieve query history

**Response:**
```json
{
  "total": 12,
  "queries": [
    {
      "id": 1,
      "original_question": "What are total sales?",
      "answer": "Total sales were $50,000",
      "confidence": 0.95,
      "created_at": "2024-07-04T12:20:30"
    }
  ]
}
```

### GET `/schema?admin_key=your_admin_secret_key`
View database schema (admin only)

**Response:**
```json
{
  "tables": [
    "CREATE TABLE customers (...)",
    "CREATE TABLE products (...)",
    "CREATE TABLE orders (...)",
    "..."
  ]
}
```

---

## 🗄️ Database Schema

### Tables

#### customers
- `id` (PK)
- `name`, `email` (UNIQUE), `phone`
- `city`, `country`
- `signup_date`, `created_at`

#### products
- `id` (PK)
- `name`, `price` (CHECK > 0), `stock` (CHECK >= 0)
- `category_id` (FK)
- `description`, `created_at`

#### categories
- `id` (PK)
- `name` (UNIQUE), `description`
- `created_at`

#### employees
- `id` (PK)
- `name`, `email` (UNIQUE), `department`
- `salary` (CHECK > 0), `hire_date`
- `created_at`

#### orders
- `id` (PK)
- `customer_id` (FK), `employee_id` (FK)
- `order_date`, `total_amount` (CHECK >= 0)
- `status` (pending/completed/cancelled)
- `created_at`

#### order_items
- `id` (PK)
- `order_id` (FK), `product_id` (FK)
- `quantity` (CHECK > 0), `unit_price` (CHECK > 0)
- `subtotal` (CHECK > 0), `created_at`

#### qa_cache
- `id` (PK)
- `normalized_question` (UNIQUE)
- `original_question`, `sql_query`
- `answer`, `evidence`, `confidence`
- `execution_time_ms`, `token_usage`
- `created_at`, `updated_at`

---

## 🧪 Testing

### Run All Tests
```bash
cd backend
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ -v --cov=agents --cov=graph --cov=api
```

### Run Specific Test
```bash
pytest tests/test_agents.py -v
pytest tests/test_cache.py -v
pytest tests/test_api.py -v
```

---
```bash
cd backend
pip install -r requirements.txt
python database/seed.py

```
## 🔒 Security

✅ **Read-only database access** (no UPDATE/DELETE/INSERT)  
✅ **SQL injection protection** (dangerous keywords blocked)  
✅ **Prompt injection protection** (input validation)  
✅ **No system prompt leakage**  
✅ **No API key exposure** (.env isolation)  
✅ **Validator bypass prevention** (mandatory validation)  
✅ **CORS configuration** (frontend origin allowed)  
✅ **Admin endpoint protection** (secret key required)  

---

## 📊 Token Optimization

| Agent | Model | Max Tokens | Typical Usage |
|-------|-------|------------|---------------|
| Planner | Gemini 2.5 Flash | 100 | 45-60 |
| SQL Agent | Gemini 2.5 Flash | 500 | 220-280 |
| Validator | Gemini 2.5 Pro | 500 | 410-480 |
| Response | Gemini 2.5 Flash | 1000 | 180-250 |
| **Per Query** | **~2100** | **~1000** | |

**Cache Hit**: <50ms (no LLM calls)

---

## 📝 Logging

Logs stored in `backend/logs/`

Metrics logged:
- **Latency** (ms per request)
- **SQL queries** (for audit)
- **Token usage** (per agent)
- **Cache hits/misses**
- **Validation results**
- **Retry attempts**

---

## 🔄 Workflow State Machine

The LangGraph workflow has 8 nodes:

1. **plan** → Classify question and decompose intent
2. **relevance_check** → Accept/reject non-sales questions
3. **cache_lookup** → Check cache for existing answer
4. **sql_generation** → Generate SELECT query
5. **sql_execution** → Execute query via MCP
6. **validation** → Validate results against intent
7. **generate_response** → Create business-friendly answer
8. **cache_store** → Store validated response

**Retry Logic**: If validation fails, retry sql_generation up to 4 times.

---

## 🛠️ Configuration

Edit `.env` to customize:

```env
# Gemini API
GEMINI_API_KEY=your_key

# Database
DATABASE_PATH=./database/sales.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Cache
CACHE_TTL_HOURS=24
MAX_CACHE_SIZE=1000

# Retries
MAX_RETRIES=4

# Token Limits
PLANNER_MAX_TOKENS=100
VALIDATOR_MAX_TOKENS=500
RESPONSE_MAX_TOKENS=1000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Security
ADMIN_SECRET_KEY=your_secret
```

---

## 📈 Sample Questions to Try

1. "What are total sales?"
2. "How many orders were placed in the last month?"
3. "Which product had the most sales?"
4. "What is the average order value?"
5. "Show me sales by category"
6. "How many customers do we have?"
7. "What was the revenue for employee named John?"
8. "List top 5 selling products"
9. "What is the customer retention rate?"
10. "Show me sales trend over time"

---

## 🐛 Troubleshooting

### Issue: "Gemini API key not found"
**Solution**: Set `GEMINI_API_KEY` in `.env` file

### Issue: "MCP server connection failed"
**Solution**: Ensure MCP server is running on port 8001
```bash
curl http://localhost:8001/health
```
## 🗄️ Database: SQLite

### Why SQLite?
- ✅ Zero-configuration (no server needed)
- ✅ Single file database (easy backup/versioning)
- ✅ Perfect for development & production
- ✅ Full support for foreign keys & constraints
- ✅ Read-only access via MCP (secure)

### Database Initialization

```bash
cd backend
python database/seed.py
```
### Issue: "Database not initialized"
**Solution**: Run seed script
```bash
cd backend
python database/seed.py
```

### Issue: "CORS error in frontend"
**Solution**: Add your frontend origin to `CORS_ORIGINS` in `.env`

### Issue: "Port already in use"
**Solution**: Change port in `.env` or kill existing process
```bash
lsof -i :8000  # Find process
kill -9 <PID>  # Kill it
```

---

## 📚 Documentation

- [Architecture Guide](./docs/ARCHITECTURE.md) *(coming soon)*
- [Agent Specifications](./docs/AGENTS.md) *(coming soon)*
- [Database Design](./docs/DATABASE.md) *(coming soon)*
- [API Reference](./docs/API.md) *(coming soon)*
- [Deployment Guide](./docs/DEPLOYMENT.md) *(coming soon)*

---

## 🤝 Contributing

Contributions welcome!

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m 'feat: description'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see LICENSE file

---

## 💬 Support

For issues or questions:
- Open a GitHub issue
- Check [Troubleshooting](#-troubleshooting) section
- Contact maintainers

---

## 🙏 Acknowledgments

- Google Gemini 2.5 models
- LangGraph & LangChain
- FastAPI & Uvicorn
- React & Vite
- SQLite

---

**Last Updated**: July 4, 2024  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
