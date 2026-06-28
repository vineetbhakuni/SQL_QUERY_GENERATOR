from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from app.database import engine, Base
from app.models import auth, business
from app.routers import auth as auth_router
from app.routers import history as history_router
from app.routers import query as query_router

# Verify connectivity and ensure all SQLAlchemy tables exist at startup.
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    Base.metadata.create_all(bind=engine)
except Exception as exc:
    raise RuntimeError(
        f"Cannot connect to or initialize the database. Check DATABASE_URL in .env.\n{exc}"
    ) from exc

app = FastAPI(
    title="VINEETSQL - AI SQL Query Generator",
    description="Natural-language SQL assistant with role-based access control",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(query_router.router)
app.include_router(history_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}
