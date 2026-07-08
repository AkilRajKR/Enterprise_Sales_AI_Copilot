# Enterprise Sales AI Analytics System

A production-grade multi-agent AI application for automotive sales analytics using LangGraph, LangChain, FastAPI, React, SQLite, and Google Gemini models.

## 🧠 Overview

This system answers natural-language questions over an **Automotive Sales Database** using:
- **Planner Agent**: Classifies and decomposes user questions into structured intent.
- **SQL Agent**: Generates and executes safe READ-ONLY queries via MCP.
- **Validator Agent**: Ensures SQL results match user intent (with up to 4 retries).
- **Supervisor**: Controls workflow and retry logic (LangGraph state machine).
- **Cache Agent**: Stores and retrieves validated responses (TTL: 24 hours), avoiding error caching.
- **Response Agent**: Generates business-friendly answers from SQL data.

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
│ (Configured Gemini Model)       │
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
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ [Validator Agent]                    │
│ Validate SQL Results                 │
│ ├─ Valid? Continue ▼                │
│ └─ Invalid? Retry (max 4)           │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ [Response Agent]                     │
│ Generate Business-Friendly Answer    │
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
✅ **Dynamic Model Support** (Configurable via `GEMINI_MODEL` env var)  
✅ **MCP SQLite integration** (READ-ONLY, injection-protected, auto port discovery)  
✅ **Comprehensive audit logging** (latency, SQL, tokens, retries)  
✅ **React dashboard** with real-time analytics  
✅ **Automated startup script** (`start_backend.ps1` for easy deployment)  

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
│   │   ├── sqlite_server.py    # MCP server (Auto port discovery)
│   │   ├── mcp_client.py       # MCP client for agents
│   │   └── __init__.py
│   ├── database/
│   │   ├── schema.py           # SQLite schema (Automotive data)
│   │   ├── seed.py             # Database initialization
│   │   └── __init__.py
│   ├── api/
│   │   ├── main.py             # FastAPI app (port 8000)
│   │   ├── schemas.py          # Pydantic request/response models
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
├── start_backend.ps1           # Automated script for backend startup
├── .env.example                # Environment template
├── .gitignore                  # Git exclusions
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Google Gemini API Key (free tier: https://aistudio.google.com/app/apikey)

### 1️⃣ Clone and Setup Environment
```bash
git clone https://github.com/AkilRajKR/Enterprise_Sales_AI_Copilot.git
cd Enterprise_Sales_AI_Copilot
cp .env.example .env
```

Edit `.env` and add your Gemini API key and preferred model:
```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.1-pro-preview
```

### 2️⃣ Backend Setup & Database Initialization
```bash
cd backend
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database with automotive sales data
python database/seed.py
```

### 3️⃣ Start Backend with Automated Script (Windows)
We have a convenient PowerShell script that handles killing old ghost processes and starting both the MCP server and FastAPI backend automatically.
```powershell
cd ..
.\start_backend.ps1
```
*Note: The script starts the FastAPI backend on port 8000. The MCP server port is auto-discovered starting from 8001.*

### 4️⃣ Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

**Frontend is now available at `http://localhost:5173`**

---

## 🔗 API Endpoints

### POST `/ask`
Submit a sales question

**Request:**
```json
{
  "question": "Which brand has the most customers?"
}
```

**Response:**
```json
{
  "question": "Which brand has the most customers?",
  "answer": "Based on our data, Toyota has the most customers, totaling 15,200.",
  "sql_query": "SELECT Brands.name, COUNT(Customers.customer_id) ...",
  "evidence": {
    "name": "Toyota",
    "customer_count": 15200
  },
  "confidence": 0.94,
  "cache_hit": false,
  "retry_count": 0,
  "validation_status": "passed",
  "execution_time_ms": 450,
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

---

## 🗄️ Database Schema (Automotive Sales)

### Tables

#### Brands
- `brand_id` (PK)
- `name` (UNIQUE), `country_of_origin`, `established_year`

#### Models
- `model_id` (PK)
- `brand_id` (FK), `name`, `type` (SUV, Sedan, etc.), `base_price`

#### Customers
- `customer_id` (PK)
- `first_name`, `last_name`, `email`, `phone`, `city`, `state`

#### Dealers
- `dealer_id` (PK)
- `name`, `location`, `rating`

#### Vehicles
- `vehicle_id` (PK)
- `model_id` (FK), `vin` (UNIQUE), `color`, `manufacturing_year`, `status`

#### Manufacturing_Plants
- `plant_id` (PK)
- `name`, `location`, `capacity`

#### Sales
- `sale_id` (PK)
- `vehicle_id` (FK), `customer_id` (FK), `dealer_id` (FK)
- `sale_date`, `sale_price`

#### QA_Cache
- `id` (PK)
- `normalized_question` (UNIQUE), `original_question`, `sql_query`
- `answer`, `evidence`, `confidence`, `execution_time_ms`, `token_usage`
- `created_at`, `updated_at`

---

## 🔒 Security

✅ **Read-only database access** (no UPDATE/DELETE/INSERT)  
✅ **SQL injection protection** (dangerous keywords blocked)  
✅ **Prompt injection protection** (input validation)  
✅ **No system prompt leakage**  
✅ **No API key exposure** (.env isolation)  
✅ **Validator bypass prevention** (mandatory validation)  
✅ **CORS configuration** (frontend origin allowed)  

---

## 🛠️ Configuration

Edit `.env` to customize:

```env
# Gemini API
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-3.1-pro-preview

# Database
DATABASE_URL=sqlite:///./sales.db
DATABASE_PATH=database/sales.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Cache
CACHE_TTL_HOURS=24
MAX_CACHE_SIZE=1000

# Retries
MAX_RETRIES=4

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 📈 Sample Questions to Try

1. "Which brand has the most customers?"
2. "How many orders were placed in the last month?"
3. "Which vehicle model had the most sales?"
4. "What is the average vehicle price?"
5. "Show me sales by brand"
6. "How many customers do we have in total?"
7. "List top 5 selling models"
8. "Show me the sales trend over time"

---

## 🐛 Troubleshooting

### Issue: "Network Error" on Frontend
**Solution**: This happens if the Gemini API exhausts its free tier quota and the backend crashes. Ensure `GEMINI_MODEL` is set to an available model with adequate quota in `.env` (like `gemini-3.1-pro-preview`), and restart the backend.

### Issue: "Port already in use" (10048 Error)
**Solution**: Windows often leaves ports in `TIME_WAIT`. The `start_backend.ps1` script handles this by discovering available ports, or use it to kill stale processes.

---

**Last Updated**: July 2026  
**Version**: 2.0.0  
**Status**: ✅ Production Ready
