import logging
import os
import sqlite3
from typing import List, Dict, Any, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.llm_factory import invoke_with_fallback

logger = logging.getLogger(__name__)


class SQLAgent:
    def __init__(self, api_key: str, db_path: str):
        self.db_path     = db_path
        self.api_key     = api_key
        self.temperature = 0.0
        self.max_tokens  = int(os.getenv("SQL_MAX_TOKENS", 500))

        self.schema = self._get_schema()

        self.prompt = ChatPromptTemplate.from_template("""
Business meaning:

Brands = car manufacturers

Models = cars produced by a brand

Customer_Ownership = completed vehicle sales

Dealer_Brand = brands available at dealers

Car_Vins = every physical car

Customers = buyers

Database Schema:
{schema}

User Intent:
- Type: {intent_type}
- Tables: {tables}
- Metrics: {metrics}
- SQL Keywords: {sql_keywords}

Rules:
1. ONLY SELECT statements allowed
2. Use proper JOINs for multi-table queries
3. Include GROUP BY for aggregations
4. Use ORDER BY for sorting
5. Add LIMIT for large result sets
6. Use aliases for readability
7. Return ONLY the raw SQL query — no markdown, no explanation.

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
        """Generate SQL and return (sql_query, token_usage)."""
        logger.info("=" * 80)
        logger.info("ENTERED SQL AGENT")
        logger.info(f"Question : {question}")
        logger.info(f"Intent   : {intent}")
        logger.info("=" * 80)

        # Build chain (without parser so we can grab usage metadata)
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
        query = raw_response.content

        # ── Strip markdown fences that Gemini may wrap the SQL in ──────────
        query = query.strip()
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

    # ── SQL execution ─────────────────────────────────────────────────────────

    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts."""
        # Safety check before executing
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
