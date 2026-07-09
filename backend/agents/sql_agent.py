import logging
import os
import sqlite3
from typing import List, Dict, Any, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.llm_factory import invoke_with_fallback

logger = logging.getLogger(__name__)

_CLARIFICATION_PREFIX = "CLARIFICATION_NEEDED:"


class SQLAgent:
    def __init__(self, api_key: str, db_path: str):
        self.db_path     = db_path
        self.api_key     = api_key
        self.temperature = 0.0
        self.max_tokens  = int(os.getenv("SQL_MAX_TOKENS", 600))

        self.schema = self._get_schema()

        self.prompt = ChatPromptTemplate.from_template("""
You are a SQL generation agent for an Automotive Sales database.

=== DATABASE SCHEMA ===
{schema}

=== BUSINESS MEANING ===
Brands             = car manufacturers
Models             = cars produced by a brand
Customer_Ownership = completed vehicle sales records
Dealer_Brand       = brands available at each dealer
Car_Vins           = every individual physical vehicle
Customers          = buyers (NO personal identifiers allowed in SELECT)
Manufacture_Plant  = factories that build vehicles

=== USER INTENT ===
- Type: {intent_type}
- Tables: {tables}
- Metrics: {metrics}
- SQL Keywords: {sql_keywords}

=== STRICT RULES — NEVER VIOLATE ===

RULE 1 — NEVER ASSUME:
  If the question is unclear, vague, or you are not sure which table or column
  to use, DO NOT guess. Instead output EXACTLY this text and nothing else:
  CLARIFICATION_NEEDED: <your plain-English question asking for more detail>

RULE 2 — NO PERSONAL DATA:
  Never SELECT columns: name, full_name, first_name, last_name, dob,
  date_of_birth, salary, income, phone, email, address, ssn, passport,
  credit_card, bank_account or any similar personal identifier.
  If the question requires personal data, output:
  CLARIFICATION_NEEDED: That data is protected. I can only provide aggregated or anonymised metrics.

RULE 3 — SELECT ONLY:
  Only generate SELECT statements. No INSERT, UPDATE, DELETE, DROP, PRAGMA.

RULE 4 — CORRECT SQL:
  Use proper JOINs, GROUP BY for aggregations, ORDER BY for sorting,
  LIMIT for large result sets. Use aliases for readability.

RULE 5 — OUTPUT FORMAT:
  Either output a valid raw SQL query (no markdown, no explanation),
  OR output exactly: CLARIFICATION_NEEDED: <plain-English question>
  Nothing else is allowed.

Question: {question}
""")

        self.parser = StrOutputParser()
        self.dangerous_keywords = [
            "DROP", "DELETE", "UPDATE", "INSERT",
            "ALTER", "TRUNCATE", "PRAGMA", "ATTACH", "DETACH",
        ]

    # ── Schema ────────────────────────────────────────────────────────────────

    def _get_schema(self) -> str:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT sql FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                schema_list = [row[0] for row in cursor.fetchall() if row[0]]
            return "\n\n".join(schema_list)
        except Exception as e:
            logger.error(f"[SQL] Error getting schema: {e}")
            return ""

    # ── SQL generation ────────────────────────────────────────────────────────

    def generate_query(self, question: str, intent: Dict[str, Any]) -> str:
        """Generate SQL (no usage tracking — backward compat)."""
        query, _ = self.generate_query_with_usage(question, intent)
        return query

    def generate_query_with_usage(
        self, question: str, intent: Dict[str, Any]
    ) -> Tuple[str, Dict[str, int]]:
        """Generate SQL and return (sql_query, token_usage).
        Returns 'CLARIFICATION_NEEDED: ...' string if LLM cannot generate SQL.
        """
        logger.info("=" * 80)
        logger.info("ENTERED SQL AGENT")
        logger.info(f"Question : {question}")
        logger.info(f"Intent   : {intent}")
        logger.info("=" * 80)

        try:
            raw_response, _model = invoke_with_fallback(
                chain_builder=lambda llm: self.prompt | llm,
                invoke_kwargs={
                    "question":    question,
                    "schema":      self.schema,
                    "intent_type": intent.get("intent", "unknown"),
                    "tables":      intent.get("entities", {}).get("tables", []),
                    "metrics":     intent.get("metrics", []),
                    "sql_keywords": intent.get("sql_keywords", []),
                },
                api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            usage = self._extract_usage(raw_response)
            query = raw_response.content.strip()

            # Strip markdown fences that Gemini may wrap the SQL in
            for fence in ("```sql", "```"):
                if query.startswith(fence):
                    query = query[len(fence):]
            if query.endswith("```"):
                query = query[:-3]
            query = query.strip()

            logger.info("=" * 80)
            logger.info("CLEANED SQL FROM GEMINI")
            logger.info(query)
            logger.info("=" * 80)

            return query, usage

        except Exception as e:
            logger.error(f"[SQL] Generation failed: {e}")
            # On failure, surface clarification rather than guessing
            return (
                f"{_CLARIFICATION_PREFIX} I was unable to generate a query for your question. "
                "Could you rephrase it? Specify the entity (brand, model, dealer) and the metric you want (count, total, top N).",
                {},
            )

    # ── SQL execution ─────────────────────────────────────────────────────────

    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts."""
        # If SQL agent returned a clarification request, don't execute
        if sql_query.startswith(_CLARIFICATION_PREFIX):
            return []

        query_upper = sql_query.upper()
        for kw in self.dangerous_keywords:
            if kw in query_upper:
                logger.error(f"[SQL] Dangerous keyword detected: {kw}")
                return []

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(sql_query)
                rows = cursor.fetchall()

            results = [dict(row) for row in rows]
            logger.info(f"[SQL] Executed: {len(results)} rows returned")
            return results

        except Exception as e:
            logger.error(f"[SQL] Error executing query: {e}")
            return []

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
