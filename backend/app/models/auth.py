from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")
    permissions: Mapped[list["Permission"]] = relationship("Permission", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("roles.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    role: Mapped[Optional["Role"]] = relationship("Role", back_populates="users")
    table_access: Mapped[list["UserTableAccess"]] = relationship("UserTableAccess", back_populates="user")
    query_history: Mapped[list["QueryHistory"]] = relationship("QueryHistory", back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user")


class Permission(Base):
    """Data-driven RBAC: one row per (role, table) pair."""
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    allowed_operations: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    # NULL = all columns allowed
    allowed_columns: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)

    role: Mapped["Role"] = relationship("Role", back_populates="permissions")


class UserTableAccess(Base):
    """Direct per-user table permissions — used when a user has no role."""
    __tablename__ = "user_table_access"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    allowed_operations: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="table_access")


class QueryHistory(Base):
    __tablename__ = "query_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    natural_language_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    sql_query: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    rows_returned: Mapped[Optional[int]] = mapped_column(Integer)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="query_history")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    operation_type: Mapped[Optional[str]] = mapped_column(String(20))
    tables_involved: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    was_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    block_reason: Mapped[Optional[str]] = mapped_column(Text)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    rows_affected: Mapped[Optional[int]] = mapped_column(Integer)

    user: Mapped["User"] = relationship("User", back_populates="audit_logs")
