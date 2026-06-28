import json
import re

import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel(settings.GEMINI_MODEL)

SYSTEM_PROMPT = """You are an expert SQL assistant. Given a natural-language request and a PostgreSQL schema, produce one or more SQL query candidates.

Rules:
- Only use tables and columns that exist in the provided schema.
- For ambiguous requests, return multiple labeled candidates.
- For each candidate, produce a JSON object with these fields:
    label: short name (e.g. "Option A")
    sql: the SQL statement (no semicolons at the end)
    explanation: plain English description of what the query does
    tables_involved: list of table names used
    columns_involved: list of "table.column" strings used
    operation_type: one of SELECT | INSERT | UPDATE | DELETE
    is_risky: true if the query modifies/deletes data without a WHERE clause or affects many rows
- Return ONLY a JSON array of candidate objects. No prose outside the JSON.
- Never include semicolons inside the SQL string.
- Do not hallucinate column or table names not present in the schema.
"""


def _extract_json(text: str) -> list[dict]:
    """Pull a JSON array out of the model response (strip markdown fences)."""
    text = text.strip()
    # Strip markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
    return json.loads(text)


def generate_candidates(
    user_prompt: str,
    schema_text: str,
    intent_hint: str = "",
) -> list[dict]:
    """Call Gemini and return a list of query candidate dicts."""
    prompt = f"""{SYSTEM_PROMPT}

{schema_text}

User request: {user_prompt}
{f'Intent hint: {intent_hint}' if intent_hint else ''}

Return the JSON array now:"""

    response = _model.generate_content(prompt)
    candidates = _extract_json(response.text)
    if not isinstance(candidates, list):
        candidates = [candidates]
    return candidates


def detect_intent(user_prompt: str) -> str:
    """Classify the prompt as read / write / ambiguous."""
    prompt = (
        "Classify this database request as one word: read, write, or ambiguous.\n"
        f"Request: {user_prompt}\nAnswer:"
    )
    resp = _model.generate_content(prompt)
    word = resp.text.strip().lower().split()[0]
    if word in ("read", "write", "ambiguous"):
        return word
    return "ambiguous"
