"""
llm_factory.py
--------------
Central factory for creating Gemini LLM instances with automatic fallback.

Model priority order (all free tier):
  1. GEMINI_MODEL (from .env)                   — primary
  2. GEMINI_FALLBACK_MODEL (from .env)          — secondary
  3. "gemini-1.5-flash"                         — hardcoded safety net

On 429 RESOURCE_EXHAUSTED the caller should catch the error and call
build_llm() again with use_fallback=True to obtain the fallback model.
"""

import logging
import os
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

# ── Model preference list ────────────────────────────────────────────────────
# Lower index = higher preference. We stop at the first one that works.
_FREE_TIER_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
    os.getenv("GEMINI_FALLBACK_MODEL", "gemini-1.5-flash-8b"),
    "gemini-1.5-flash",           # absolute safety net
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
    )
    return llm, model


def invoke_with_fallback(
    chain_builder,          # callable(llm) -> runnable chain
    invoke_kwargs: dict,
    api_key: str,
    temperature: float = 0.1,
    max_tokens: int = 500,
):
    """
    Invoke a LangChain chain with automatic model fallback on quota errors.

    Args:
        chain_builder: A callable that accepts an `llm` and returns a chain.
        invoke_kwargs:  kwargs to pass to chain.invoke().
        api_key:        Gemini API key.
        temperature:    LLM temperature.
        max_tokens:     Max output tokens.

    Returns:
        (response, model_name_used)
    """
    last_error: Optional[Exception] = None

    for idx, model_name in enumerate(ORDERED_MODELS):
        try:
            llm, model_name = build_llm(api_key, temperature, max_tokens, idx)
            chain = chain_builder(llm)
            response = chain.invoke(invoke_kwargs)
            if idx > 0:
                logger.warning(
                    f"[LLM_FACTORY] Primary model failed; succeeded with fallback: {model_name}"
                )
            return response, model_name

        except Exception as exc:
            err_str = str(exc)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                logger.warning(
                    f"[LLM_FACTORY] Quota exceeded for '{model_name}' "
                    f"(attempt {idx + 1}/{len(ORDERED_MODELS)}). Trying next model..."
                )
                last_error = exc
                continue   # try next model
            else:
                # Non-quota error — re-raise immediately
                raise

    # All models exhausted
    logger.error("[LLM_FACTORY] All models exhausted. Raising last error.")
    raise last_error
