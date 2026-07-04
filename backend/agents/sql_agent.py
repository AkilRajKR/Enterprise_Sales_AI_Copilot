import logging
import sqlite3
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
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
- Entities: {entities}
- Metrics: {metrics}

Generate a single, optimized SELECT query.
Return ONLY the SQL query, no explanation.

Question: {question}
""")
        
        self.parser = StrOutputParser()
    
    def _get_schema(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        
        schema = "\n\n".join([row[0] for row in cursor.fetchall()])
        conn.close()
        
        return schema
    
    def generate_query(self, question: str, intent: Dict[str, Any]) -> str:
        try:
            chain = self.prompt | self.llm | self.parser
            
            query = chain.invoke({
                "question": question,
                "schema": self.schema,
                "intent_type": intent.get("intent", "unknown"),
                "entities": intent.get("entities", {}),
                "metrics": intent.get("metrics", [])
            })
            
            dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "PRAGMA"]
            query_upper = query.upper()
            
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    logger.error(f"Dangerous SQL detected: {keyword}")
                    return None
            
            logger.info(f"Generated SQL query")
            return query
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
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
            logger.info(f"Query returned {len(results)} rows")
            return results
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
