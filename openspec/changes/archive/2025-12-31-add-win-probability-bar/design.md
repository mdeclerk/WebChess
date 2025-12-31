## UI Placement
- Implement as DOM elements (not canvas) so it can be positioned and resized independently of the render loop.
- Place the bar inside the board card container and offset it to the left so it sits outside the board frame with the same gap as the board-to-panel spacing.

## Visual Style
- Use only two colors: pure/near-white for White and pure/near-black for Black (no gradients).
- Apply rounded corners on the outer track to match the board/panel radius; keep the interior join straight so segments meet cleanly.

## Sizing Strategy
- Read the on-screen bounds of the board canvas via `getBoundingClientRect()`.
- Set the bar’s height to the full board frame height (brown frame included) and its width to ~`squareSize / 2` (based on on-screen square size).
- Update sizing on initial load and on `resize` events.

## Animation Strategy
- Animate updates via a single CSS transition on the White segment height (e.g., `transition: height 250ms ease-out`).
- Derive the Black segment height as `calc(100% - var(--white-pct))` (or equivalent), ensuring both segments change in lockstep and always sum to the full height.
- Use a fast-but-not-jarring duration of ~1s (e.g., `1000ms`) with an ease-out style curve.

## Update Strategy
- Add a `requestWinProbability()` API helper mirroring `requestFen()` (uses `boardMatrixFromPieces()` + current `gameState` and `state.turn`).
- Refresh the bar:
  - After initial FEN load (or immediately after init once pieces exist)
  - After every `chess:move-applied` event
  - After undo actions (when the position is reverted)
- On API error: keep the last displayed probabilities (or default 0.5/0.5 before first success).
