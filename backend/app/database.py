from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Supabase requires SSL; psycopg2 respects sslmode in the URL or connect_args.
_connect_args = {}
if "supabase" in settings.DATABASE_URL:
    _connect_args = {"sslmode": "require"}

engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
