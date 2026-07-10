import logging
import os
from typing import Dict, Any, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.llm_factory import invoke_with_fallback, extract_text_content

logger = logging.getLogger(__name__)


class ResponseAgent:
    def __init__(self, api_key: str):
        self.api_key     = api_key
        self.temperature = 0.2
        self.max_tokens  = int(os.getenv("RESPONSE_MAX_TOKENS", 800))

        self.prompt = ChatPromptTemplate.from_template("""
You are an Automotive Sales Business Analyst writing responses for non-technical stakeholders.

Question asked: {question}
Data returned from the database: {data}

=== STRICT RULES — NEVER VIOLATE ===

RULE 1 — NEVER ASSUME OR INVENT DATA:
  Only use numbers and facts that are present in the Data section above.
  If the data is empty or missing, tell the user clearly what is missing.
  Do NOT make up numbers, estimates, or conclusions that aren't in the data.

RULE 2 — NEVER USE TECHNICAL LANGUAGE:
  Do not mention SQL, databases, tables, joins, queries, or any technical term.
  Write as if explaining to a business manager who has never heard of SQL.

RULE 3 — IF DATA IS EMPTY:
  Say exactly what happened in plain English. For example:
  "The database did not return any results for this question.
   This may mean no records match those criteria, or the question may need
   to be more specific. Please try rephrasing your question."
  Do NOT assume why the data is empty or invent a reason.

RULE 4 — IF YOU ARE UNSURE:
  If the data provided is ambiguous and you cannot give a confident answer,
  say: "I need more information to answer this accurately. Could you clarify [specific thing]?"
  Do NOT guess.

RULE 5 — FORMAT:
  - First sentence: directly answer the question (or say data is unavailable).
  - Then 2-3 sentences with key numbers or context from the data.
  - Maximum 4 sentences total.
  - No bullet points. Plain paragraph only.

Answer:
""")

        self.parser = StrOutputParser()

    # ── Public API ────────────────────────────────────────────────────────────

    def generate(self, question: str, sql_results: list) -> str:
        """Generate NL response (no usage tracking — backward compat)."""
        answer, _ = self.generate_with_usage(question, sql_results)
        return answer

    def generate_with_usage(
        self, question: str, sql_results: list
    ) -> Tuple[str, Dict[str, int]]:
        """Generate NL response and return (answer, token_usage)."""
        try:
            # Limit data sent to LLM to avoid context overflow
            data_str = str(sql_results)[:3000] if sql_results else "No data returned."

            raw_response, _model = invoke_with_fallback(
                chain_builder=lambda llm: self.prompt | llm,
                invoke_kwargs={"question": question, "data": data_str},
                api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            usage  = self._extract_usage(raw_response)
            answer = extract_text_content(raw_response)

            logger.info("[RESPONSE] Generated successfully")
            return answer, usage

        except Exception as e:
            logger.error(f"[RESPONSE] Error generating response: {e}")
            # On failure, return honest human-readable message — no assumptions
            return (
                "The system was unable to generate a response at this time. "
                "This is a temporary issue, not a problem with your question. "
                "Please try again in a moment.",
                {},
            )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_usage(response) -> Dict[str, int]:
        usage = {}
        try:
            meta = getattr(response, "usage_metadata", None)
            if meta:
                if isinstance(meta, dict):
                    usage["input_tokens"]  = meta.get("input_tokens",  0)
                    usage["output_tokens"] = meta.get("output_tokens", 0)
                else:
                    usage["input_tokens"]  = getattr(meta, "input_tokens",  0)
                    usage["output_tokens"] = getattr(meta, "output_tokens", 0)
        except Exception:
            pass
        return usage
