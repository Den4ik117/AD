# Repository Guidelines

## Project Structure & Module Organization
`app/` contains the Litestar API: `controllers` expose endpoints, `services` encode business logic, `repositories` wrap SQLAlchemy queries, and `schemas` define the Pydantic payloads shared across layers. `app/main.py` wires the async engine, dependency providers, and the top-level `Litestar` instance launched through Uvicorn. Database history lives in `migrations/` with generated files under `migrations/versions/`; keep `alembic.ini` in sync whenever DSNs change. Tests mirror the runtime layout (`tests/test_routes`, `test_services`, `test_repositories`, `test_models`), while coverage artifacts are deposited into `htmlcov/`. Top-level helpers include `compose.yaml` for PostgreSQL, `api.http` for sample requests, and `requirements.txt` for the locked toolchain.

## Build, Test, and Development Commands
1. `python -m venv .venv && source .venv/bin/activate` followed by `pip install -r requirements.txt` aligns local deps with CI.
2. `docker compose up -d` spins up the default Postgres container; customize `DATABASE_URL` if pointing to a different host.
3. `alembic upgrade head` applies migrations, and `alembic revision -m "short summary"` creates new schema steps.
4. `python -m app.main` serves the API at `http://127.0.0.1:8000`; run `uvicorn app.main:app --reload` for hot reloads.
5. `pytest`, `pytest -n auto`, or `pytest --cov=app --cov-report=html` execute the suite, parallelize it, and regenerate `htmlcov/` respectively.

## Coding Style & Naming Conventions
Code follows PEP 8 with 4-space blocks, complete type hints, and succinct docstrings (see `app/controllers/user_controller.py`). Use `CamelCase` for models, repositories, and services, but keep modules, functions, and fixtures in `snake_case`. Favor Pydantic validation helpers such as `model_validate`, enforce strict payloads with `ConfigDict(extra="forbid")`, and keep repository functions pure/async for straightforward testing.

## Testing Guidelines
Pytest plus `pytest-asyncio` drive async unit tests, while repository suites reuse fixtures declared in `tests/conftest.py`. Keep file names in the `test_<area>.py` style (`tests/test_routes/test_user_routes.py`) and add regression tests whenever modifying controllers, services, or SQL expressions; maintain ≥80% coverage before opening a PR.

## Commit & Pull Request Guidelines
History shows Conventional Commit prefixes (`feat:`, `fix:`, `docs:`); continue that style, keeping the subject under 72 characters and elaborating in the body when behavior changes. Pull requests should summarize intent, list key changes, link the relevant lab/issue, call out new migrations or configuration steps, and paste the exact test command that was executed locally.

## Security & Configuration Tips
Store credentials in environment variables or an untracked `.env`; the committed DSN in `app/main.py` is only for local Docker use. When sharing traces or screenshots, redact user data, and never commit dumps of the live database or coverage artifacts beyond `htmlcov/`.
