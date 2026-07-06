import os
import time
import logging
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from pathlib import Path

# ── Load .env from project root regardless of cwd ────────────────────────────
_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=_root / ".env")

from graph.workflow import create_sales_workflow
from api.schemas import QuestionRequest, QueryResponse, HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Lifespan (replaces deprecated @app.on_event) ─────────────────────────────
workflow = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global workflow
    logger.info("=" * 80)
    logger.info("Initializing Enterprise Sales AI Workflow...")
    try:
        workflow = create_sales_workflow()
        logger.info("Sales workflow initialized successfully")
    except Exception:
        logger.exception("Workflow initialization failed")
        raise
    logger.info("=" * 80)
    yield
    # Shutdown cleanup (if needed)
    logger.info("Shutting down Enterprise Sales AI...")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Enterprise Sales AI Analytics",
    description="Multi-agent AI system for automotive sales analytics",
    version="1.0.0",
    lifespan=lifespan,
)

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
    )


@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QuestionRequest):
    global workflow

    if workflow is None:
        raise HTTPException(status_code=500, detail="Workflow not initialized")

    try:
        logger.info("=" * 80)
        logger.info(f"Processing Question: {request.question}")
        logger.info("=" * 80)

        start = time.perf_counter()

        initial_state = {
            "user_question":      request.question,
            "planner_output":     {},
            "is_relevant":        False,
            "cache_hit":          False,
            "cached_answer":      None,
            "sql_query":          "",
            "sql_result":         [],
            "validation_status":  False,
            "validation_feedback": "",
            "retry_count":        0,
            "final_answer":       "",
            "evidence":           {},
            "confidence":         0.0,
            "token_usage":        {},
            "execution_time_ms":  0.0,
            "timestamp":          datetime.utcnow(),
        }

        result = workflow.invoke(initial_state)

        result["execution_time_ms"] = (time.perf_counter() - start) * 1000

        logger.info("=" * 80)
        logger.info("Workflow Finished")
        logger.info(f"Answer: {str(result.get('final_answer', ''))[:200]}")
        logger.info("=" * 80)

        return QueryResponse(
            question=result.get("user_question", ""),
            answer=result.get("final_answer", ""),
            sql_query=result.get("sql_query", ""),
            evidence=result.get("evidence", {}),
            confidence=result.get("confidence", 0.0),
            cache_hit=result.get("cache_hit", False),
            retry_count=result.get("retry_count", 0),
            validation_status=(
                "passed" if result.get("validation_status") else "failed"
            ),
            execution_time_ms=round(result.get("execution_time_ms", 0), 2),
            token_usage=result.get("token_usage", {}),
        )

    except Exception as e:
        logger.exception("Workflow Execution Failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history(limit: int = Query(50, ge=1, le=100)):
    """Retrieve query history from cache."""
    try:
        from agents.cache import CacheAgent
        db_path = os.getenv("DATABASE_PATH", "database/sales.db")
        cache   = CacheAgent(db_path)
        history = cache.get_history(limit)
        return {"total": len(history), "queries": history}
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schema")
async def get_schema(admin_key: str = Query(None)):
    """Get database schema (admin only)."""
    if admin_key != os.getenv("ADMIN_SECRET_KEY", "admin"):
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        db_path = os.getenv("DATABASE_PATH", "database/sales.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

        return {"tables": [t[0] for t in tables if t[0]]}

    except Exception as e:
        logger.error(f"Error retrieving schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
