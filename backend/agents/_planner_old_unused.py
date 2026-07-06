import logging
import json
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class PlannerAgent:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.1,
            max_tokens=100
        )
        
        self.prompt = ChatPromptTemplate.from_template("""
You are the planning agent for an Enterprise Automotive Sales Analytics system.

The database contains these business entities:

- Brands: vehicle manufacturers
- Models: vehicle models belonging to brands
- Dealers: dealerships selling vehicles
- Customers: vehicle buyers
- Customer_Ownership: links customers with purchased vehicles
- Car_Vins: individual vehicles
- Car_Parts: parts associated with vehicles
- Car_Options: optional equipment
- Manufacture_Plant: production plants
- Dealer_Brand: brands sold by each dealer

A question is RELEVANT if it is about:
- vehicle sales
- customers
- dealerships
- brands
- models
- VINs
- ownership
- inventory
- parts
- options
- manufacturing

Map common business words:

product -> Model or Brand
car -> Car_Vins
buyer -> Customer
sale -> Customer_Ownership
dealer -> Dealers
manufacturer -> Brands or Manufacture_Plant

IMPORTANT:

Return ONLY a JSON object.

Do NOT include explanations.

Do NOT use Markdown.

Return exactly in this format:

{{
    "is_relevant": true,
    "intent": "customer_analysis",
    "entities": {{
        "tables": ["Customers"],
        "filters": {{}},
        "aggregations": ["COUNT"]
    }},
    "metrics": ["customer_count"],
    "sql_keywords": ["COUNT"],
    "confidence": 0.95
}}

Question:
{question}
""")
        
    def classify(self, question: str) -> Dict[str, Any]:
        try:
            chain = self.prompt | self.llm

            raw = chain.invoke({"question": question})

            logger.info("=" * 80)
            logger.info("RAW GEMINI RESPONSE:")
            logger.info(raw.content)
            logger.info("=" * 80)

            content = raw.content.strip()

            # Remove Markdown code fences
            if content.startswith("```json"):
                content = content.replace("```json", "", 1)

            if content.startswith("```"):
                content = content.replace("```", "", 1)

            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()

            result = json.loads(content)

            # Ensure all required keys exist
            result.setdefault("is_relevant", True)
            result.setdefault("intent", "general_analysis")
            result.setdefault("entities", {
                "tables": [],
                "filters": {},
                "aggregations": []
            })
            result.setdefault("metrics", [])
            result.setdefault("sql_keywords", [])
            result.setdefault("confidence", 0.8)

            result["normalized_question"] = self._normalize_question(question)

            logger.info(
                f"[PLANNER] Classified: "
                f"is_relevant={result['is_relevant']}, "
                f"intent={result['intent']}"
            )

            return result

        except Exception as e:
            logger.exception("[PLANNER] Parsing failed")

            return {
                "is_relevant": False,
                "intent": "error",
                "entities": {
                    "tables": [],
                    "filters": {},
                    "aggregations": []
                },
                "metrics": [],
                "sql_keywords": [],
                "confidence": 0.0,
                "normalized_question": self._normalize_question(question)
            }
    
    def _normalize_question(self, question: str) -> str:
        """Normalize question for semantic matching"""
        return question.strip().lower()


"""{
"is_relevant": true,
"intent": "...",
"entities": {
"tables": [],
"filters": {},
"aggregations": []
},
"metrics": [],
"sql_keywords": [],
"confidence": 0.95
}"""