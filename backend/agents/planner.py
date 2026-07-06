import json
import logging
import os
from typing import Dict, Any, Tuple

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class PlannerAgent:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            google_api_key=api_key,
            temperature=0.1,
            max_tokens=300,
        )

        self.prompt = ChatPromptTemplate.from_template(
            """
You are the Planning Agent of an Enterprise Automotive Sales Analytics System.

Your job is ONLY to understand the user's request.

Database Tables

- Brands
- Models
- Dealers
- Customers
- Customer_Ownership
- Car_Vins
- Car_Parts
- Car_Options
- Dealer_Brand
- Manufacture_Plant

Business Meaning

Brands = Vehicle manufacturers

Models = Vehicle models

Customers = Buyers

Customer_Ownership = Vehicle sales

Dealers = Dealerships

Dealer_Brand = Brands sold by dealers

Car_Vins = Individual vehicles

Car_Parts = Vehicle parts

Car_Options = Optional accessories

Manufacture_Plant = Manufacturing plants

Rules

1. Assume every question is about this database.
2. Never reject a question.
3. Determine:
   - business intent
   - tables involved
   - metrics
   - SQL keywords
4. Return JSON ONLY.
5. Do NOT explain anything.
6. Do NOT use Markdown.
7. First character must be {{
8. Last character must be }}

Return EXACTLY this structure:

{{
    "is_relevant": true,
    "intent": "",
    "entities": {{
        "tables": [],
        "filters": {{}},
        "aggregations": []
    }},
    "metrics": [],
    "sql_keywords": [],
    "confidence": 0.95
}}

User Question:

{question}
"""
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def classify(self, question: str) -> Dict[str, Any]:
        """Classify the question and return planner output (no usage tracking)."""
        result, _ = self.classify_with_usage(question)
        return result

    def classify_with_usage(
        self, question: str
    ) -> Tuple[Dict[str, Any], Dict[str, int]]:
        """Classify the question and return (planner_output, token_usage)."""
        try:
            chain    = self.prompt | self.llm
            response = chain.invoke({"question": question})

            logger.info("=" * 80)
            logger.info("RAW GEMINI RESPONSE (Planner)")
            logger.info(response.content)
            logger.info("=" * 80)

            # Extract token usage from metadata
            usage = self._extract_usage(response)

            content = response.content.strip()

            # Strip markdown fences if Gemini wraps the JSON
            for fence in ("```json", "```"):
                if content.startswith(fence):
                    content = content[len(fence):]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            result = json.loads(content)

            result.setdefault("is_relevant", True)
            result.setdefault("intent", "general_analysis")
            result.setdefault(
                "entities",
                {"tables": [], "filters": {}, "aggregations": []},
            )
            result.setdefault("metrics", [])
            result.setdefault("sql_keywords", [])
            result.setdefault("confidence", 0.95)
            result["normalized_question"] = self._normalize_question(question)

            logger.info(
                f"[PLANNER] Intent={result['intent']} | "
                f"Tables={result['entities'].get('tables', [])}"
            )
            return result, usage

        except Exception as e:
            logger.exception("[PLANNER] Planner failed")
            fallback = {
                "is_relevant": True,
                "intent": "general_analysis",
                "entities": {"tables": [], "filters": {}, "aggregations": []},
                "metrics": [],
                "sql_keywords": [],
                "confidence": 0.5,
                "normalized_question": self._normalize_question(question),
            }
            return fallback, {}

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _normalize_question(self, question: str) -> str:
        return question.strip().lower()

    @staticmethod
    def _extract_usage(response) -> Dict[str, int]:
        usage = {}
        try:
            meta = getattr(response, "usage_metadata", None)
            if meta:
                usage["input_tokens"]  = getattr(meta, "input_tokens",  0)
                usage["output_tokens"] = getattr(meta, "output_tokens", 0)
        except Exception:
            pass
        return usage