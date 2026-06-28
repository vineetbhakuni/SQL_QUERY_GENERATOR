import re

import sqlglot
import sqlglot.expressions as exp
from sqlalchemy import text
from sqlalchemy.orm import Session


def analyze_impact(sql: str, db: Session) -> dict:
    """
    For SELECT: run EXPLAIN and extract estimated rows.
    For UPDATE/DELETE: build a SELECT COUNT(*) with the same WHERE clause.
    Returns {"estimated_rows": int | None, "is_risky": bool, "risk_reason": str | None}
    """
    try:
        tree = sqlglot.parse_one(sql, dialect="postgres")
    except Exception:
        return {"estimated_rows": None, "is_risky": False, "risk_reason": None}

    is_risky = False
    risk_reason = None

    if isinstance(tree, exp.Select):
        estimated = _explain_row_estimate(sql, db)
        return {"estimated_rows": estimated, "is_risky": False, "risk_reason": None}

    if isinstance(tree, (exp.Update, exp.Delete)):
        where_clause = tree.find(exp.Where)
        if where_clause is None:
            is_risky = True
            risk_reason = f"{type(tree).__name__.upper()} without a WHERE clause — would affect ALL rows"

        count_sql = _build_count_query(tree)
        if count_sql:
            try:
                result = db.execute(text(count_sql))
                row = result.fetchone()
                estimated = row[0] if row else None
            except Exception:
                db.rollback()
                estimated = None
        else:
            estimated = None

        if estimated is not None and estimated > 100 and not is_risky:
            is_risky = True
            risk_reason = f"Operation would modify {estimated} rows — please review carefully"

        return {
            "estimated_rows": estimated,
            "is_risky": is_risky,
            "risk_reason": risk_reason,
        }

    return {"estimated_rows": None, "is_risky": False, "risk_reason": None}


def _explain_row_estimate(sql: str, db: Session) -> int | None:
    try:
        result = db.execute(text(f"EXPLAIN {sql}"))
        for row in result:
            m = re.search(r"rows=(\d+)", row[0])
            if m:
                return int(m.group(1))
    except Exception:
        db.rollback()  # reset aborted transaction so subsequent db ops still work
    return None


def _build_count_query(tree: exp.Expression) -> str | None:
    """Generate SELECT COUNT(*) FROM <table> WHERE <same condition>."""
    try:
        if isinstance(tree, exp.Update):
            table = tree.find(exp.Table)
            where = tree.find(exp.Where)
        elif isinstance(tree, exp.Delete):
            table = tree.find(exp.Table)
            where = tree.find(exp.Where)
        else:
            return None

        if table is None:
            return None

        table_name = table.name
        where_sql = f" WHERE {where.this.sql(dialect='postgres')}" if where else ""
        return f"SELECT COUNT(*) FROM {table_name}{where_sql}"
    except Exception:
        return None
