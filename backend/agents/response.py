import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)


class ResponseAgent:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.3,
            max_tokens=1000
        )
        
        self.prompt = ChatPromptTemplate.from_template("""
You are a business analyst. Create a clear business-friendly answer.

Question: {question}
Data: {data}

Generate a natural language response that:
1. Directly answers the question
2. Includes key numbers and metrics
3. Is clear for non-technical stakeholders
4. Is concise (2-3 sentences max)
5. Never fabricates information

Answer:
""")
        
        self.parser = StrOutputParser()
    
    def generate(self, question: str, sql_results: list) -> str:
        try:
            chain = self.prompt | self.llm | self.parser
            
            data_str = str(sql_results)[:2000]
            
            answer = chain.invoke({"question": question, "data": data_str})
            
            logger.info(f"Generated response")
            return answer
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Unable to generate response at this time."
