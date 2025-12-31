## 1. Implementation
- [x] 1.1 Add probability-bar DOM next to the board container (vertical track + 2 segments).
- [x] 1.2 Add styling so the bar matches board height and is ~half a square wide; White anchors bottom-up, Black top-down; rounded corners and only black/white fills.
- [x] 1.3 Add `requestWinProbability()` to `app/static/js/api.js` calling `POST /api/win-probability`.
- [x] 1.4 Add state storage for the current win probability (default 0.5/0.5) and a safe update helper (clamp/sum-to-1).
- [x] 1.5 Update `app/static/js/app.js` to fetch probability on init and after both move-apply and undo actions.
- [x] 1.6 Animate probability updates so the White/Black boundary moves smoothly and both segments resize in lockstep.
- [x] 1.7 Handle failures by keeping the last successful value (or 0.5/0.5 if none yet).

## 2. Verification
- [x] 2.1 Load the app: bar renders and shows a balanced value after first fetch.
- [x] 2.2 Make a move: bar updates shortly after the move is applied.
- [x] 2.3 Undo / restart / new game: bar updates to reflect the current board state.
- [x] 2.4 Probability updates animate smoothly without gaps/overlap between segments.
- [x] 2.5 Resize viewport: bar remains aligned with the board height.
