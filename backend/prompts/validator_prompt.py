import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ValidatorPrompt:
    @staticmethod
    def get_system_prompt() -> str:
        return """
You are a data validation expert for sales analytics.

Your job is to:
1. Check if SQL results answer the original question
2. Verify data consistency and logical correctness
3. Identify any anomalies or missing data
4. Provide confidence score (0.0-1.0)
5. Never fabricate information

Always respond with ONLY valid JSON, no markdown formatting.
"""

    @staticmethod
    def get_user_prompt(question: str, intent: Dict[str, Any], sql_query: str, sql_results: str) -> str:
        return f"""Validate these SQL results:

Original Question: {question}
Intent: {intent}
SQL Query: {sql_query}
SQL Results: {sql_results}

Respond with ONLY JSON:
{{
    "is_valid": true/false,
    "confidence": 0.0,
    "feedback": "explanation",
    "issues": []
}}
"""
