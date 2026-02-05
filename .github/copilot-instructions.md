# AI Coding Assistant Instructions

## Architecture Overview
This is a Flask application with Celery for background task processing, using SQLAlchemy for relational data (users/jobs) and Redis as Celery broker. Includes AI components: RAG (Retrieval-Augmented Generation) with FAISS vector store and MCP (Model Context Protocol) agent with LangChain tools.

- **Web Service**: Flask app with factory pattern (`app/factory.py`), blueprints in `app/routes/`
- **Background Tasks**: Celery worker/beat via `app/celery_app.py`, tasks in `app/tasks/`
- **Data**: SQLAlchemy models in `app/models.py`, repositories in `app/repositories/`
- **AI Features**: RAG pipeline (`app/rag/`), MCP agent (`app/mcp/`) with tools for image processing/page parsing
- **Deployment**: Docker Compose with services for web, worker, beat, MCP server, Redis, MongoDB

## Key Patterns & Conventions
- **App Factory**: Use `create_app()` from `app.factory` for Flask initialization
- **Blueprints**: Register API routes under `/api` prefix, auth under `/auth`
- **Job Management**: Jobs stored in SQLAlchemy, updated via `app.repositories.job_repository`
- **Celery Tasks**: Define in `app/tasks/`, import from `app.celery_app.celery_app`
- **Configuration**: Environment variables loaded via `python-dotenv`, settings in `app.settings.Settings`
- **Logging**: Rotating file handler configured in `Settings.setup_logging()`
- **AI Integration**: LangChain for LLM/agents, FAISS for in-memory vector storage

## Development Workflow
- **Local Setup**: `pip install -r requirements.txt`, set `.env` with DB URIs, run `python run.py` for Flask + `celery -A app.celery_app.celery_app worker --loglevel=INFO` for tasks
- **Docker**: `docker compose -f Docker-compose.yml up --build` starts all services
- **Testing**: Use `pytest` with coverage, mypy for type checking, black/flake8 for formatting
- **Migrations**: `flask db upgrade` for SQLAlchemy schema changes
- **API Docs**: Swagger UI at `/api/docs/` via Flasgger

## Common Tasks
- **Add Route**: Create blueprint in `app/routes/`, register in `app/routes/__init__.py` and `factory.py`
- **Add Task**: Define function in `app/tasks/`, ensure imported in `celery_app.py`
- **Add Model**: Create SQLAlchemy model in `app/models.py`, add to admin if needed
- **AI Tool**: Add LangChain Tool in `app/mcp/tools.py`, register in `app/mcp/agent.py`
- **RAG Data**: Use `app.rag.vector_store.add_metadata()` to add documents to FAISS store

## File Structure Reference
- `app/__init__.py`: App instance creation
- `app/factory.py`: Flask app factory with extensions/blueprints
- `app/settings.py`: Configuration class with Celery beat schedules
- `app/models.py`: SQLAlchemy models (Job, User)
- `app/routes/`: Blueprints for API endpoints
- `app/tasks/`: Celery task definitions
- `app/rag/`: RAG pipeline with embeddings/vector store
- `app/mcp/`: MCP agent with tools and server
- `run.py`: Development server entry point
- `wsgi.py`: Production Gunicorn entry point</content>
<parameter name="filePath">c:\Users\Admin\PycharmProjects\flask_mongo_celery_project\.github\copilot-instructions.md