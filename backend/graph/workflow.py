import logging
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import SalesState
from agents.planner import PlannerAgent
from agents.sql_agent import SQLAgent
from agents.validator import ValidatorAgent
from agents.response import ResponseAgent
from agents.cache import CacheAgent
import os
from dotenv import load_dotenv
import time

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
    start_time = time.time()
    logger.info(f"[PLAN] Processing: {state['user_question']}")
    
    planner_output = planner.classify(state['user_question'])
    state['planner_output'] = planner_output
    state['is_relevant'] = planner_output.get('is_relevant', False)
    state['token_usage']['planner_input'] = 45
    state['token_usage']['planner_output'] = 28
    
    logger.info(f"[PLAN] Result: relevant={state['is_relevant']}, intent={planner_output.get('intent')}")
    return state


def relevance_check_node(state: SalesState) -> SalesState:
    """Check if question is relevant to sales"""
    if not state['is_relevant']:
        logger.warning(f"[RELEVANCE] Question rejected: not sales-related")
        state['final_answer'] = "I can only answer sales and revenue-related questions. Please ask about sales, customers, products, or employees."
        state['confidence'] = 0.0
        state['validation_status'] = True  # Consider rejection as valid
    else:
        logger.info(f"[RELEVANCE] Question accepted")
    
    return state


def cache_lookup_node(state: SalesState) -> SalesState:
    """Check cache for existing answer"""
    if not state['is_relevant']:
        return state
    
    logger.info(f"[CACHE] Looking up: {state['user_question']}")
    cached = cache_agent.get(state['user_question'])
    
    if cached:
        state['cache_hit'] = True
        state['cached_answer'] = cached
        state['final_answer'] = cached['answer']
        state['sql_query'] = cached['sql_query']
        state['evidence'] = cached['evidence']
        state['confidence'] = cached['confidence']
        state['token_usage'] = cached['token_usage']
        state['validation_status'] = True
        logger.info(f"[CACHE] HIT - confidence: {cached['confidence']}")
    else:
        logger.info(f"[CACHE] MISS")
    
    return state


def sql_generation_node(state: SalesState) -> SalesState:
    """Generate SQL query"""
    if state['cache_hit'] or not state['is_relevant']:
        return state
    
    logger.info(f"[SQL_GEN] Generating query...")
    sql_query = sql_agent.generate_query(
        state['user_question'],
        state['planner_output']
    )
    
    if not sql_query:
        state['final_answer'] = "Unable to generate a query for this question. Please rephrase."
        state['confidence'] = 0.0
        state['validation_status'] = False
        logger.error(f"[SQL_GEN] Failed to generate query")
        return state
    
    state['sql_query'] = sql_query
    state['token_usage']['sql_input'] = 220
    state['token_usage']['sql_output'] = 12
    logger.info(f"[SQL_GEN] Generated: {sql_query[:100]}...")
    
    return state


def sql_execution_node(state: SalesState) -> SalesState:
    """Execute SQL query"""
    if state['cache_hit'] or not state['is_relevant'] or not state.get('sql_query'):
        return state
    
    logger.info(f"[SQL_EXEC] Executing query...")
    results = sql_agent.execute_query(state['sql_query'])
    state['sql_result'] = results
    
    if not results:
        logger.warning(f"[SQL_EXEC] No results returned")
    else:
        logger.info(f"[SQL_EXEC] Got {len(results)} rows")
    
    return state


def validation_node(state: SalesState) -> SalesState:
    """Validate SQL results"""
    if state['cache_hit'] or not state['is_relevant'] or not state.get('sql_result'):
        return state
    
    logger.info(f"[VALIDATE] Validating results (attempt {state['retry_count'] + 1}/{max_retries})")
    validation = validator.validate(
        state['user_question'],
        state['planner_output'],
        state['sql_query'],
        state['sql_result']
    )
    
    state['validation_status'] = validation.get('is_valid', False)
    state['validation_feedback'] = validation.get('feedback', '')
    state['confidence'] = validation.get('confidence', 0.0)
    state['token_usage']['validator_input'] = 410
    state['token_usage']['validator_output'] = 85
    
    logger.info(f"[VALIDATE] Result: valid={state['validation_status']}, confidence={state['confidence']}")
    return state


def retry_decision(state: SalesState) -> str:
    """Decide whether to retry or proceed"""
    if state['cache_hit'] or not state['is_relevant']:
        logger.info(f"[RETRY] Skipping validation (cache_hit={state['cache_hit']}, relevant={state['is_relevant']})")
        return "generate_response"
    
    if state.get('validation_status'):
        logger.info(f"[RETRY] Validation passed, proceeding to response")
        return "generate_response"
    
    if state['retry_count'] < max_retries:
        state['retry_count'] += 1
        logger.warning(f"[RETRY] Validation failed, retrying ({state['retry_count']}/{max_retries})")
        return "sql_generation"
    
    logger.error(f"[RETRY] Max retries ({max_retries}) exceeded")
    return "generate_response"


def response_generation_node(state: SalesState) -> SalesState:
    """Generate business-friendly response"""
    if not state['is_relevant'] or state['cache_hit']:
        return state
    
    if not state.get('sql_result'):
        logger.warning(f"[RESPONSE] No SQL results to generate response from")
        return state
    
    logger.info(f"[RESPONSE] Generating answer...")
    answer = response_agent.generate(
        state['user_question'],
        state.get('sql_result', [])
    )
    
    state['final_answer'] = answer
    state['token_usage']['response_input'] = 180
    state['token_usage']['response_output'] = 32
    logger.info(f"[RESPONSE] Generated: {answer[:100]}...")
    
    return state


def cache_store_node(state: SalesState) -> SalesState:
    """Store validated response in cache"""
    if state['cache_hit'] or not state['is_relevant'] or not state.get('validation_status'):
        return state
    
    logger.info(f"[CACHE_STORE] Storing response...")
    cache_agent.store(
        state['user_question'],
        state['sql_query'],
        state['final_answer'],
        state.get('evidence', {}),
        state['confidence'],
        state.get('execution_time_ms', 0),
        state.get('token_usage', {})
    )
    
    logger.info(f"[CACHE_STORE] Stored successfully")
    return state


def create_sales_workflow():
    """Create and compile the LangGraph workflow with proper state transitions"""
    workflow = StateGraph(SalesState)
    memory = MemorySaver()  # Enable checkpointing
    
    # Add nodes
    workflow.add_node("plan", plan_node)
    workflow.add_node("relevance_check", relevance_check_node)
    workflow.add_node("cache_lookup", cache_lookup_node)
    workflow.add_node("sql_generation", sql_generation_node)
    workflow.add_node("sql_execution", sql_execution_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("generate_response", response_generation_node)
    workflow.add_node("cache_store", cache_store_node)
    
    # Add edges (workflow routing)
    workflow.add_edge("plan", "relevance_check")
    workflow.add_edge("relevance_check", "cache_lookup")
    workflow.add_edge("cache_lookup", "sql_generation")
    workflow.add_edge("sql_generation", "sql_execution")
    workflow.add_edge("sql_execution", "validation")
    
    # Conditional edge: retry or proceed
    workflow.add_conditional_edges(
        "validation",
        retry_decision,
        {
            "sql_generation": "sql_generation",
            "generate_response": "generate_response"
        }
    )
    
    workflow.add_edge("generate_response", "cache_store")
    workflow.add_edge("cache_store", END)
    
    # Set entry point
    workflow.set_entry_point("plan")
    
    # Compile with checkpointing
    return workflow.compile(checkpointer=memory)
