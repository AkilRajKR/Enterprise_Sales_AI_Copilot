from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class QueryResponse(BaseModel):
    question: str
    answer: str
    sql_query: str
    evidence: Dict[str, Any]
    confidence: float
    cache_hit: bool
    retry_count: int
    validation_status: str
    execution_time_ms: float
    token_usage: Dict[str, int]


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
