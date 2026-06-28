
CREATE TABLE IF NOT EXISTS roles (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(100) UNIQUE NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id       INTEGER REFERENCES roles(id),
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS permissions (
    id                  SERIAL PRIMARY KEY,
    role_id             INTEGER REFERENCES roles(id) NOT NULL,
    table_name          VARCHAR(100) NOT NULL,
    allowed_operations  TEXT[] NOT NULL,
    allowed_columns     TEXT[]
);

CREATE TABLE IF NOT EXISTS query_history (
    id                      SERIAL PRIMARY KEY,
    user_id                 INTEGER REFERENCES users(id) NOT NULL,
    natural_language_prompt TEXT NOT NULL,
    sql_query               TEXT NOT NULL,
    explanation             TEXT,
    rows_returned           INTEGER,
    executed_at             TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER REFERENCES users(id) NOT NULL,
    query_text       TEXT NOT NULL,
    operation_type   VARCHAR(20),
    tables_involved  TEXT[],
    was_allowed      BOOLEAN NOT NULL,
    block_reason     TEXT,
    executed_at      TIMESTAMPTZ DEFAULT NOW(),
    rows_affected    INTEGER
);

-- ── Roles ──────────────────────────────────────────────────

INSERT INTO roles (name, description) VALUES
    ('viewer',  'Read-only access to all HR tables'),
    ('analyst', 'Read and update access to HR tables'),
    ('admin',   'Full access to all HR tables')
ON CONFLICT (name) DO NOTHING;

-- ── Permissions ────────────────────────────────────────────

-- viewer: SELECT only, limited columns on sensitive tables
INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'employees',   ARRAY['SELECT'], ARRAY['employee_id','first_name','last_name','email','phone_number','hire_date','job_id','department_id','manager_id'] FROM roles WHERE name='viewer';

INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'departments', ARRAY['SELECT'], NULL FROM roles WHERE name='viewer';

INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'jobs',        ARRAY['SELECT'], NULL FROM roles WHERE name='viewer';

INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'locations',   ARRAY['SELECT'], NULL FROM roles WHERE name='viewer';

INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'countries',   ARRAY['SELECT'], NULL FROM roles WHERE name='viewer';

INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'regions',     ARRAY['SELECT'], NULL FROM roles WHERE name='viewer';

INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'dependents',  ARRAY['SELECT'], NULL FROM roles WHERE name='viewer';

-- analyst: SELECT + UPDATE on all HR tables (all columns)
INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'employees',   ARRAY['SELECT','UPDATE'], NULL FROM roles WHERE name='analyst';

INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'departments', ARRAY['SELECT','UPDATE'], NULL FROM roles WHERE name='analyst';

INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'jobs',        ARRAY['SELECT','UPDATE'], NULL FROM roles WHERE name='analyst';

INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'locations',   ARRAY['SELECT','UPDATE'], NULL FROM roles WHERE name='analyst';

INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'countries',   ARRAY['SELECT'], NULL FROM roles WHERE name='analyst';

INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'regions',     ARRAY['SELECT'], NULL FROM roles WHERE name='analyst';

INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, 'dependents',  ARRAY['SELECT','INSERT','UPDATE','DELETE'], NULL FROM roles WHERE name='analyst';

-- admin: full CRUD on all HR tables
INSERT INTO permissions (role_id, table_name, allowed_operations, allowed_columns)
SELECT id, t, ARRAY['SELECT','INSERT','UPDATE','DELETE'], NULL
FROM roles, unnest(ARRAY['employees','departments','jobs','locations','countries','regions','dependents']) AS t
WHERE name = 'admin';

-- ── Demo users ─────────────────────────────────────────────
-- viewer_user  / viewer123
-- analyst_user / analyst123
-- admin_user   / admin123

INSERT INTO users (username, email, password_hash, role_id, is_active)
SELECT 'viewer_user', 'viewer@vineetsql.local',
       '$2b$12$.55GMug3r/DZ.YrMwZxpQeYmKVZkNxJc/WP3y13orJ8ZMxy6W/R3i',
       (SELECT id FROM roles WHERE name='viewer'),
       TRUE
ON CONFLICT (username) DO NOTHING;

INSERT INTO users (username, email, password_hash, role_id, is_active)
SELECT 'analyst_user', 'analyst@vineetsql.local',
       '$2b$12$eDg5hrEjMxhXZKgW0UXjaOLVNPbuxqp1dCXUKRoa9VU5tS6CF5Ev6',
       (SELECT id FROM roles WHERE name='analyst'),
       TRUE
ON CONFLICT (username) DO NOTHING;

INSERT INTO users (username, email, password_hash, role_id, is_active)
SELECT 'admin_user', 'admin@vineetsql.local',
       '$2b$12$V1nU6Kq5cQoCvgyYulwZkevxdLfzR9fj5Y.jiQxG4irSI/DS77el2',
       (SELECT id FROM roles WHERE name='admin'),
       TRUE
ON CONFLICT (username) DO NOTHING;
