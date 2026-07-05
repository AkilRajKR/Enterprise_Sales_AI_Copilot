import logging
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

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
You are a data validation expert for sales analytics.

Validate that SQL results correctly answer the user's question:

Original Question: {question}

Planned Intent:
- Type: {intent}
- Entities: {entities}
- Metrics: {metrics}

SQL Query: {sql_query}

SQL Results (first 10 rows):
{sql_results}

Validate:
1. Do the results answer the question?
2. Are the metrics correct?
3. Are the data values reasonable?
4. Is the data logically consistent?
5. Are there missing rows or anomalies?

Provide confidence score (0.0-1.0) for validity.

Respond with ONLY JSON:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "feedback": "clear explanation",
    "issues": ["issue1", "issue2"] or []
}}
""")
        
        self.parser = JsonOutputParser()
    
    def validate(
        self,
        question: str,
        intent: Dict[str, Any],
        sql_query: str,
        sql_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        try:
            chain = self.prompt | self.llm | self.parser
            
            # Format results safely
            if len(sql_results) > 10:
                results_preview = sql_results[:10]
                results_str = json.dumps(results_preview, default=str) + f"\n(... and {len(sql_results) - 10} more rows)"
            else:
                results_str = json.dumps(sql_results, default=str)
            
            validation = chain.invoke({
                "question": question,
                "intent": intent.get("intent", "unknown"),
                "entities": intent.get("entities", {}),
                "metrics": intent.get("metrics", []),
                "sql_query": sql_query,
                "sql_results": results_str[:2000]  # Truncate to avoid token limits
            })
            
            logger.info(f"[VALIDATOR] Valid={validation.get('is_valid')}, Confidence={validation.get('confidence')}")
            return validation
        except Exception as e:
            logger.error(f"[VALIDATOR] Error: {e}")
            return {
                "is_valid": False,
                "confidence": 0.0,
                "feedback": f"Validation error: {str(e)}",
                "issues": ["Validation failed"]
            }
