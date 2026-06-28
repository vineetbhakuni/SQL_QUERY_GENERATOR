-- Migration: add user_table_access for direct per-user table permissions
-- Run this in your database (Supabase SQL Editor or psql).
--
-- New users registered through the UI will get rows here instead of a role.
-- Existing demo users (viewer_user, analyst_user, admin_user) keep their
-- role-based permissions unchanged.

CREATE TABLE IF NOT EXISTS user_table_access (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    table_name          VARCHAR(100) NOT NULL,
    allowed_operations  TEXT[] NOT NULL DEFAULT ARRAY['SELECT'],
    UNIQUE (user_id, table_name)
);
