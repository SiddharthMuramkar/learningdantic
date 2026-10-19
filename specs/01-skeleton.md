# 01 skeleton
Status: done

## What and why
The base every other spec builds on, alone in wave 1. Everything in specs/contract.md marked "real" works;
everything marked "stub" exists with its exact signature. Teaches episode 01 (Postgres) and 02 (Alembic).
Dependencies, all at once, in a new `app` dependency group (not default): fastapi[standard], sqlalchemy,
psycopg[binary], alembic, "logfire[fastapi,sqlalchemy]>=5.2,<6", pytest-playwright. Then `uv lock`.
compose.yaml: `name: acme-desk`, service `db`, image `postgres:18`, user/password/db `acme`,
port `127.0.0.1:5432:5432`, volume `pgdata:/var/lib/postgresql`, a pg_isready healthcheck.
Alembic lives in `migrations/` (not `alembic/`), one initial migration with the whole schema, ruff post-write hooks.
CI: a new `fullstack` job (postgres:18 service with the acme user, `MODEL=test`, `uv sync --locked --group app`,
`uv run pytest app/tests --ignore=app/tests/e2e`). The existing `ci` job is unchanged.
AGENTS.md: the header says the current rules apply to notebooks/ and solutions/; add the "full-stack track"
section from the approved plan (app/__init__.py is where setup() runs). README.md: one short section linking track/.
Your piece: ep01 = `seed()` in app/seed.py; ep02 = `upgrade()` in the initial migration.

## Done when
- [x] The Check passes with Postgres up; `docker compose up -d --wait` works on a fresh volume
- [x] `uv run --group app uvicorn app.main:app` starts; `/health` answers; stub routes answer 501
- [x] app/tests/test_ep01_postgres.py and test_ep02_alembic.py pass (02: upgrade, downgrade base, upgrade head on a scratch DB)
- [x] Blanking `seed()` turns test_ep01 red, blanking `upgrade()` turns test_ep02 red (checked, then restored)
- [x] track/01-postgres/EPISODE.md (docker compose, `docker compose exec db psql -U acme acme`, `\dt`, `;`, `\q`, down vs down -v)
- [x] track/02-alembic/EPISODE.md (read the migration, upgrade/downgrade/history/current, autogenerate a change and discard it)
- [x] The existing keyless notebook list still passes after `uv lock` (starlette may move)

## Touches
Everything in contract.md marked 01, plus AGENTS.md, README.md, SPEC.md, specs/, the guard hook (already changed on this branch).

## Out of scope
Any real behaviour in the stub files. Async SQLAlchemy. testcontainers. An .env.example change (the URL default lives in app/db.py).
