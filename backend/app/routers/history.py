from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auth import AuditLog, QueryHistory, User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/history", tags=["history"])


class QueryHistoryOut(BaseModel):
    id: int
    natural_language_prompt: str
    sql_query: str
    explanation: str | None
    rows_returned: int | None
    executed_at: str

    class Config:
        from_attributes = True


class AuditLogOut(BaseModel):
    id: int
    query_text: str
    operation_type: str | None
    tables_involved: list[str] | None
    was_allowed: bool
    block_reason: str | None
    executed_at: str
    rows_affected: int | None

    class Config:
        from_attributes = True


@router.get("/queries", response_model=list[QueryHistoryOut])
def get_query_history(
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(QueryHistory)
        .filter(QueryHistory.user_id == current_user.id)
        .order_by(QueryHistory.executed_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        QueryHistoryOut(
            id=r.id,
            natural_language_prompt=r.natural_language_prompt,
            sql_query=r.sql_query,
            explanation=r.explanation,
            rows_returned=r.rows_returned,
            executed_at=r.executed_at.isoformat(),
        )
        for r in rows
    ]


@router.get("/audit", response_model=list[AuditLogOut])
def get_audit_log(
    limit: int = Query(100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the current user's own audit trail. Admins see all entries."""
    role_name = current_user.role.name if current_user.role else ""
    q = db.query(AuditLog)
    if role_name != "admin":
        q = q.filter(AuditLog.user_id == current_user.id)
    rows = q.order_by(AuditLog.executed_at.desc()).offset(offset).limit(limit).all()
    return [
        AuditLogOut(
            id=r.id,
            query_text=r.query_text,
            operation_type=r.operation_type,
            tables_involved=r.tables_involved,
            was_allowed=r.was_allowed,
            block_reason=r.block_reason,
            executed_at=r.executed_at.isoformat(),
            rows_affected=r.rows_affected,
        )
        for r in rows
    ]
