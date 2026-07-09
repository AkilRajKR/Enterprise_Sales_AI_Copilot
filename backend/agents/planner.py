import json
import logging
import os
from typing import Dict, Any, Tuple

from langchain_core.prompts import ChatPromptTemplate
from agents.llm_factory import invoke_with_fallback

logger = logging.getLogger(__name__)


class PlannerAgent:
    def __init__(self, api_key: str):
        self.api_key    = api_key
        self.temperature = 0.1
        self.max_tokens  = int(os.getenv("PLANNER_MAX_TOKENS", 400))

        self.prompt = ChatPromptTemplate.from_template(
            """
You are the Planning Agent of an Enterprise Automotive Sales Analytics System.

Your ONLY job is to classify the user's question.

=== AVAILABLE DATABASE TABLES ===
- Brands            (vehicle manufacturers)
- Models            (vehicle models per brand)
- Dealers           (dealerships)
- Customers         (buyers — NO personal data like name, DOB, salary)
- Customer_Ownership (completed vehicle sales)
- Car_Vins          (individual vehicles)
- Car_Parts         (vehicle parts)
- Car_Options       (optional accessories)
- Dealer_Brand      (brands available at dealers)
- Manufacture_Plant (manufacturing plants)

=== STRICT RULES — READ CAREFULLY ===

RULE 1 — NEVER ASSUME:
  If the question is vague, ambiguous, or you are not 100% sure what data is needed,
  set "needs_clarification": true and fill "clarification_questions" with 1–3 short
  plain-English questions that will help you understand exactly what the user wants.
  DO NOT guess. DO NOT invent intent.

RULE 2 — NO PERSONAL DATA:
  If the question asks for individual personal details (customer name, DOB, address,
  salary, phone, email, passport, bank info), set "is_relevant": false and
  "rejection_reason": "privacy".

RULE 3 — SCOPE:
  Only answer questions about automotive sales, brands, models, dealers, vehicles,
  manufacturing. If totally off-topic (e.g. weather, recipes), set "is_relevant": false
  and "rejection_reason": "off_topic".

RULE 4 — FORMAT:
  Return JSON ONLY. No markdown. No explanation.
  First character must be {{ and last must be }}.

=== CLARIFICATION EXAMPLES ===
Question: "show me the data"
→ needs_clarification: true, questions: ["Which data would you like to see — brands, models, dealers, or sales?", "Do you want totals or a breakdown by a specific category?"]

Question: "how is it performing?"
→ needs_clarification: true, questions: ["Which entity are you asking about — a specific brand, model, or dealer?", "What time period should I look at?"]

Question: "give me everything"
→ needs_clarification: true, questions: ["Everything is a very broad request. Could you specify which area — sales counts, dealer rankings, brand performance?"]

=== OUTPUT SCHEMA ===
{{
    "is_relevant": true,
    "needs_clarification": false,
    "clarification_questions": [],
    "rejection_reason": "",
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
            response, _model = invoke_with_fallback(
                chain_builder=lambda llm: self.prompt | llm,
                invoke_kwargs={"question": question},
                api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            logger.info("=" * 80)
            logger.info("RAW GEMINI RESPONSE (Planner)")
            logger.info(response.content)
            logger.info("=" * 80)

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
            result.setdefault("needs_clarification", False)
            result.setdefault("clarification_questions", [])
            result.setdefault("rejection_reason", "")
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
                f"NeedsClarification={result['needs_clarification']} | "
                f"Tables={result['entities'].get('tables', [])}"
            )
            return result, usage

        except Exception as e:
            logger.exception("[PLANNER] Planner failed")
            # On LLM failure do NOT assume — ask for clarification
            fallback = {
                "is_relevant": True,
                "needs_clarification": True,
                "clarification_questions": [
                    "I had trouble understanding your question. Could you rephrase it?",
                    "Please be specific about which data you want — e.g. brand, model, dealer, or sales count.",
                ],
                "rejection_reason": "",
                "intent": "unknown",
                "entities": {"tables": [], "filters": {}, "aggregations": []},
                "metrics": [],
                "sql_keywords": [],
                "confidence": 0.0,
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