import os
import json
import sqlite3
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CacheAgent:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_cache_table()

    # ── Schema init ───────────────────────────────────────────────────────────

    def _init_cache_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS qa_cache (
                    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                    normalized_question TEXT UNIQUE NOT NULL,
                    original_question   TEXT NOT NULL,
                    sql_query           TEXT NOT NULL,
                    answer              TEXT NOT NULL,
                    evidence            TEXT NOT NULL,
                    confidence          REAL NOT NULL,
                    execution_time_ms   REAL NOT NULL,
                    token_usage         TEXT NOT NULL,
                    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def normalize_question(self, question: str) -> str:
        return question.strip().lower()

    # ── Cache read ────────────────────────────────────────────────────────────

    def get(self, question: str, ttl_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Return cached answer or None."""
        normalized = self.normalize_question(question)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM qa_cache
                WHERE normalized_question = ?
                  AND datetime(created_at) > datetime('now', '-' || ? || ' hours')
                ORDER BY created_at DESC
                LIMIT 1
            """, (normalized, ttl_hours))
            row = cursor.fetchone()

        if row:
            logger.info(f"[CACHE] Hit for: {question}")
            return {
                "id":                row["id"],
                "original_question": row["original_question"],
                "sql_query":         row["sql_query"],
                "answer":            row["answer"],
                "evidence":          json.loads(row["evidence"]),
                "confidence":        row["confidence"],
                "execution_time_ms": row["execution_time_ms"],
                "token_usage":       json.loads(row["token_usage"]),
                "created_at":        row["created_at"],
            }

        logger.info(f"[CACHE] Miss for: {question}")
        return None

    # ── Cache write ───────────────────────────────────────────────────────────

    def store(
        self,
        original_question: str,
        sql_query: str,
        answer: str,
        evidence: Dict[str, Any],
        confidence: float,
        execution_time_ms: float,
        token_usage: Dict[str, int],
    ) -> bool:
        normalized = self.normalize_question(original_question)

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO qa_cache
                        (normalized_question, original_question, sql_query, answer,
                         evidence, confidence, execution_time_ms, token_usage)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(normalized_question) DO UPDATE SET
                        answer            = excluded.answer,
                        sql_query         = excluded.sql_query,
                        evidence          = excluded.evidence,
                        confidence        = excluded.confidence,
                        execution_time_ms = excluded.execution_time_ms,
                        token_usage       = excluded.token_usage,
                        updated_at        = CURRENT_TIMESTAMP
                """, (
                    normalized,
                    original_question,
                    sql_query,
                    answer,
                    json.dumps(evidence),
                    confidence,
                    execution_time_ms,
                    json.dumps(token_usage),
                ))
                conn.commit()

            logger.info(f"[CACHE] Stored answer for: {original_question}")
            return True

        except Exception as e:
            logger.error(f"[CACHE] Error storing answer: {e}")
            return False

    # ── History ───────────────────────────────────────────────────────────────

    def get_history(self, limit: int = 50) -> list:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM qa_cache ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
        return [dict(row) for row in rows]

    # ── Maintenance ───────────────────────────────────────────────────────────

    def clear_expired(self, ttl_hours: int = 24) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM qa_cache "
                "WHERE datetime(created_at) < datetime('now', '-' || ? || ' hours')",
                (ttl_hours,),
            )
            deleted = cursor.rowcount
            conn.commit()

        logger.info(f"[CACHE] Cleared {deleted} expired cache entries")
        return deleted
