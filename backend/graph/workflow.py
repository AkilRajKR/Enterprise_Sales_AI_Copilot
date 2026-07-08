import logging
import os
from datetime import datetime
from pathlib import Path
from langgraph.graph import StateGraph, END
from graph.state import SalesState
from agents.planner import PlannerAgent
from agents.sql_agent import SQLAgent
from agents.validator import ValidatorAgent
from agents.response import ResponseAgent
from agents.cache import CacheAgent
from agents.privacy_guard import is_pii_question, get_block_response, scrub_pii_from_results
from dotenv import load_dotenv
import time

# ── Load .env from project root (works regardless of cwd) ────────────────────
_base = Path(__file__).resolve().parent.parent.parent  # project root
load_dotenv(dotenv_path=_base / ".env")

logger = logging.getLogger(__name__)

api_key  = os.getenv("GEMINI_API_KEY")
db_path  = os.getenv("DATABASE_PATH", "database/sales.db")
max_retries = int(os.getenv("MAX_RETRIES", 4))

planner        = PlannerAgent(api_key)
sql_agent      = SQLAgent(api_key, db_path)
validator      = ValidatorAgent(api_key)
response_agent = ResponseAgent(api_key)
cache_agent    = CacheAgent(db_path)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: extract token counts from a LangChain AIMessage
# ─────────────────────────────────────────────────────────────────────────────
def _extract_usage(response) -> dict:
    """Return input/output token counts from a LangChain AI message."""
    usage = {}
    try:
        meta = getattr(response, "usage_metadata", None)
        if meta:
            usage["input_tokens"]  = getattr(meta, "input_tokens",  0)
            usage["output_tokens"] = getattr(meta, "output_tokens", 0)
    except Exception:
        pass
    return usage


# ─────────────────────────────────────────────────────────────────────────────
# Node 1 — Planner
# ─────────────────────────────────────────────────────────────────────────────
def plan_node(state: SalesState) -> SalesState:
    """Classify question and decompose intent."""
    logger.info(f"[PLAN] Processing: {state['user_question']}")

    planner_output, usage = planner.classify_with_usage(state["user_question"])

    logger.info("=" * 80)
    logger.info(f"Planner Output:\n{planner_output}")
    logger.info("=" * 80)

    state["planner_output"] = planner_output
    state["is_relevant"]    = planner_output.get("is_relevant", True)  # use Gemini's decision

    # Accumulate real token usage
    state["token_usage"]["planner_input"]  = usage.get("input_tokens", 0)
    state["token_usage"]["planner_output"] = usage.get("output_tokens", 0)

    logger.info(
        f"[PLAN] Result: relevant={state['is_relevant']}, "
        f"intent={planner_output.get('intent')}"
    )
    return state


# ─────────────────────────────────────────────────────────────────────────────
# Node 2 — Privacy guard
# ─────────────────────────────────────────────────────────────────────────────
def privacy_guard_node(state: SalesState) -> SalesState:
    """Block queries that request personal customer data (PII)."""
    if not state.get("is_relevant", True):
        return state

    blocked, reason = is_pii_question(state["user_question"])
    if blocked:
        logger.warning(f"[PRIVACY] Query blocked — PII pattern: {reason!r}")
        block = get_block_response()
        state["final_answer"]      = block["final_answer"]
        state["confidence"]        = block["confidence"]
        state["validation_status"] = block["validation_status"]
        state["is_relevant"]       = False   # short-circuit the rest of the pipeline
    else:
        logger.info("[PRIVACY] Query passed privacy check.")
    return state


# ─────────────────────────────────────────────────────────────────────────────
# Node 3 — Relevance check
# ─────────────────────────────────────────────────────────────────────────────
def relevance_check_node(state: SalesState) -> SalesState:
    """Gate irrelevant questions with a friendly message."""
    if not state.get("is_relevant", True):
        logger.warning("[RELEVANCE] Question is not sales-related — rejecting.")
        state["final_answer"] = (
            "I can only answer questions about the automotive sales database "
            "(brands, models, customers, dealers, vehicles, manufacturing plants). "
            "Please rephrase your question."
        )
        state["confidence"]        = 0.0
        state["validation_status"] = True   # treat as handled
    else:
        logger.info("[RELEVANCE] Question accepted.")
    return state


