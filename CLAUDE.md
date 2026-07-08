# To-Do PWA — Backend (FastAPI)

Python 3.12+ and FastAPI. This is the API for my to-do PWA; the React frontend is a separate repo.

## Conventions
- Modern, idiomatic Python: type hints everywhere, `async def` for routes/IO, Pydantic v2 schemas.
- Layout: `app/` with `main.py`, `routers/`, `models/`, `schemas/`, `services/`, dependencies for DI.
- Use standard FastAPI patterns (APIRouter, dependency injection) — don't reach for Rails-style conventions.

## Commands
- Run: `uvicorn app.main:app --reload`
- Tests (once set up): `pytest`

## Notes
- Contrast new patterns with the Rails equivalent so they click.
- Flag Python footguns: mutable default args, blocking calls inside async, etc.
- Do not edit files! Your role is to help me learn Python. 
