# Flask + Mongo + Celery Project

Flask API project with background jobs (Celery + Redis), job state stored in MongoDB, plus extra modules for RAG and MCP.

## Features

- **API**: Flask + Blueprints, CORS
- **API docs**: Swagger UI (Flasgger) at `GET /api/docs/`
- **Jobs in MongoDB**: statuses/progress/results
- **Background processing**: Celery worker + Celery beat via Redis
- **Image processing**: conversion/processing in a task
- **Page parser**: extracts images from a webpage and stores results
- **Email reports**: send job results via email
- **RAG**: endpoint for RAG pipeline queries
- **MCP**: dedicated service for the MCP server

## Architecture (high level)

- **web**: Flask + Gunicorn (`wsgi.py`)
- **worker**: Celery worker (started via `app/celery_app.py` to guarantee Flask+Celery initialization)
- **beat**: Celery beat (scheduler)
- **redis**: Celery broker/backend
- **mongo**: job document storage
- **mcp**: `python -m app.mcp.server`

## Quick start (Docker Compose)

### Requirements

- Docker Desktop (with `docker compose`)

### Run

```bash
docker compose -f Docker-compose.yml up --build
```

After startup:

- API: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/api/docs/`
- MCP server: `http://localhost:9000/`

### Stop

```bash
docker compose -f Docker-compose.yml down
```

## Local run (without Docker)

### Requirements

- Python 3.11+
- Redis
- MongoDB

### Install dependencies

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file (or export environment variables). Minimal example:

```dotenv
SECRET_KEY=change-me

MONGO_URI=mongodb://localhost:27017/flask_jobs
SQLALCHEMY_DATABASE_URI=sqlite:///users.db

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

FILE_OUTPUT_DIR=./output

# Optional (email)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=you@example.com
MAIL_PASSWORD=app-password
MAIL_DEFAULT_SENDER=you@example.com

# Optional (Celery beat scheduled job)
DAILY_JOB_ID=job_daily
PARSER_URL=https://www.python.org
PARSER_LIMIT=5
DAILY_JOB_USER_EMAIL=you@example.com
```

### Run Flask

```bash
python run.py
```

### Run Celery worker / beat

> Important: use `app/celery_app.py` so Celery starts with Flask app context and configuration.

```bash
celery -A app.celery_app.celery_app worker --loglevel=INFO
celery -A app.celery_app.celery_app beat --loglevel=INFO
```

## API (short)

### Swagger

- `GET /api/docs/` — Swagger UI

### Jobs

- **Parse job**: `POST /api/jobs/parse` (form-data: `url`, `limit`)
- **Image job**: see `image_routes` in `app/routes/`
- **Status**: see `status_routes` in `app/routes/`

### RAG

- `POST /rag` — body: `{ "question": "..." }`

### Agent

- `POST /api/agent` — JSON `{ "query": "..." }` or multipart with a `file`

## Celery tasks

Registered as:

- `tasks.parse_page` (page parsing)
- `tasks.process_image` (image processing)
- `send_job_report` (email report)

The scheduler (beat) is configured via `Settings.CELERY_CONFIG["beat_schedule"]`.

## Security recommendations

- **Do not commit `.env`** and never store secrets in the repository.
- For production, set a strong `SECRET_KEY` and enable secure cookies.

