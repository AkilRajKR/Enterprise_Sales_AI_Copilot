import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PlannerPrompt:
    @staticmethod
    def get_system_prompt() -> str:
        return """
You are an expert sales question classifier for an e-commerce analytics system.

Your job is to:
1. Determine if the question is about sales/revenue (answer 'true') or not (answer 'false')
2. Classify the intent: revenue_analysis, customer_analysis, product_analysis, employee_analysis, or other
3. Extract key entities (products, dates, regions, metrics)
4. Identify required metrics
5. Provide confidence score (0.0-1.0)

Always respond with ONLY valid JSON, no markdown formatting.
"""

    @staticmethod
    def get_user_prompt(question: str) -> str:
        return f"""Classify this sales question:

Question: {question}

Respond with ONLY JSON:
{{
    "is_relevant": true/false,
    "intent": "intent_type",
    "entities": {{}},
    "metrics": [],
    "confidence": 0.0
}}
"""
