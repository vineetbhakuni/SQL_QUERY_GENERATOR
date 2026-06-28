from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.database import get_db
from app.models.auth import User, UserTableAccess

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Schemas ─────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    table_access: list[str]   # table names the user is allowed to SELECT


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    accessible_tables: list[str]


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    accessible_tables: list[str]

    class Config:
        from_attributes = True


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_accessible_tables(user: User) -> list[str]:
    """Return table names the user can access, from direct access or role permissions."""
    if user.table_access:
        return [ta.table_name for ta in user.table_access]
    if user.role and user.role.permissions:
        return [p.table_name for p in user.role.permissions]
    return []


# ── Dependency ───────────────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserOut, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if not req.table_access:
        raise HTTPException(400, "Select at least one table to access")
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(400, "Username already taken")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(400, "Email already registered")

    user = User(
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        role_id=None,
    )
    db.add(user)
    db.flush()  # get user.id before commit

    for table_name in req.table_access:
        db.add(UserTableAccess(
            user_id=user.id,
            table_name=table_name.lower(),
            allowed_operations=["SELECT"],
        ))

    db.commit()
    db.refresh(user)
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        accessible_tables=[ta.table_name for ta in user.table_access],
    )


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(
        {"sub": user.username},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        username=user.username,
        accessible_tables=_get_accessible_tables(user),
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        accessible_tables=_get_accessible_tables(current_user),
    )
