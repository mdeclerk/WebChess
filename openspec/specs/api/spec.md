# api Specification

## Purpose
TBD - created by archiving change refactor-win-probability-efficiency. Update Purpose after archive.
## Requirements
### Requirement: Win-Probability Endpoint
The system SHALL expose a `POST /win-probability` endpoint that returns an estimated win probability for each side based on a static board evaluation.

The request payload SHALL include:
- `board`: 8×8 matrix of piece codes or null
- `turn`: side to move ("white" or "black")
- `castling`: castling availability string (default "KQkq")
- `en_passant`: optional en passant target square
- `halfmove`: halfmove clock (default 0)
- `fullmove`: fullmove number (default 1)

The response SHALL include:
- `white`: float in [0.0, 1.0] representing White's win probability
- `black`: float in [0.0, 1.0] representing Black's win probability
- `score`: integer centipawn evaluation from White's perspective

**BREAKING**: The `depth` and `nodes` fields are removed from the response because the endpoint no longer performs a search.

#### Scenario: Instant evaluation without search
- **WHEN** a valid board state is posted to `/win-probability`
- **THEN** the endpoint returns immediately using a static evaluation
- **AND** the response does not include `depth` or `nodes`

#### Scenario: Win probability reflects material balance
- **WHEN** White has significant material advantage
- **THEN** `white` probability is greater than `black`

