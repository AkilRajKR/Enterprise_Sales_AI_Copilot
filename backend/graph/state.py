from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class SalesState(TypedDict, total=False):
    user_question: str
    planner_output: Dict[str, Any]
    is_relevant: bool
    cache_hit: bool
    cached_answer: Optional[Dict[str, Any]]
    sql_query: str
    sql_result: List[Dict[str, Any]]
    validation_status: bool
    validation_feedback: str
    retry_count: int
    final_answer: str
    evidence: Dict[str, Any]
    confidence: float
    token_usage: Dict[str, int]
    execution_time_ms: float
    timestamp: datetime
