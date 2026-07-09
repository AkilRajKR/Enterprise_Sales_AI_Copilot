"""
privacy_guard.py
----------------
Blocks or sanitizes queries that attempt to expose personal customer data.

Personal data categories protected:
  - Names / full names
  - Date of birth / age (specific individual)
  - Salary / income / financial records
  - Address / location (individual level)
  - Phone / email / contact
  - Government IDs (SSN, passport, license)
  - Credit card / bank account numbers

Behaviour:
  - If a query is detected as requesting personal data → returns a
    structured block response immediately (no LLM call).
  - SQL results are also scrubbed: columns matching PII patterns are
    replaced with "*** PROTECTED ***".
"""

import logging
import re
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

# ── Keyword patterns that trigger a PII block ─────────────────────────────────
_PII_QUESTION_PATTERNS: List[re.Pattern] = [
    # Names (e.g. customer name, customer's name, client's names, client name, person name)
    re.compile(r"\b(customer|client|person|people|user|buyer|ownership)?'?s?\s*(names?|first_?names?|last_?names?|full_?names?|person_?names?)\b", re.I),
    # DOB / age of specific person
    re.compile(r"\b(date[\s_]*of[\s_]*births?|dob|birth[\s_]*dates?|birthdates?|birthdays?)\b", re.I),
    # Salary / income
    re.compile(r"\b(salar(y|ies)|incomes?|earnings?|wages?|compensations?|pay[\s_]?slips?)\b", re.I),
    # Address / location (individual)
    re.compile(r"\b(customer|client|person)?'?s?\s*(home[\s_]*address(es)?|residential[\s_]*address(es)?|street[\s_]*address(es)?|postal[\s_]*address(es)?|zip[\s_]*codes?)\b", re.I),
    # Contact
    re.compile(r"\b(phone[\s_]*numbers?|mobiles?|telephones?|emails?|email[\s_]*address(es)?|contact[\s_]*(details?|info|numbers?))\b", re.I),
    # Gov IDs
    re.compile(r"\b(ssn|social[\s_]*security|passport[\s_]*numbers?|national[\s_]*ids?|driving[\s_]*licenses?|driver[\s_]*licenses?)\b", re.I),
    # Financial IDs
    re.compile(r"\b(credit[\s_]*cards?|bank[\s_]*accounts?|account[\s_]*numbers?|ibans?|routing[\s_]*numbers?)\b", re.I),
]

# ── SQL column name patterns to scrub from results ────────────────────────────
_PII_COLUMN_PATTERNS: List[re.Pattern] = [
    re.compile(r"^(full_?name|first_?name|last_?name|customer_?name|client_?name|person_?name|name)$", re.I),
    re.compile(r"^(dob|date_?of_?birth|birth_?date|birthdate)$", re.I),
    re.compile(r"^(salary|income|earnings|wage)$", re.I),
    re.compile(r"^(address|street|city_detail|zip|postal_?code|home_address)$", re.I),
    re.compile(r"^(phone|mobile|telephone|email|contact)$", re.I),
    re.compile(r"^(ssn|social_security|passport|national_id|license_number|driver_license)$", re.I),
    re.compile(r"^(credit_card|bank_account|account_number|iban)$", re.I),
]

_BLOCK_RESPONSE = (
    "🔒 **Privacy Protection Active**\n\n"
    "This query appears to request personal customer information such as names, "
    "dates of birth, contact details, financial data, or government identification numbers.\n\n"
    "For compliance with data privacy regulations (GDPR / PDPA), individual customer "
    "personal details are **protected** and cannot be retrieved or displayed.\n\n"
    "You may query **aggregated** or **anonymised** metrics instead — for example:\n"
    "• Total customer count by region\n"
    "• Sales volume by brand or model\n"
    "• Dealer performance rankings\n"
    "• Vehicle ownership statistics"
)


# ── Public API ────────────────────────────────────────────────────────────────

def is_pii_question(question: str) -> Tuple[bool, str]:
    """
    Check whether a natural-language question is requesting PII.

    Returns:
        (is_blocked, reason_description)
    """
    for pattern in _PII_QUESTION_PATTERNS:
        m = pattern.search(question)
        if m:
            logger.warning(f"[PRIVACY] PII pattern matched: '{m.group()}' in question: {question!r}")
            return True, m.group()
    return False, ""


def get_block_response() -> Dict[str, Any]:
    """
    Return a structured workflow-compatible block response.
    This mimics the shape of a normal SalesState final answer.
    """
    return {
        "is_relevant":        True,
        "final_answer":       _BLOCK_RESPONSE,
        "sql_query":          "",
        "sql_result":         [],
        "evidence":           {},
        "confidence":         1.0,   # confident in the block decision
        "validation_status":  True,
        "validation_feedback": "Privacy guard blocked this query.",
        "cache_hit":          False,
        "retry_count":        0,
        "token_usage":        {},
        "execution_time_ms":  0.0,
        "privacy_blocked":    True,
    }


def scrub_pii_from_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove PII column values from SQL result rows.
    Replaces protected column values with '*** PROTECTED ***'.
    """
    if not results:
        return results

    # Determine which columns to scrub
    sample = results[0]
    cols_to_scrub = {
        col for col in sample.keys()
        if any(pat.match(col) for pat in _PII_COLUMN_PATTERNS)
    }

    if not cols_to_scrub:
        return results

    logger.warning(f"[PRIVACY] Scrubbing PII columns from results: {cols_to_scrub}")

    scrubbed = []
    for row in results:
        new_row = dict(row)
        for col in cols_to_scrub:
            if col in new_row:
                new_row[col] = "*** PROTECTED ***"
        scrubbed.append(new_row)
    return scrubbed
