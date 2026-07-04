import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from graph.workflow import create_sales_workflow
from api.schemas import QuestionRequest, QueryResponse, HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enterprise Sales AI Analytics",
    description="Multi-agent AI system for sales analytics",
    version="1.0.0"
)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow = None


@app.on_event("startup")
async def startup_event():
    global workflow
    try:
        workflow = create_sales_workflow()
        logger.info("Sales workflow initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing workflow: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QuestionRequest):
    """Submit a sales question to the AI system"""
    if not workflow:
        raise HTTPException(status_code=500, detail="Workflow not initialized")
    
    try:
        logger.info(f"Processing question: {request.question}")
        
        result = workflow.invoke({
            "user_question": request.question,
            "retry_count": 0
        })
        
        response = QueryResponse(
            question=result.get("user_question", ""),
            answer=result.get("final_answer", "No answer generated"),
            sql_query=result.get("sql_query", ""),
            evidence=result.get("evidence", {}),
            confidence=result.get("confidence", 0.0),
            cache_hit=result.get("cache_hit", False),
            retry_count=result.get("retry_count", 0),
            validation_status="passed" if result.get("validation_status") else "failed",
            execution_time_ms=result.get("execution_time_ms", 0),
            token_usage=result.get("token_usage", {})
        )
        
        logger.info(f"Question processed successfully: {response.confidence}")
        return response
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history(limit: int = Query(50, ge=1, le=100)):
    """Retrieve query history"""
    try:
        from agents.cache import CacheAgent
        db_path = os.getenv("DATABASE_PATH", "database/sales.db")
        cache = CacheAgent(db_path)
        history = cache.get_history(limit)
        return {"total": len(history), "queries": history}
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schema")
async def get_schema(admin_key: str = Query(None)):
    """Get database schema (admin only)"""
    if admin_key != os.getenv("ADMIN_SECRET_KEY", "admin"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        import sqlite3
        db_path = os.getenv("DATABASE_PATH", "database/sales.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        return {"tables": [table[0] for table in tables if table[0]]}
    except Exception as e:
        logger.error(f"Error retrieving schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("API_DEBUG", "False") == "True"
    )
