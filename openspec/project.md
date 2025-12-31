# Project Context

## Purpose
WebChess is a single-page chess app (MVP) with a Python backend and a canvas-based UI.

Goals:
- Provide a clean in-browser playing experience with drag-and-drop moves.
- Keep the server as the source of truth for move legality and game state updates.
- Offer lightweight “engine” features (computer plays Black, basic analysis metadata).

## Tech Stack
- Backend: Python + FastAPI, served via Uvicorn.
- API schema/validation: Pydantic models (v2-style `ConfigDict` usage in `app/api/routes.py`).
- Frontend: static HTML/CSS/JS served by FastAPI `StaticFiles`; vanilla JS ES modules + `<canvas>`.
- Styling: Tailwind CSS via CDN (no build step).
- Testing: `pytest` (+ FastAPI `TestClient`), `pytest-cov`, `httpx`.
- Dev environment: Docker (`Dockerfile`) + helper script `./buildenv.sh`; VS Code tasks in `.vscode/tasks.json`.

## Project Conventions

### Code Style
- Python: type hints where helpful, 4-space indentation, docstrings for non-trivial functions, `snake_case` names, `PascalCase` classes, `UPPER_SNAKE_CASE` constants.
- JS: ES module files under `app/static/js/`, `camelCase` identifiers, prefer small focused modules (state/render/api/interaction separation).
- Avoid adding heavy tooling unless needed: there is no configured formatter/linter (no `ruff`/`black`/`isort` config in repo).
- API error/validation conventions:
  - Shape/field validation errors are FastAPI/Pydantic defaults (`422`).
  - Engine endpoints (`/api/move`, `/api/win-probability`) return `400` with `{"detail": "<reason>"}` for basic request validation (`invalid_turn`, `invalid_board`, `invalid_depth`).
  - Move validation (`/api/validate`) returns `200` and encodes illegality as `{"legal": false, "reason": "<code>"}` (e.g. `no_piece`, `wrong_color`, `occupied_by_ally`, `king_in_check`, `castle_blocked`, ...).

### Architecture Patterns
- `app/main.py` composes the service:
  - mounts the API router under `/api`
  - serves the static frontend at `/` via `StaticFiles(directory="app/static", html=True)`
- `app/api/routes.py` holds the HTTP contract (Pydantic payload/response models) and delegates to domain logic in `app/chess/`.
- Domain code organization:
  - `app/chess/base/`: board/move primitives + notation helpers (FEN, LAN/UCI)
  - `app/chess/rules/`: legality + move application, check/checkmate/stalemate detection
  - `app/chess/engine/`: move generation + evaluation + alpha-beta search
- API is stateless: clients post the full game state in each request; server returns derived state (FEN, updated clocks, etc.).

### Testing Strategy
- Primary runner: `./buildenv.sh test` (executes `pytest` in Docker).
- Prefer unit tests for rules/notation/engine; keep API tests focused on request/response contract.
- Determinism: tests seed randomness via `PYTEST_DETERMINISTIC_SEED` (default `0`) in `tests/conftest.py`.
- Pytest markers used: `slow`, `api` (declared in `pytest.ini` and `tests/conftest.py`).

### Git Workflow
Not formalized in this repo.

Suggested default:
- Use feature branches off `main` and open PRs.
- Keep commits small and descriptive; prefer “why” in PR description, “what” in commit message.
- Avoid mixing refactors with behavior changes unless necessary.

## Domain Context
Chess/state conventions (also summarized in `README.md`):
- Coordinates:
  - `file`: `0..7` corresponds to `a..h`
  - `rank`: `0..7` corresponds to `8..1` (rank 0 is the top of the board)
  - `board` is an 8x8 matrix indexed as `board[rank][file]`
- Piece codes: single-letter strings; uppercase = white (e.g. `"P"`), lowercase = black (e.g. `"p"`).
- Turn values: `"white"` or `"black"` (backend); UI uses `"White"`/`"Black"` in some places.
- Castling rights: a string like `"KQkq"` (or `"-"`).
- En passant: optional `{file, rank}` coordinate in API payloads; domain helpers often normalize to `(file, rank)` tuples.
- Notation:
  - Validation response returns LAN like `e2e4`; promotions append `=Q` (auto-queen).
  - Castling notation is `O-O` / `O-O-O`.
- Engine:
  - Depth is limited to `1..4` (plies) for UI responsiveness.
  - Evaluation score is from White’s perspective (positive favors White, negative favors Black).

## Important Constraints
- No frontend build pipeline/bundler; keep browser code compatible with static serving from `app/static/`.
- Tailwind is loaded via CDN; UI styling depends on external network access in the browser.
- Backend execution is Docker-first (`./buildenv.sh init|start|test`); developers may not have `python` installed locally.
- Keep server-side computation bounded (especially engine search); avoid introducing slow endpoints without a proposal.

## External Dependencies
- Tailwind CDN: `https://cdn.tailwindcss.com`
- Python dependencies (see `requirements.txt`): `fastapi`, `uvicorn[standard]`, `pydantic`, `pytest`, `pytest-cov`, `httpx`
- Docker is required for the documented dev/test workflow; service listens on port `8000` by default.
