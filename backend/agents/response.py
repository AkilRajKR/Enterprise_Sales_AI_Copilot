import logging
import os
from typing import Dict, Any, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.llm_factory import invoke_with_fallback

logger = logging.getLogger(__name__)


class ResponseAgent:
    def __init__(self, api_key: str):
        self.api_key     = api_key
        self.temperature = 0.3
        self.max_tokens  = int(os.getenv("RESPONSE_MAX_TOKENS", 1000))

        self.prompt = ChatPromptTemplate.from_template("""
You are an Automotive Sales Business Analyst. Create a clear, business-friendly answer.

Question: {question}
Data: {data}

Guidelines:
1. Directly answer the question in the first sentence.
2. Include the key numbers and metrics from the data.
3. Write for non-technical stakeholders — no SQL jargon.
4. Keep it concise: 2–4 sentences maximum.
5. Never fabricate or assume data that isn't in the provided results.
6. If results are empty, say so clearly.

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
            data_str = str(sql_results)[:2000]

            raw_response, _model = invoke_with_fallback(
                chain_builder=lambda llm: self.prompt | llm,
                invoke_kwargs={"question": question, "data": data_str},
                api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            usage  = self._extract_usage(raw_response)
            answer = raw_response.content.strip()

            logger.info("[RESPONSE] Generated successfully")
            return answer, usage

        except Exception as e:
            logger.error(f"[RESPONSE] Error generating response: {e}")
            return "Unable to generate a response at this time.", {}

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
