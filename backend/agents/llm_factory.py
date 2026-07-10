"""
llm_factory.py
--------------
Central factory for creating Gemini LLM instances with automatic fallback.

Model priority order (all free tier):
  1. GEMINI_MODEL (from .env)                   — primary
  2. GEMINI_FALLBACK_MODEL (from .env)          — secondary
  3. "gemini-2.5-flash"                         — fallback safety net 1
  4. "gemini-2.0-flash"                         — fallback safety net 2
  5. "gemini-flash-latest"                      — fallback safety net 3
"""

import logging
import os
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

# ── Model preference list ────────────────────────────────────────────────────
# Lower index = higher preference. We stop at the first one that works.
_FREE_TIER_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.0-flash"),
    "gemini-2.5-flash",           # safety nets
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]


def _deduplicated_models() -> list[str]:
    """Return unique models preserving order."""
    seen: set = set()
    result = []
    for m in _FREE_TIER_MODELS:
        if m and m not in seen:
            seen.add(m)
            result.append(m)
    return result


ORDERED_MODELS = _deduplicated_models()


def build_llm(
    api_key: str,
    temperature: float = 0.1,
    max_tokens: int = 500,
    model_index: int = 0,
) -> tuple[ChatGoogleGenerativeAI, str]:
    """
    Build a ChatGoogleGenerativeAI instance.

    Returns (llm, model_name).
    model_index 0 = primary, 1 = first fallback, etc.
    Raises IndexError if model_index exceeds available models.
    """
    model = ORDERED_MODELS[model_index % len(ORDERED_MODELS)]
    logger.info(f"[LLM_FACTORY] Using model: {model} (index={model_index})")
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        max_retries=0,
    )
    return llm, model


_last_working_index = 0


def invoke_with_fallback(
    chain_builder,          # callable(llm) -> runnable chain
    invoke_kwargs: dict,
    api_key: str,
    temperature: float = 0.1,
    max_tokens: int = 500,
):
    """
    Invoke a LangChain chain with automatic model fallback on any error (quota, 404, etc).

    Args:
        chain_builder: A callable that accepts an `llm` and returns a chain.
        invoke_kwargs:  kwargs to pass to chain.invoke().
        api_key:        Gemini API key.
        temperature:    LLM temperature.
        max_tokens:     Max output tokens.

    Returns:
        (response, model_name_used)
    """
    global _last_working_index
    last_error: Optional[Exception] = None
    num_models = len(ORDERED_MODELS)

    for i in range(num_models):
        idx = (_last_working_index + i) % num_models
        model_name = ORDERED_MODELS[idx]
        try:
            llm, model_name = build_llm(api_key, temperature, max_tokens, idx)
            chain = chain_builder(llm)
            response = chain.invoke(invoke_kwargs)
            
            if idx != _last_working_index:
                logger.warning(
                    f"[LLM_FACTORY] Succeeded with fallback: {model_name} (idx {idx}). "
                    f"Updating last working index from {_last_working_index} to {idx}."
                )
                _last_working_index = idx
                
            return response, model_name

        except Exception as exc:
            err_str = str(exc)
            logger.warning(
                f"[LLM_FACTORY] Model '{model_name}' failed with error: {err_str[:200]}... "
                f"Trying next model in list."
            )
            last_error = exc
            continue   # try next model

    # All models exhausted
    logger.error("[LLM_FACTORY] All models exhausted. Raising last error.")
    raise last_error


def extract_text_content(response) -> str:
    """
    Safely extract string content from any ChatGoogleGenerativeAI response,
    supporting both string content and list of content parts.
    """
    if response is None:
        return ""
    
    # Check if we have an AIMessage or similar with a .content attribute
    content = getattr(response, "content", response)
    
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
            elif hasattr(part, "text"):
                parts.append(part.text)
            elif isinstance(part, str):
                parts.append(part)
        return "".join(parts).strip()
    
    return str(content).strip()
