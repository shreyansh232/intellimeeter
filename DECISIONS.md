# Technical Decisions

## PostgreSQL

### Why
* Reliable relational storage for structured data (Users, Meetings, Action Items).
* Native support for `JSONB`, perfect for storing flexible transcripts and AI analysis results.
* Excellent async support via `asyncpg` and SQLAlchemy 2.0.

### Tradeoffs
* **Pros**: Strong transactional guarantees, production-ready, great query capabilities.
* **Cons**: Requires a running server (unlike SQLite), but managed easily via Docker.

---

## pwdlib & Argon2

### Why
* `passlib` is largely unmaintained. `pwdlib` is a modern, type-safe alternative.
* Used `PasswordHash.recommended()` which defaults to Argon2ID, providing state-of-the-art protection against brute-force and hardware-accelerated attacks.

---

## Pure JSON Authentication

### Why
* Removed OAuth2 form-data requirements to provide a consistent, JSON-first API experience.
* Easier for frontend developers and CLI users to interact with using standard JSON payloads.

---

## OpenAI Structured Output

### Why
* Utilized OpenAI's native `.parse()` functionality with Pydantic models.
* Guarantees that AI responses strictly follow our schema, eliminating the need for complex retry logic or manual JSON parsing.

---

## Service Layer Architecture

### Why
* Separated business logic (`app/services`) from HTTP concerns (`app/api`).
* Ensures that core logic (like analysis or reminders) can be tested and reused independently of the FastAPI framework.

---

## APScheduler

### Why
* Lightweight and built-in task scheduling.
* Perfectly suited for the "overdue reminders" use case without the overhead of Celery or Redis.
