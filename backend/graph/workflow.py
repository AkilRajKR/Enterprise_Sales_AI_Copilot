import time
import logging
from datetime import datetime
from typing import Any
from langgraph.graph import StateGraph
from graph.state import SalesState
from agents.planner import PlannerAgent
from agents.sql_agent import SQLAgent
from agents.validator import ValidatorAgent
from agents.response import ResponseAgent
from agents.cache import CacheAgent
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

api_key = os.getenv("GEMINI_API_KEY")
db_path = os.getenv("DATABASE_PATH", "database/sales.db")
max_retries = int(os.getenv("MAX_RETRIES", 4))

planner = PlannerAgent(api_key)
sql_agent = SQLAgent(api_key, db_path)
validator = ValidatorAgent(api_key)
response_agent = ResponseAgent(api_key)
cache_agent = CacheAgent(db_path)


def plan_node(state: SalesState) -> SalesState:
    """Planner node: classify question and decompose intent"""
    logger.info(f"Planning: {state['user_question']}")
    
    planner_output = planner.classify(state['user_question'])
    state['planner_output'] = planner_output
    state['is_relevant'] = planner_output.get('is_relevant', False)
    
    return state


def relevance_check_node(state: SalesState) -> SalesState:
    """Check if question is relevant to sales"""
    if not state['is_relevant']:
        logger.info("Question rejected: not sales-related")
        state['final_answer'] = "I can only answer sales and revenue-related questions."
        state['confidence'] = 0.0
    
    return state


def cache_lookup_node(state: SalesState) -> SalesState:
    """Check cache for existing answer"""
    if not state['is_relevant']:
        return state
    
    cached = cache_agent.get(state['user_question'])
    if cached:
        state['cache_hit'] = True
        state['cached_answer'] = cached
        state['final_answer'] = cached['answer']
        state['sql_query'] = cached['sql_query']
        state['evidence'] = cached['evidence']
        state['confidence'] = cached['confidence']
        state['token_usage'] = cached['token_usage']
        logger.info("Cache hit!")
    
    return state


def sql_generation_node(state: SalesState) -> SalesState:
    """Generate SQL query"""
    if state['cache_hit'] or not state['is_relevant']:
        return state
    
    logger.info("Generating SQL...")
    sql_query = sql_agent.generate_query(
        state['user_question'],
        state['planner_output']
    )
    
    if not sql_query:
        state['final_answer'] = "Unable to generate query for this question."
        state['confidence'] = 0.0
        return state
    
    state['sql_query'] = sql_query
    logger.info(f"Generated query: {sql_query}")
    
    return state


def sql_execution_node(state: SalesState) -> SalesState:
    """Execute SQL query"""
    if state['cache_hit'] or not state['is_relevant'] or not state.get('sql_query'):
        return state
    
    logger.info("Executing SQL...")
    results = sql_agent.execute_query(state['sql_query'])
    state['sql_result'] = results
    
    return state


def validation_node(state: SalesState) -> SalesState:
    """Validate SQL results"""
    if state['cache_hit'] or not state['is_relevant'] or not state.get('sql_result'):
        return state
    
    logger.info("Validating results...")
    validation = validator.validate(
        state['user_question'],
        state['planner_output'],
        state['sql_query'],
        state['sql_result']
    )
    
    state['validation_status'] = validation.get('is_valid', False)
    state['validation_feedback'] = validation.get('feedback', '')
    state['confidence'] = validation.get('confidence', 0.0)
    
    return state


def retry_decision_node(state: SalesState) -> str:
    """Decide whether to retry or proceed"""
    if state['cache_hit'] or not state['is_relevant']:
        return "generate_response"
    
    if state.get('validation_status'):
        return "generate_response"
    
    if state['retry_count'] < max_retries:
        logger.info(f"Retry {state['retry_count'] + 1}/{max_retries}")
        return "sql_generation"
    
    logger.info("Max retries reached")
    return "generate_response"


def response_generation_node(state: SalesState) -> SalesState:
    """Generate business-friendly response"""
    if not state['is_relevant']:
        return state
    
    if not state.get('final_answer') or state['cache_hit']:
        return state
    
    logger.info("Generating response...")
    answer = response_agent.generate(
        state['user_question'],
        state.get('sql_result', [])
    )
    
    state['final_answer'] = answer
    
    return state


def cache_store_node(state: SalesState) -> SalesState:
    """Store validated response in cache"""
    if state['cache_hit'] or not state['is_relevant'] or not state.get('validation_status'):
        return state
    
    logger.info("Storing in cache...")
    cache_agent.store(
        state['user_question'],
        state['sql_query'],
        state['final_answer'],
        state.get('evidence', {}),
        state['confidence'],
        state.get('execution_time_ms', 0),
        state.get('token_usage', {})
    )
    
    return state


def create_sales_workflow():
    """Create and compile the LangGraph workflow"""
    workflow = StateGraph(SalesState)
    
    # Add nodes
    workflow.add_node("plan", plan_node)
    workflow.add_node("relevance_check", relevance_check_node)
    workflow.add_node("cache_lookup", cache_lookup_node)
    workflow.add_node("sql_generation", sql_generation_node)
    workflow.add_node("sql_execution", sql_execution_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("generate_response", response_generation_node)
    workflow.add_node("cache_store", cache_store_node)
    
    # Add edges
    workflow.add_edge("plan", "relevance_check")
    workflow.add_edge("relevance_check", "cache_lookup")
    workflow.add_edge("cache_lookup", "sql_generation")
    workflow.add_edge("sql_generation", "sql_execution")
    workflow.add_edge("sql_execution", "validation")
    workflow.add_conditional_edges(
        "validation",
        retry_decision_node,
        {"sql_generation": "sql_generation", "generate_response": "generate_response"}
    )
    workflow.add_edge("generate_response", "cache_store")
    
    workflow.set_entry_point("plan")
    workflow.set_finish_point("cache_store")
    
    return workflow.compile()
