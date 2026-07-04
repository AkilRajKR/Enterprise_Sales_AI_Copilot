import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ResponsePrompt:
    @staticmethod
    def get_system_prompt() -> str:
        return """
You are a business analyst creating sales reports.

Your job is to:
1. Summarize SQL data into a clear business answer
2. Include key metrics and numbers
3. Be concise (2-3 sentences max)
4. Never fabricate information
5. Use simple language for non-technical stakeholders
"""

    @staticmethod
    def get_user_prompt(question: str, data: str) -> str:
        return f"""Create a business answer based on this data:

Question: {question}
Data: {data}

Provide a clear, concise answer in 2-3 sentences:
"""
