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
    
    def _init_cache_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qa_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                normalized_question TEXT UNIQUE NOT NULL,
                original_question TEXT NOT NULL,
                sql_query TEXT NOT NULL,
                answer TEXT NOT NULL,
                evidence TEXT NOT NULL,
                confidence REAL NOT NULL,
                execution_time_ms REAL NOT NULL,
                token_usage TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def normalize_question(self, question: str) -> str:
        return question.strip().lower()
    
    def get(self, question: str, ttl_hours: int = 24) -> Optional[Dict[str, Any]]:
        normalized = self.normalize_question(question)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM qa_cache 
            WHERE normalized_question = ? 
            AND datetime(created_at) > datetime('now', '-' || ? || ' hours')
            ORDER BY created_at DESC LIMIT 1
        """, (normalized, ttl_hours))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            logger.info(f"Cache hit for: {question}")
            return {
                "id": row["id"],
                "original_question": row["original_question"],
                "sql_query": row["sql_query"],
                "answer": row["answer"],
                "evidence": json.loads(row["evidence"]),
                "confidence": row["confidence"],
                "execution_time_ms": row["execution_time_ms"],
                "token_usage": json.loads(row["token_usage"]),
                "created_at": row["created_at"]
            }
        
        logger.info(f"Cache miss for: {question}")
        return None
    
    def store(self, original_question: str, sql_query: str, answer: str, evidence: Dict[str, Any], confidence: float, execution_time_ms: float, token_usage: Dict[str, int]) -> bool:
        normalized = self.normalize_question(original_question)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO qa_cache 
                (normalized_question, original_question, sql_query, answer, evidence, confidence, execution_time_ms, token_usage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(normalized_question) DO UPDATE SET
                    answer = excluded.answer,
                    sql_query = excluded.sql_query,
                    evidence = excluded.evidence,
                    confidence = excluded.confidence,
                    execution_time_ms = excluded.execution_time_ms,
                    token_usage = excluded.token_usage,
                    updated_at = CURRENT_TIMESTAMP
            """, (normalized, original_question, sql_query, answer, json.dumps(evidence), confidence, execution_time_ms, json.dumps(token_usage)))
            
            conn.commit()
            conn.close()
            logger.info(f"Cached answer for: {original_question}")
            return True
        except Exception as e:
            logger.error(f"Error caching answer: {e}")
            conn.close()
            return False
    
    def get_history(self, limit: int = 50) -> list:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM qa_cache ORDER BY created_at DESC LIMIT ?", (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def clear_expired(self, ttl_hours: int = 24) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM qa_cache WHERE datetime(created_at) < datetime('now', '-' || ? || ' hours')", (ttl_hours,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Cleared {deleted} expired cache entries")
        return deleted
