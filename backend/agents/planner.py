import json
import logging
import os
from typing import Dict, Any, Tuple

from langchain_core.prompts import ChatPromptTemplate
from agents.llm_factory import invoke_with_fallback, extract_text_content

logger = logging.getLogger(__name__)


class PlannerAgent:
    def __init__(self, api_key: str):
        self.api_key    = api_key
        self.temperature = 0.1
        self.max_tokens  = int(os.getenv("PLANNER_MAX_TOKENS", 400))

        self.prompt = ChatPromptTemplate.from_template(
            """
You are the Planning Agent of an Enterprise Automotive Sales Analytics System.
Your job is to classify the user question and return a JSON plan.

=== DATABASE TABLES ===
- Brands            (vehicle manufacturers / car makes)
- Models            (vehicle models per brand)
- Dealers           (dealerships)
- Customers         (buyers — counts only, NO personal data)
- Customer_Ownership (completed vehicle sales)
- Car_Vins          (individual vehicles)
- Car_Parts         (vehicle parts)
- Car_Options       (optional accessories)
- Dealer_Brand      (brands available at dealers)
- Manufacture_Plant (manufacturing plants)

=== DECISION: needs_clarification ===

Set needs_clarification: FALSE for these (they are CLEAR questions):
- Counting entities: "how many customers", "how many vehicles", "how many dealers"
- Ranking: "which brand has the most", "which dealer sold the most", "top 5 plants"
- Aggregation: "total sales", "most popular", "highest sales volume"
- Listing: "show me all brands", "list all models", "what options are available"
- Any question with a clear entity (brand/model/dealer/customer/vehicle/plant/option/part)
  AND a clear metric (count/total/most/highest/lowest/average/list)

Set needs_clarification: TRUE ONLY if the question has NO clear entity AND NO clear metric:
- "show me the data" -> no entity, no metric
- "how is it performing?" -> no entity specified
- "give me everything" -> too vague
- "what do you have?" -> unclear scope
- "show me something interesting" -> no focus

=== PRIVACY RULE ===
Personal identifiers (name, DOB, salary, phone, email, address, SSN, credit card)
-> set is_relevant: false, rejection_reason: "privacy"

=== SCOPE RULE ===
Non-automotive, non-sales topics (weather, recipes, geography, sports)
-> set is_relevant: false, rejection_reason: "off_topic"

=== OUTPUT RULES ===
- Return JSON ONLY. No markdown. No explanation.
- First character must be {{ and last must be }}

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
        result, _ = self.classify_with_usage(question)
        return result

    def classify_with_usage(
        self, question: str
    ) -> Tuple[Dict[str, Any], Dict[str, int]]:
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
            # Extract token usage from metadata
            usage = self._extract_usage(response)

            content = extract_text_content(response)

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
                f"Rejection={result['rejection_reason']} | "
                f"Tables={result['entities'].get('tables', [])}"
            )
            return result, usage

        except Exception as e:
            logger.exception("[PLANNER] Planner failed — using fallback (no assumption)")
            # On LLM failure do NOT assume — ask for clarification
            fallback = {
                "is_relevant": True,
                "needs_clarification": True,
                "clarification_questions": [
                    "I had trouble understanding your question. Could you rephrase it?",
                    "Please specify which data you want: brand, model, dealer, customer count, or sales.",
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