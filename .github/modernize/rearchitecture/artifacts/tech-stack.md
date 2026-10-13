# Technology Stack

## Languages and runtimes

- Python backend; `backend/requirements.txt` uses open-ended minimum versions and the blueprint states Python 3.11+.
- TypeScript/React frontend; Next.js `^14.2.15`, React `^18.3.1`, TypeScript `^5.6.3`.
- Java demo target; Maven, Java 17, Spring Boot `2.7.18`.
- YAML, JSON, SQL, Mermaid/C4 text, and Docker Compose configuration.

## Backend dependencies

FastAPI, Uvicorn, Pydantic v2, pydantic-settings, python-multipart, websockets, SQLAlchemy 2, Alembic, passlib/bcrypt, python-jose, httpx, NetworkX, NumPy, SciPy, scikit-learn, sqlglot, OR-Tools, Jinja2, ReportLab, pytest, pytest-asyncio, pytest-cov, Hypothesis, and Ruff.

The configured runtime can optionally use Neo4j, PostgreSQL/pgvector, Redis/Celery, MinIO/S3, Ollama, Gemini, and Anthropic-compatible LLM settings. The checked-in requirements do not include all optional provider clients; local fallback modes are present in configuration.

## Frontend dependencies

Next.js App Router, React, Axios, Tailwind CSS, PostCSS, Autoprefixer, Lucide React, clsx, tailwind-merge, ESLint, and Next ESLint configuration.

## Demo target dependencies

Spring Boot Web, Spring Data JPA, Spring Security, H2 runtime, Spring Boot Test, and the Spring Boot Maven plugin. The application properties configure in-memory H2, GxP flags, hard-coded demo admin settings, and Windows instrument directories.

## Runtime/configuration constraints

- Backend defaults to SQLite, in-memory/local graph behavior, local background execution, and local storage; Docker Compose enables PostgreSQL, Neo4j, Redis/Celery, and MinIO.
- `backend/app/config.py` externalizes database, graph, queue, object storage, JWT, LLM, algorithm, and CORS settings.
- `frontend/lib/api.ts` defaults API calls to `http://localhost:8000` and reads the browser token from local storage.
- `demo-lims/src/main/resources/application.properties` fixes the Java service port at 8080 and uses a shared in-memory H2 schema.

