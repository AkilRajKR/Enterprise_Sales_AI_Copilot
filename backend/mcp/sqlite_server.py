import os
import json
import logging
import sqlite3
from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SQLite MCP Server")

db_path = os.getenv("DATABASE_PATH", "database/sales.db")


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    success: bool
    data: Any = None
    error: str = None


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "SQLite MCP"}


@app.post("/execute")
async def execute_query(request: QueryRequest):
    """Execute READ-ONLY SQL query"""
    try:
        if not request.query.strip().upper().startswith("SELECT"):
            return QueryResponse(success=False, error="Only SELECT queries allowed")
        
        dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "PRAGMA"]
        query_upper = request.query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return QueryResponse(success=False, error=f"Dangerous keyword detected: {keyword}")
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(request.query)
        rows = cursor.fetchall()
        conn.close()
        
        results = [dict(row) for row in rows]
        logger.info(f"Query executed successfully: {len(results)} rows returned")
        
        return QueryResponse(success=True, data=results)
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return QueryResponse(success=False, error=str(e))


@app.get("/schema")
async def get_schema():
    """Get database schema"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        return {"tables": [table[0] for table in tables if table[0]]}
    except Exception as e:
        logger.error(f"Error retrieving schema: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
