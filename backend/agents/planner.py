import logging
import json
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)


class PlannerAgent:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5",
            google_api_key=api_key,
            temperature=0.1,
            max_tokens=100
        )
        
        self.prompt = ChatPromptTemplate.from_template("""
You are a sales question classifier and intent decomposer.

Analyze the user's question and determine:
1. If it's sales/revenue related (relevant) or not
2. The intent type: revenue_analysis, customer_analysis, product_analysis, employee_analysis, or other
3. Key entities mentioned (table names, time periods, metrics)
4. Required metrics
5. SQL keywords needed

Return ONLY valid JSON:
{{
    "is_relevant": true/false,
    "intent": "intent_type",
    "entities": {{
        "tables": [],
        "filters": {{}},
        "aggregations": []
    }},
    "metrics": [],
    "sql_keywords": [],
    "confidence": 0.0
}}

Question: {question}
""")
        
        self.parser = JsonOutputParser()
    
    def classify(self, question: str) -> Dict[str, Any]:
        try:
            chain = self.prompt | self.llm | self.parser
            result = chain.invoke({"question": question})
            
            # Normalize question for caching
            normalized = self._normalize_question(question)
            result['normalized_question'] = normalized
            
            logger.info(f"[PLANNER] Classified: is_relevant={result.get('is_relevant')}, intent={result.get('intent')}")
            return result
        except Exception as e:
            logger.error(f"[PLANNER] Error: {e}")
            return {
                "is_relevant": False,
                "intent": "error",
                "entities": {"tables": [], "filters": {}, "aggregations": []},
                "metrics": [],
                "sql_keywords": [],
                "confidence": 0.0,
                "normalized_question": self._normalize_question(question)
            }
    
    def _normalize_question(self, question: str) -> str:
        """Normalize question for semantic matching"""
        return question.strip().lower()
