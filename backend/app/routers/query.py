from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auth import QueryHistory, User
from app.routers.auth import get_current_user
from app.services.authorization import check_authorization
from app.services.impact_analyzer import analyze_impact
from app.services.llm_service import detect_intent, generate_candidates
from app.services.query_validator import validate_sql
from app.services.schema_service import get_schema_info, schema_to_prompt_text

router = APIRouter(prefix="/query", tags=["query"])


# ── Schemas ─────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    prompt: str


class Candidate(BaseModel):
    label: str
    sql: str
    explanation: str
    tables_involved: list[str]
    columns_involved: list[str]
    operation_type: str
    is_risky: bool
    validation: dict
    impact: dict
    authorization: dict


class GenerateResponse(BaseModel):
    intent: str
    candidates: list[Candidate]


class ExecuteRequest(BaseModel):
    sql: str


class ExecuteResponse(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    rows_returned: int
    message: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateResponse)
def generate(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        schema = get_schema_info()
        schema_text = schema_to_prompt_text(schema)
    except Exception as e:
        raise HTTPException(500, f"Schema introspection failed: {e}")

    try:
        intent = detect_intent(req.prompt)
    except Exception as e:
        intent = "ambiguous"

    try:
        raw_candidates = generate_candidates(req.prompt, schema_text, intent)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    candidates: list[Candidate] = []
    for raw in raw_candidates:
        sql = raw.get("sql", "").strip()
        if not sql:
            continue

        validation = validate_sql(sql)
        impact = analyze_impact(sql, db) if validation["valid"] else {
            "estimated_rows": None, "is_risky": False, "risk_reason": None
        }
        auth = check_authorization(sql, current_user, db)

        candidates.append(Candidate(
            label=raw.get("label", "Option"),
            sql=sql,
            explanation=raw.get("explanation", ""),
            tables_involved=raw.get("tables_involved", []),
            columns_involved=raw.get("columns_involved", []),
            operation_type=raw.get("operation_type", "UNKNOWN"),
            is_risky=raw.get("is_risky", False) or impact.get("is_risky", False),
            validation=validation,
            impact=impact,
            authorization=auth,
        ))

    return GenerateResponse(intent=intent, candidates=candidates)


@router.post("/execute", response_model=ExecuteResponse)
def execute(
    req: ExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sql = req.sql.strip()

    # Re-validate and re-authorize before execution — never trust the client
    validation = validate_sql(sql)
    if not validation["valid"]:
        raise HTTPException(400, f"Invalid SQL: {validation['errors']}")

    auth = check_authorization(sql, current_user, db)
    if not auth["allowed"]:
        raise HTTPException(403, f"Not authorized: {auth['reason']}")

    try:
        result = db.execute(text(sql))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(400, f"SQL execution error: {e}")

    if result.returns_rows:
        column_names = list(result.keys())
        rows = [list(row) for row in result.fetchall()]
    else:
        column_names = ["rows_affected"]
        rows = [[result.rowcount]]

    rows_returned = len(rows)

    try:
        history = QueryHistory(
            user_id=current_user.id,
            natural_language_prompt="(direct execution)",
            sql_query=sql,
            rows_returned=rows_returned,
        )
        db.add(history)
        db.commit()
    except Exception:
        db.rollback()

    return ExecuteResponse(
        columns=column_names,
        rows=rows,
        rows_returned=rows_returned,
        message="Query executed successfully",
    )


@router.post("/generate-and-execute", response_model=ExecuteResponse)
def generate_and_execute(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Convenience: generate the first allowed candidate and execute it."""
    gen = generate(req, db, current_user)
    allowed = [c for c in gen.candidates if c.authorization["allowed"] and c.validation["valid"]]
    if not allowed:
        raise HTTPException(403, "No authorized and valid query could be generated")

    chosen = allowed[0]
    return execute(ExecuteRequest(sql=chosen.sql), db, current_user)
