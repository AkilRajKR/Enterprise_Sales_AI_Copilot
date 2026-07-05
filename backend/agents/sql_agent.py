import logging
import sqlite3
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)


class SQLAgent:
    def __init__(self, api_key: str, db_path: str):
        self.db_path = db_path
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.0,
            max_tokens=500
        )
        
        self.schema = self._get_schema()
        
        self.prompt = ChatPromptTemplate.from_template("""
You are a SQL expert for sales analytics. Generate ONLY safe SELECT queries.

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

Generate a single, optimized SELECT query.
Return ONLY the SQL query, no explanation.

Question: {question}
""")
        
        self.parser = StrOutputParser()
        self.dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "PRAGMA", "ATTACH", "DETACH"]
    
    def _get_schema(self) -> str:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            schema_list = [row[0] for row in cursor.fetchall() if row[0]]
            conn.close()
            
            return "\n\n".join(schema_list)
        except Exception as e:
            logger.error(f"[SQL] Error getting schema: {e}")
            return ""
    
    def generate_query(self, question: str, intent: Dict[str, Any]) -> str:
        try:
            chain = self.prompt | self.llm | self.parser
            
            query = chain.invoke({
                "question": question,
                "schema": self.schema,
                "intent_type": intent.get("intent", "unknown"),
                "tables": intent.get("entities", {}).get("tables", []),
                "metrics": intent.get("metrics", []),
                "sql_keywords": intent.get("sql_keywords", [])
            })
            
            # Security check: prevent injection
            query_upper = query.upper()
            for keyword in self.dangerous_keywords:
                if keyword in query_upper:
                    logger.error(f"[SQL] Dangerous keyword detected: {keyword}")
                    return None
            
            # Ensure it's a SELECT query
            if not query_upper.strip().startswith("SELECT"):
                logger.error(f"[SQL] Not a SELECT query")
                return None
            
            logger.info(f"[SQL] Generated: {query[:80]}...")
            return query
        except Exception as e:
            logger.error(f"[SQL] Error generating query: {e}")
            return None
    
    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            conn.close()
            
            results = [dict(row) for row in rows]
            logger.info(f"[SQL] Executed: {len(results)} rows returned")
            return results
        except Exception as e:
            logger.error(f"[SQL] Error executing query: {e}")
            return []
