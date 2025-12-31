# Change: Refactor win-probability endpoint for efficiency

## Why
The current `/win-probability` endpoint calls `search_best_move`, which performs a full depth-limited minimax search (up to depth 4). For a simple "probability bar" that only needs a quick strength signal, this is expensive and slow. Using a static `evaluate_board` call instead provides an instant answer without exploring the game tree.

## What Changes
- **BREAKING**: `depth` and `nodes` fields are removed from the response (no search is performed).
- Replace `search_best_move` call with `evaluate_board` for instant static evaluation.
- Simplify the response model to only include `white`, `black`, and `score`.

## Impact
- Affected specs: `api`
- Affected code: `app/api/routes.py` (endpoint implementation and response model)
