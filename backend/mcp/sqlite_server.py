import os
import logging
import sqlite3
import socket
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SQLite MCP Server")

# Resolve db_path relative to this file so it works from any cwd
_here   = Path(__file__).resolve().parent.parent  # backend/
db_path = os.getenv("DATABASE_PATH", str(_here / "database" / "sales.db"))


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    success: bool
    data: Any = None
    error: str = None


DANGEROUS_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT",
    "ALTER", "TRUNCATE", "PRAGMA", "ATTACH", "DETACH",
]


def _find_free_port(preferred: int = 8001) -> int:
    """Return `preferred` if free, else find the next available port."""
    for port in range(preferred, preferred + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free port found in range 8001-8020")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "SQLite MCP", "db_path": db_path}


@app.post("/execute", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """Execute a READ-ONLY SQL query."""
    query = request.query.strip()

    if not query.upper().startswith("SELECT"):
        return QueryResponse(success=False, error="Only SELECT queries are allowed")

    query_upper = query.upper()
    for kw in DANGEROUS_KEYWORDS:
        if kw in query_upper:
            return QueryResponse(success=False, error=f"Dangerous keyword detected: {kw}")

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        results = [dict(row) for row in rows]
        logger.info(f"[MCP] Query OK — {len(results)} rows returned")
        return QueryResponse(success=True, data=results)

    except Exception as e:
        logger.error(f"[MCP] Error executing query: {e}")
        return QueryResponse(success=False, error=str(e))


@app.get("/schema")
async def get_schema():
    """Return all CREATE TABLE statements from the database."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            rows = cursor.fetchall()

        return {"tables": [{"name": r[0], "sql": r[1]} for r in rows if r[1]]}

    except Exception as e:
        logger.error(f"[MCP] Error retrieving schema: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = _find_free_port(8001)
    if port != 8001:
        logger.warning(f"Port 8001 was in use — using port {port} instead")
    logger.info(f"Starting MCP SQLite server on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