# ─────────────────────────────────────────────────────────────────────────────
# Node 3 — Cache lookup
# ─────────────────────────────────────────────────────────────────────────────
def cache_lookup_node(state: SalesState) -> SalesState:
    """Check cache for existing answer."""
    if not state.get("is_relevant", True):
        return state

    logger.info(f"[CACHE] Looking up: {state['user_question']}")
    cached = cache_agent.get(state["user_question"])

    if cached:
        state["cache_hit"]         = True
        state["cached_answer"]     = cached
        state["final_answer"]      = cached["answer"]
        state["sql_query"]         = cached["sql_query"]
        state["evidence"]          = cached["evidence"]
        state["confidence"]        = cached["confidence"]
        state["token_usage"]       = cached["token_usage"]
        state["validation_status"] = True
        logger.info(f"[CACHE] HIT — confidence: {cached['confidence']}")
    else:
        logger.info("[CACHE] MISS")

    return state


# ─────────────────────────────────────────────────────────────────────────────
# Conditional after cache_lookup — skip SQL pipeline on hit
# ─────────────────────────────────────────────────────────────────────────────
def after_cache(state: SalesState) -> str:
    if state.get("cache_hit") or not state.get("is_relevant", True):
        return "generate_response"
    return "sql_generation"


# ─────────────────────────────────────────────────────────────────────────────
# Node 4 — SQL generation
# ─────────────────────────────────────────────────────────────────────────────
def sql_generation_node(state: SalesState) -> SalesState:
    """Generate SQL query via Gemini."""
    if state.get("cache_hit") or not state.get("is_relevant", True):
        return state

    logger.info("[SQL_GEN] Generating SQL...")

    sql_query, usage = sql_agent.generate_query_with_usage(
        state["user_question"],
        state["planner_output"],
    )

    if not sql_query:
        logger.error("[SQL_GEN] SQL generation failed")
        state["validation_status"] = False
        state["confidence"]        = 0.0
        state["final_answer"]      = "Unable to generate a SQL query for this question."
        return state

    logger.info("=" * 80)
    logger.info("[SQL_GEN] Generated SQL")
    logger.info(sql_query)
    logger.info("=" * 80)

    state["sql_query"] = sql_query
    state["token_usage"]["sql_input"]  = usage.get("input_tokens",  0)
    state["token_usage"]["sql_output"] = usage.get("output_tokens", 0)

    return state


# ─────────────────────────────────────────────────────────────────────────────
# Node 5 — SQL execution
# ─────────────────────────────────────────────────────────────────────────────
def sql_execution_node(state: SalesState) -> SalesState:
    """Execute the generated SQL query and store results."""
    if state.get("cache_hit"):
        logger.info("[SQL_EXEC] Skipped (cache hit)")
        return state

    if not state.get("is_relevant", True):
        logger.info("[SQL_EXEC] Skipped (question marked irrelevant)")
        return state

    if not state.get("sql_query"):
        logger.warning("[SQL_EXEC] No SQL query available")
        return state

    try:
        logger.info("=" * 80)
        logger.info("[SQL_EXEC] Executing SQL")
        logger.info(state["sql_query"])
        logger.info("=" * 80)

        results = sql_agent.execute_query(state["sql_query"])

        # ── Scrub PII columns from raw SQL results ───────────────────────────
        results = scrub_pii_from_results(results)

        state["sql_result"] = results

        logger.info(f"[SQL_EXEC] Rows returned: {len(results)}")
        if results:
            logger.info("[SQL_EXEC] First 5 rows:")
            logger.info(results[:5])
        else:
            logger.warning("[SQL_EXEC] Query returned no rows.")

        return state

    except Exception as e:
        logger.exception("[SQL_EXEC] SQL execution failed")
        state["sql_result"]        = []
        state["validation_status"] = False
        state["confidence"]        = 0.0
        state["final_answer"]      = f"SQL execution failed: {str(e)}"
        return state


# ─────────────────────────────────────────────────────────────────────────────
# Node 6 — Validation
# ─────────────────────────────────────────────────────────────────────────────
def validation_node(state: SalesState) -> SalesState:
    """Validate SQL results via Gemini."""
    if state.get("cache_hit") or not state.get("is_relevant", True):
        return state

    if not state.get("sql_result"):
        logger.warning("[VALIDATE] No results to validate — marking as failed")
        state["validation_status"] = False
        state["confidence"]        = 0.0
        state["final_answer"] = (
            "The query returned no data. "
            "Try rephrasing your question or check that the relevant data exists."
        )
        return state

    logger.info(
        f"[VALIDATE] Validating results "
        f"(attempt {state['retry_count'] + 1}/{max_retries})"
    )

    validation, usage = validator.validate_with_usage(
        state["user_question"],
        state["planner_output"],
        state["sql_query"],
        state["sql_result"],
    )

    state["validation_status"]  = validation.get("is_valid", False)
    state["validation_feedback"] = validation.get("feedback", "")
    state["confidence"]          = validation.get("confidence", 0.0)
    state["token_usage"]["validator_input"]  = usage.get("input_tokens",  0)
    state["token_usage"]["validator_output"] = usage.get("output_tokens", 0)

    logger.info(
        f"[VALIDATE] valid={state['validation_status']}, "
        f"confidence={state['confidence']}"
    )
    return state


