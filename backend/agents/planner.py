import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)


class PlannerAgent:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1,
            max_tokens=100
        )
        
        self.prompt = ChatPromptTemplate.from_template("""
You are a sales question classifier and intent decomposer.

Analyze the user's question and determine:
1. If it's sales/revenue related (relevant) or not
2. The intent type: revenue_analysis, customer_analysis, product_analysis, employee_analysis, or other
3. Key entities mentioned
4. Required metrics

Return ONLY valid JSON:
{{
    "is_relevant": true/false,
    "intent": "intent_type",
    "entities": {{}},
    "metrics": [],
    "confidence": 0.0
}}

Question: {question}
""")
        
        self.parser = JsonOutputParser()
    
    def classify(self, question: str) -> Dict[str, Any]:
        try:
            chain = self.prompt | self.llm | self.parser
            result = chain.invoke({"question": question})
            logger.info(f"Planner classified: {question}")
            return result
        except Exception as e:
            logger.error(f"Error in planner: {e}")
            return {"is_relevant": False, "intent": "error", "entities": {}, "metrics": [], "confidence": 0.0}
