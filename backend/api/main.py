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

# ── Lifespan ─────────────────────────────────────────────────────────────────
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
    "http://localhost:3000,http://localhost:5173,http://localhost:5174"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Error classifier ──────────────────────────────────────────────────────────
def _friendly_error(err: Exception, elapsed_ms: float, question: str) -> QueryResponse:
    """Convert any exception into a human-readable QueryResponse (200 OK)."""
    err_str = str(err).lower()

    if "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str:
        msg = (
            "The AI model has reached its hourly or daily request limit. "
            "This is a free-tier quota restriction that resets automatically.\n\n"
            "What you can do right now:\n"
            "• Wait a few minutes and try again — the limit resets shortly\n"
            "• Try a shorter or simpler question\n"
            "• Recently answered questions are cached, so try a popular query\n\n"
            "Your question is perfectly valid. The system will be back to normal soon."
        )
        vstatus = "quota_exceeded"

    elif "timeout" in err_str or "timed out" in err_str or "read timeout" in err_str:
        msg = (
            "The AI took too long to process your question.\n\n"
            "This usually happens with very complex multi-table queries. Try:\n"
            "• Asking a more focused question (e.g., one brand or one time period)\n"
            "• Breaking it into two simpler questions\n"
            "• Retrying in a moment — the service may be under load"
        )
        vstatus = "timeout"

    elif "connection" in err_str or "network" in err_str or "unreachable" in err_str or "refused" in err_str:
        msg = (
            "Cannot connect to the AI service right now.\n\n"
            "Possible causes:\n"
            "• The backend server is not running — restart it with start_backend.ps1\n"
            "• Network connectivity issue\n"
            "• The API service is temporarily down\n\n"
            "Please check that the server is running and try again."
        )
        vstatus = "connection_error"

    elif "api key" in err_str or "api_key" in err_str or "authentication" in err_str or "unauthorized" in err_str or "invalid api" in err_str:
        msg = (
            "The AI service API key is invalid or has expired.\n\n"
            "This is a configuration issue. Please contact your administrator "
            "to update the GEMINI_API_KEY in the .env file."
        )
        vstatus = "auth_error"

    elif "sql" in err_str and ("syntax" in err_str or "error" in err_str):
        msg = (
            "The system generated a database query that could not be executed.\n\n"
            "Try rephrasing your question with more specific terms. For example:\n"
            "• Instead of 'show me everything', ask 'which brand has the most customers?'\n"
            "• Use clear business terms like brand, model, dealer, or sales"
        )
        vstatus = "sql_error"

    else:
        msg = (
            "An unexpected issue occurred while processing your request.\n\n"
            "The system is otherwise working normally. Please:\n"
            "• Click 'New Query' to reset the conversation\n"
            "• Rephrase your question and try again\n"
            "• If the problem continues, restart the backend server"
        )
        vstatus = "system_error"

    return QueryResponse(
        question=question,
        answer=msg,
        sql_query="",
        evidence={},
        confidence=0.0,
        cache_hit=False,
        retry_count=0,
        validation_status=vstatus,
        execution_time_ms=elapsed_ms,
        token_usage={},
        privacy_blocked=False,
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
        return _friendly_error(
            Exception("workflow not initialized"),
            0.0,
            request.question,
        )

    start = time.perf_counter()

    try:
        logger.info("=" * 80)
        logger.info(f"Processing Question: {request.question}")
        logger.info("=" * 80)

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

        final_answer = result.get("final_answer", "")

        # ── Determine the semantic status of the response ─────────────────────
        if result.get("privacy_blocked"):
            vstatus = "privacy_blocked"
        elif result.get("planner_output", {}).get("needs_clarification"):
            vstatus = "needs_clarification"
        elif result.get("planner_output", {}).get("rejection_reason") == "off_topic":
            vstatus = "off_topic"
        elif (
            "I need" in final_answer and "clarif" in final_answer.lower()
            or "CLARIFICATION_NEEDED" in final_answer
        ):
            vstatus = "needs_clarification"
        elif result.get("validation_status"):
            vstatus = "passed"
        else:
            vstatus = "failed"

        return QueryResponse(
            question=result.get("user_question", ""),
            answer=final_answer,
            sql_query=result.get("sql_query", ""),
            evidence=result.get("evidence", {}),
            confidence=result.get("confidence", 0.0),
            cache_hit=result.get("cache_hit", False),
            retry_count=result.get("retry_count", 0),
            validation_status=vstatus,
            execution_time_ms=round(result.get("execution_time_ms", 0), 2),
            token_usage=result.get("token_usage", {}),
            privacy_blocked=result.get("privacy_blocked", False),
        )

    except Exception as e:
        logger.exception("Workflow Execution Failed")
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        return _friendly_error(e, elapsed_ms, request.question)


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
        port=8002,
        reload=True,
    )