# ─────────────────────────────────────────────────────────────────────────────
# Conditional — retry or proceed
# ─────────────────────────────────────────────────────────────────────────────
def retry_decision(state: SalesState) -> str:
    if state.get("cache_hit") or not state.get("is_relevant", True):
        logger.info(
            f"[RETRY] Skipping "
            f"(cache_hit={state.get('cache_hit')}, relevant={state.get('is_relevant')})"
        )
        return "generate_response"

    if state.get("validation_status"):
        logger.info("[RETRY] Validation passed → response")
        return "generate_response"

    if state["retry_count"] < max_retries:
        state["retry_count"] += 1
        logger.warning(
            f"[RETRY] Validation failed → retrying "
            f"({state['retry_count']}/{max_retries})"
        )
        return "sql_generation"

    logger.error(f"[RETRY] Max retries ({max_retries}) exceeded → response anyway")
    return "generate_response"


# ─────────────────────────────────────────────────────────────────────────────
# Node 7 — Response generation
# ─────────────────────────────────────────────────────────────────────────────
def response_generation_node(state: SalesState) -> SalesState:
    """Generate a business-friendly natural language response."""
    # Already answered (irrelevant question, cache hit, or empty-result fallback)
    if state.get("final_answer"):
        return state

    if not state.get("sql_result"):
        state["final_answer"] = (
            "No data was found for your query. "
            "Please try a different question or check that the data exists."
        )
        logger.warning("[RESPONSE] No SQL results — returning fallback answer")
        return state

    logger.info("[RESPONSE] Generating answer...")
    answer, usage = response_agent.generate_with_usage(
        state["user_question"],
        state.get("sql_result", []),
    )

    state["final_answer"] = answer
    state["token_usage"]["response_input"]  = usage.get("input_tokens",  0)
    state["token_usage"]["response_output"] = usage.get("output_tokens", 0)
    logger.info(f"[RESPONSE] Generated: {answer[:120]}...")

    return state


# ─────────────────────────────────────────────────────────────────────────────
# Node 8 — Cache store
# ─────────────────────────────────────────────────────────────────────────────
def cache_store_node(state: SalesState) -> SalesState:
    """Store validated response in cache."""
    if (
        state.get("cache_hit")
        or not state.get("is_relevant", True)
        or not state.get("validation_status")
        or "Unable to generate a response" in state.get("final_answer", "")
    ):
        return state

    logger.info("[CACHE_STORE] Storing response...")
    cache_agent.store(
        state["user_question"],
        state["sql_query"],
        state["final_answer"],
        state.get("evidence", {}),
        state["confidence"],
        state.get("execution_time_ms", 0),
        state.get("token_usage", {}),
    )
    logger.info("[CACHE_STORE] Stored successfully")
    return state


# ─────────────────────────────────────────────────────────────────────────────
# Graph factory
# ─────────────────────────────────────────────────────────────────────────────
def create_sales_workflow():
    """Create and compile the LangGraph workflow."""
    workflow = StateGraph(SalesState)

    # Register nodes
    workflow.add_node("plan",              plan_node)
    workflow.add_node("privacy_guard",     privacy_guard_node)
    workflow.add_node("relevance_check",   relevance_check_node)
    workflow.add_node("cache_lookup",      cache_lookup_node)
    workflow.add_node("sql_generation",    sql_generation_node)
    workflow.add_node("sql_execution",     sql_execution_node)
    workflow.add_node("validation",        validation_node)
    workflow.add_node("generate_response", response_generation_node)
    workflow.add_node("cache_store",       cache_store_node)

    # Linear edges
    workflow.add_edge("plan",            "privacy_guard")
    workflow.add_edge("privacy_guard",   "relevance_check")
    workflow.add_edge("relevance_check", "cache_lookup")

    # ✅ Skip SQL pipeline when cache hits or question is irrelevant
    workflow.add_conditional_edges(
        "cache_lookup",
        after_cache,
        {
            "sql_generation":    "sql_generation",
            "generate_response": "generate_response",
        },
    )

    workflow.add_edge("sql_generation", "sql_execution")
    workflow.add_edge("sql_execution",  "validation")

    # Conditional retry loop
    workflow.add_conditional_edges(
        "validation",
        retry_decision,
        {
            "sql_generation":    "sql_generation",
            "generate_response": "generate_response",
        },
    )

    workflow.add_edge("generate_response", "cache_store")
    workflow.add_edge("cache_store",       END)

    workflow.set_entry_point("plan")
    return workflow.compile()
