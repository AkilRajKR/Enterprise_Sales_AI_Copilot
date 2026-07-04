import logging
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)


class ValidatorAgent:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=api_key,
            temperature=0.0,
            max_tokens=500
        )
        
        self.prompt = ChatPromptTemplate.from_template("""
You are a data validation expert. Verify SQL results match intent.

Original Question: {question}
Original Intent: {intent}
SQL Query: {sql_query}
SQL Results: {sql_results}

Validate if results answer the question correctly.

Return ONLY JSON:
{{
    "is_valid": true/false,
    "confidence": 0.0,
    "feedback": "explanation",
    "issues": []
}}
""")
        
        self.parser = JsonOutputParser()
    
    def validate(self, question: str, intent: Dict[str, Any], sql_query: str, sql_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            chain = self.prompt | self.llm | self.parser
            
            results_str = str(sql_results)[:2000]
            
            validation = chain.invoke({
                "question": question,
                "intent": intent,
                "sql_query": sql_query,
                "sql_results": results_str
            })
            
            logger.info(f"Validation result: {validation}")
            return validation
        except Exception as e:
            logger.error(f"Error validating: {e}")
            return {"is_valid": False, "confidence": 0.0, "feedback": f"Error: {str(e)}", "issues": []}
