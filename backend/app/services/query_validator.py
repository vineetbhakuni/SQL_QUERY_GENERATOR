import re

import sqlglot


def validate_sql(sql: str) -> dict:
    errors: list[str] = []
    suggestions: list[str] = []

    try:
        statements = sqlglot.parse(sql, dialect="postgres", error_level=sqlglot.ErrorLevel.RAISE)
    except sqlglot.errors.ParseError as e:
        for err in e.errors:
            errors.append(err.get("description", str(err)))
        return {"valid": False, "errors": errors, "suggestions": suggestions}

    if not statements:
        return {"valid": False, "errors": ["Empty or unrecognised SQL"], "suggestions": suggestions}

    if "SELECT *" in sql.upper():
        suggestions.append("Consider selecting specific columns instead of SELECT * for better performance.")

    if re.search(r"LIKE\s+'%[^%]", sql, re.IGNORECASE):
        suggestions.append("Leading wildcard in LIKE ('%...') prevents index use; consider full-text search instead.")

    return {"valid": True, "errors": [], "suggestions": suggestions}
