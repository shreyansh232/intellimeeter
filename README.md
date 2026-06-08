# IntelliMeeter

AI-powered meeting management platform that extracts summaries, decisions, action items, follow-ups, and citations from meeting transcripts.

## Features

* **Secure Authentication**: Pure JSON-based JWT authentication using `pwdlib` (Argon2/Bcrypt).
* **Meeting Management**: Create, list, and retrieve meetings with full ownership validation.
* **AI Meeting Analysis**: Automated extraction of summaries, decisions, and follow-ups.
* **Transcript Citation Grounding**: Every AI-generated insight is backed by a timestamped citation from the transcript.
* **Action Item Management**: Automated extraction and status tracking for tasks.
* **Overdue Detection**: Proactive identification of tasks past their due date.
* **Discord Notifications**: Automated reminders for overdue action items via Discord webhooks.
* **Request Trace IDs**: Every request is assigned a unique UUID for easy debugging and log correlation.
* **Unified API Responses**: Standardized success and error wrappers across all endpoints.

## Tech Stack

* **Language**: Python 3.12
* **Framework**: FastAPI
* **Database**: PostgreSQL with SQLAlchemy (Async)
* **Migrations**: Alembic
* **AI**: OpenAI (GPT-4o-mini with Structured Outputs)
* **Task Scheduling**: APScheduler
* **Package Manager**: [uv](https://github.com/astral-sh/uv)
* **Testing**: Pytest & Pytest-asyncio

## Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
SECRET_KEY=your-super-secret-key
OPENAI_API_KEY=sk-your-openai-key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

## Local Setup

### 1. Install uv
If you don't have `uv` installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Run Migrations
```bash
uv run alembic upgrade head
```

### 4. Start Application
```bash
uv run uvicorn app.main:app --reload
```

* **API**: [http://localhost:8000](http://localhost:8000)
* **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Makefile Commands

A `Makefile` is provided for common development tasks:

* `make tests`: Run all unit and integration tests.
* `make lint`: Run ruff linting checks.
* `make run`: Run the development server.
* `make clean`: Clean up cache files.

## Docker

```bash
docker compose up --build
```

## API Examples

### Register
```bash
curl -X POST http://localhost:8000/api/auth/register \
-H "Content-Type: application/json" \
-d '{"email":"test@example.com", "password":"password123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
-H "Content-Type: application/json" \
-d '{"email":"test@example.com", "password":"password123"}'
```

### Create Meeting
```bash
curl -X POST http://localhost:8000/api/meetings \
-H "Authorization: Bearer <token>" \
-H "Content-Type: application/json" \
-d '{
  "title": "Strategy Session",
  "meeting_date": "2026-06-10T10:00:00Z",
  "participants": ["test@example.com"],
  "transcript": [{"timestamp": "00:01", "speaker": "User", "text": "We must launch by Friday."}]
}'
```

### Analyze Meeting
```bash
curl -X POST http://localhost:8000/api/meetings/{meeting_id}/analyze \
-H "Authorization: Bearer <token>"
```

## Architecture

1. **Middleware**: Trace ID generation and logging.
2. **Auth Service**: JWT handling with `pwdlib`.
3. **Meetings Service**: CRUD operations and ownership checks.
4. **Analysis Service**: OpenAI integration with structured output validation.
5. **Reminder Service**: APScheduler polling for overdue items and Discord delivery.
