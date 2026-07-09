import logging
import os
from typing import Dict, Any, List, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from agents.llm_factory import invoke_with_fallback, extract_text_content
import json

logger = logging.getLogger(__name__)


class ValidatorAgent:
    def __init__(self, api_key: str):
        self.api_key     = api_key
        self.temperature = 0.0
        self.max_tokens  = int(os.getenv("VALIDATOR_MAX_TOKENS", 500))

        self.prompt = ChatPromptTemplate.from_template("""
You are a data validation expert for an Automotive Sales Business.

Validate that the SQL results correctly answer the user's question:

Original Question: {question}

Planned Intent:
- Type: {intent}
- Entities: {entities}
- Metrics: {metrics}

SQL Query: {sql_query}

SQL Results (first 10 rows):
{sql_results}

Validate:
1. Do the results answer the question?
2. Are the metrics correct?
3. Are the data values reasonable?
4. Is the data logically consistent?
5. Are there missing rows or anomalies?

Provide confidence score (0.0-1.0) for validity.

Respond with ONLY valid JSON (no markdown fences):
{{
    "is_valid": true,
    "confidence": 0.85,
    "feedback": "clear explanation",
    "issues": []
}}
""")

        self.parser = JsonOutputParser()

    # ── Public API ────────────────────────────────────────────────────────────

    def validate(
        self,
        question: str,
        intent: Dict[str, Any],
        sql_query: str,
        sql_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Validate results (no usage tracking — backward compat)."""
        result, _ = self.validate_with_usage(question, intent, sql_query, sql_results)
        return result

    def validate_with_usage(
        self,
        question: str,
        intent: Dict[str, Any],
        sql_query: str,
        sql_results: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, Any], Dict[str, int]]:
        """Validate results and return (validation_dict, token_usage)."""
        try:
            # Format results safely before building the invoke kwargs
            preview     = sql_results[:10]
            extra       = len(sql_results) - 10
            results_str = json.dumps(preview, default=str)
            if extra > 0:
                results_str += f"\n(... and {extra} more rows)"

            raw_response, _model = invoke_with_fallback(
                chain_builder=lambda llm: self.prompt | llm,
                invoke_kwargs={
                    "question":    question,
                    "intent":      intent.get("intent", "unknown"),
                    "entities":    intent.get("entities", {}),
                    "metrics":     intent.get("metrics", []),
                    "sql_query":   sql_query,
                    "sql_results": results_str[:2000],
                },
                api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            usage   = self._extract_usage(raw_response)
            content = extract_text_content(raw_response)

            # Strip markdown fences if present
            for fence in ("```json", "```"):
                if content.startswith(fence):
                    content = content[len(fence):]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            validation = json.loads(content)

            logger.info(
                f"[VALIDATOR] valid={validation.get('is_valid')}, "
                f"confidence={validation.get('confidence')}"
            )
            return validation, usage

        except Exception as e:
            logger.error(f"[VALIDATOR] Error: {e}")
            return {
                "is_valid":   False,
                "confidence": 0.0,
                "feedback":   f"Validation error: {str(e)}",
                "issues":     ["Validation failed"],
            }, {}

    # ── Helpers ───────────────────────────────────────────────────────────────

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
