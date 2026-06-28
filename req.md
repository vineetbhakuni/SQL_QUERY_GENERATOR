# Build Prompt — AI SQL Query Generator (with Access Control)

> Copy everything below the line into your AI coding assistant (Claude, Cursor, etc.).
> Fill in the bracketed `[...]` choices first, or leave them and let the assistant pick sensible defaults.

---

## Role

You are a senior full-stack engineer. Build a working, well-documented **AI-powered SQL Query Generator** with a secure access-control layer. Produce runnable code, not just descriptions. Explain key decisions briefly as you go and ask before making irreversible choices.

## Goal

Build an assistant that lets a non-technical user describe what they want in plain English and get back safe, correct, explained SQL — **but only for the data and operations they are authorized to touch.**

The flow:

1. User types a request in natural language.
2. System reads the live database schema.
3. System generates one or more candidate SQL queries.
4. Each candidate is explained in plain language, shows the tables/columns involved, and estimates its impact (rows returned or modified).
5. **An authorization layer checks every candidate against the user's role and blocks anything they're not permitted to run.**
6. The user picks an allowed query and executes it; results and history are saved.

## Tech Stack

- **Backend:** [Python — FastAPI] (preferred) or Flask
- **Database:** [PostgreSQL] or MySQL — connect to a real DB, don't fake it
- **LLM:** [Anthropic Claude API] or OpenAI — used for generation + explanation
- **Frontend:** [React] or simple HTML/JS — a page to type requests, view candidates, see explanations/impact, and run the chosen query
- **Auth:** JWT-based login with roles stored in the DB

If a choice isn't specified, pick the default in brackets and tell me why.

## Modules

**1. User Prompt Processing** — accept natural-language input, clean it, detect intent (read vs. write vs. ambiguous).

**2. Schema Understanding** — introspect the connected database. Extract tables, columns, types, and foreign-key relationships. Feed this schema to the LLM so it never guesses or hallucinates column names.

**3. Query Generation** — use the LLM + schema to produce valid SQL. Support SELECT, INSERT, UPDATE, DELETE. When the request is ambiguous, return **multiple labeled candidates** instead of one.

**4. Explanation Engine** — for each query, explain it in simple language: what it returns/changes, which tables and columns it uses, and what joins/filters/aggregations are applied.

**5. Impact Analyzer** — before running anything, estimate the blast radius. For reads, estimate rows returned. For writes/deletes, run a matching `SELECT COUNT(*)` with the same `WHERE` clause to report how many rows *would* change, and clearly flag risky operations (DELETE/UPDATE without WHERE, etc.).

**6. Validation & Optimization** — validate SQL syntax, reject malformed queries, and suggest a more efficient alternative where one exists.

**7. Selection & Execution** — show the user the allowed candidates, let them choose one, execute it, and return results. Persist a query history per user.

**8. Access Control & Authorization (security layer — required)** — see below.

## Security & Access Control (key requirement)

The system must **prevent users from running queries against data or operations they are not authorized for.** Implement:

- **Authentication:** users log in; identity is verified (hashed passwords, JWT sessions).
- **Role-Based Access Control (RBAC):** each user has a role (e.g. `viewer`, `analyst`, `admin`). Roles map to permissions:
  - which **tables/columns** they may read,
  - which **operations** they may perform (e.g. `viewer` = SELECT only; `analyst` = SELECT/UPDATE on assigned tables; `admin` = all).
- **Pre-execution authorization check:** after a query is generated, parse it to find every table, column, and operation it touches, then check each against the user's permissions. If any part is disallowed, **block the query and show a clear "not authorized" message** — never silently run a partially-allowed query.
- **Row/column-level filtering (optional but recommended):** restrict results to rows/columns the user is allowed to see (e.g. a manager sees only their department).
- **SQL-injection and prompt-injection defense:** use parameterized/validated queries, never trust raw LLM output blindly, and confirm before any destructive write.
- **Audit log:** record who ran what query, when, and whether it was allowed or blocked.

Make the permission rules **data-driven** (stored in DB tables like `roles`, `permissions`, `user_roles`) so they can be changed without editing code.

## Functional Requirements (acceptance criteria)

The finished system should:

- accept natural-language prompts and generate valid SQL,
- generate multiple alternatives when the request is ambiguous,
- explain each query and list the tables/columns involved,
- estimate rows affected before execution,
- validate query correctness,
- **enforce role-based authorization on every query and block unauthorized ones,**
- work against MySQL or PostgreSQL,
- maintain per-user query history and an audit log,
- return execution results.

## Sample Behavior

**Input:** "Show all employees whose salary is greater than ₹50,000."
**Generated:** `SELECT * FROM Employee WHERE Salary > 50000;`
**Explanation:** Returns employee records with salary above ₹50,000.
**Impact:** ~25 rows returned.
**Auth check:** allowed for `viewer` and above.

**Input:** "Increase salary of all employees in IT by 10%."
**Generated:** `UPDATE Employee SET Salary = Salary * 1.10 WHERE Department = 'IT';`
**Explanation:** Raises IT-department salaries by 10%.
**Impact:** ~42 rows would be modified (flagged as a write).
**Auth check:** blocked for `viewer`/`analyst`, allowed only for `admin`.

## Deliverables

1. Project structure and a short README with run instructions.
2. A SQL seed script that creates a sample schema (e.g. Employee, Students, Department) **plus** the `roles`, `permissions`, and `user_roles` tables, with a few demo users of different roles.
3. Backend implementing all 8 modules.
4. A minimal frontend that exercises the full flow including login.
5. Notes on the security model and how to extend permissions.

## How to proceed

Start by proposing the project structure and the permission/role data model, wait for my confirmation, then build module by module — schema understanding and the authorization layer first, since everything else depends on them.