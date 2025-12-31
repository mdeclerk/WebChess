# WebChess MVP

Single-page chess app with a Python backend and a canvas-based UI. The server validates moves, returns notation and FEN, and provides a simple engine for black moves and analysis.

![WebChess screenshot](docs/image.png)

Parts of this project have been co-programmed by AI using [OpenSpec](https://github.com/Fission-AI/OpenSpec).

## Prerequisites

- Docker (Docker Desktop is fine) to run the dev server and tests via `./buildenv.sh`.
- A Unix-like shell to run `./buildenv.sh` (macOS/Linux; on Windows use WSL).
- Port `8000` available on your machine.
- Internet access in your browser (Tailwind CSS is loaded via CDN).

## Quickstart (Docker)

```bash
./buildenv.sh init    # Create docker image 'webchess-dev'
./buildenv.sh start   # Start uvicorn server in container
```

Open: http://127.0.0.1:8000

## Features
- Canvas-rendered board with textured tiles and piece sprites
- Drag-and-drop moves with animated snapping
- Live move validation with legal/illegal feedback
- Rules engine with castling, en passant, and promotion (auto-queen)
- Move list and FEN panel synced after each move
- Automatic black moves via a built-in engine (depth slider 1-4)
- Game-over detection (checkmate / stalemate) surfaced in responses
- Tailwind CSS loaded via CDN (no build step)

## API Endpoints

- `GET /api/health` health check
- `POST /api/fen` return FEN for a given board/state
- `POST /api/validate` validate and apply a move
- `POST /api/move` return an engine move with analysis metadata
- `POST /api/win-probability` return win probabilities from static evaluation

## Build tool `buildenv.sh`

`./buildenv.sh` is a small helper wrapper around Docker so you don’t need a local Python install. It builds a dev image and runs commands with the repo mounted into the container.

```bash
./buildenv.sh init 		# build the `webchess-dev` image
./buildenv.sh bash 		# open an interactive shell in the container
./buildenv.sh test 		# run `pytest` in the container
./buildenv.sh start 	# run the FastAPI app via Uvicorn on port `8000` (with `--reload`)
./buildenv.sh stop 		# stop running containers based on the image
```

Commands are available as VS Code tasks in `.vscode/tasks.json`.

## Project structure
- `app/chess/` rules, notation, and engine
- `app/api/` API routes and schemas
- `app/static/` frontend assets (HTML/CSS/JS + piece SVGs)
- `tests/` pytest test suite
