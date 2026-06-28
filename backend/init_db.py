from pathlib import Path

from sqlalchemy import text

from app.database import Base, engine
from app.models import auth, business  # noqa: F401 - imported so metadata includes all models


BASE_DIR = Path(__file__).resolve().parent


def _execute_sql_file(filename: str) -> None:
    sql_path = BASE_DIR / filename
    sql = sql_path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)


def seed_data() -> None:
    print("Creating SQLAlchemy-managed tables...")
    Base.metadata.create_all(bind=engine)

    print("Loading business schema and sample HR data from seed.sql...")
    _execute_sql_file("seed.sql")

    print("Resetting role permissions to avoid duplicate permission rows...")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM permissions"))

    print("Loading RBAC roles, permissions, and demo users from rbac_seed.sql...")
    _execute_sql_file("rbac_seed.sql")

    print("Database initialization and seeding completed successfully!")


if __name__ == "__main__":
    seed_data()
