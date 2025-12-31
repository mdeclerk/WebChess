# Proposal: add-win-probability-bar

## Why
Players benefit from a fast, glanceable signal of who is currently favored. WebChess already exposes `POST /api/win-probability`, but the UI does not surface it.

## What Changes
- Add a vertical win-probability bar adjacent to the chess board, showing White vs Black winning chances.
- Fetch probability data from `POST /api/win-probability` using the current client-side board state.
- Update the bar on initial load and after position changes (moves, undo, reset).

## User Experience
- The bar is a single vertical track split into a White segment (bottom-up) and a Black segment (top-down).
- The segments always sum to the full track height; White height represents White win probability, and Black is the remainder.
- When probabilities update, the split transitions smoothly to the new value and the segments remain joined without gaps.
- Styling is minimal: only white/black fills with rounded corners matching the board/panel look.
- The bar sits along the left edge of the board area and matches the board’s visible height, with a width of approximately half a square.

## Impact
- Frontend: small additions to DOM, styling, and API integration; no build tooling required.
- Backend: no change (reuses the existing endpoint).
- Performance: one lightweight request per move (plus initial load).

## Out of Scope
- Displaying numeric percentages, tooltips, or engine search depth controls for probability.
- Persisting probability history over time.

## Risks / Mitigations
- **UI alignment across responsive sizes**: compute sizing based on the board canvas’ on-screen bounds and update on resize.
- **Transient API failures**: keep the last known probability (or default to 50/50 before first successful fetch).
