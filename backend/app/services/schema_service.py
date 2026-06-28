from sqlalchemy import inspect

from app.database import engine

_USER_SCHEMA = "public"

_EXCLUDED_TABLES = {
    # Supabase internal tables
    "schema_migrations", "buckets", "objects", "hooks", "extensions",
    # VINEETSQL auth tables — never expose to the LLM
    "users", "roles", "permissions", "audit_log", "query_history",
}


def get_schema_info() -> dict:
    """Introspect the live DB and return tables/columns/FK relationships."""
    inspector = inspect(engine)
    schema: dict = {}

    for table_name in inspector.get_table_names(schema=_USER_SCHEMA):
        if table_name in _EXCLUDED_TABLES:
            continue

        columns = []
        for col in inspector.get_columns(table_name, schema=_USER_SCHEMA):
            columns.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
            })

        fks = []
        for fk in inspector.get_foreign_keys(table_name, schema=_USER_SCHEMA):
            fks.append({
                "column": fk["constrained_columns"],
                "references": f"{fk['referred_table']}.{fk['referred_columns']}",
            })

        pks = inspector.get_pk_constraint(table_name, schema=_USER_SCHEMA).get("constrained_columns", [])

        schema[table_name] = {
            "columns": columns,
            "primary_keys": pks,
            "foreign_keys": fks,
        }

    return schema


def schema_to_prompt_text(schema: dict) -> str:
    """Render schema dict as compact DDL-like text for an LLM prompt."""
    lines = ["Database schema (PostgreSQL):"]
    for table, info in schema.items():
        col_defs = []
        for c in info["columns"]:
            nullable = "" if c["nullable"] else " NOT NULL"
            pk = " [PK]" if c["name"] in info["primary_keys"] else ""
            col_defs.append(f"  {c['name']} {c['type']}{nullable}{pk}")
        lines.append(f"\nTable {table}:")
        lines.extend(col_defs)
        for fk in info["foreign_keys"]:
            lines.append(f"  FK {fk['column']} -> {fk['references']}")
    return "\n".join(lines)
