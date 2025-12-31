# ui Specification

## Purpose
Provide lightweight, glanceable UI signals adjacent to the chess board that help players understand the current position.

## ADDED Requirements
### Requirement: Win-Probability Bar
The UI SHALL display a vertical win-probability bar adjacent to the chess board using data from `POST /api/win-probability`.

The bar SHALL:
- be positioned outside the board on the left, separated by the same horizontal gap used between the board and the right-side panel
- match the full board frame height (including the brown frame around the squares)
- have a width approximately half of a chess square
- be visually simple, using only white and black fills for its two segments
- use rounded corners consistent with the board/panel styling

The bar SHALL consist of exactly two stacked segments:
- a White segment anchored from bottom to top whose height represents White win probability
- a Black segment anchored from top to bottom whose height represents Black win probability

The White and Black segment heights SHALL always sum to the full bar height.

#### Scenario: Rendered bar on initial load
- **WHEN** the UI loads with an initial position
- **THEN** the win-probability bar is visible adjacent to the board
- **AND** the bar represents a valid probability split that sums to the full height

#### Scenario: Probability updates after a move
- **WHEN** a legal move is applied to the position
- **THEN** the UI requests updated win probabilities from `POST /api/win-probability`
- **AND** the displayed bar updates to reflect the returned probabilities

#### Scenario: Probability updates after undo
- **WHEN** the user undoes a move and the position changes
- **THEN** the UI requests updated win probabilities from `POST /api/win-probability`
- **AND** the displayed bar updates to reflect the returned probabilities

#### Scenario: Robustness to API failure
- **WHEN** `POST /api/win-probability` fails or returns invalid values
- **THEN** the UI continues to render without errors
- **AND** the bar remains at the last known valid probability (or defaults to 50/50 if none yet)

### Requirement: Win-Probability Bar Animation
When new win-probability data arrives, the UI SHALL animate the probability bar smoothly from the current displayed values to the new values.

The animation SHALL complete in approximately 1 second.

During animation, the White and Black segments SHALL:
- remain adjacent (no gap or overlap)
- animate in lockstep so the meeting boundary moves smoothly to its new position
- always sum to the full bar height throughout the animation

#### Scenario: Smooth transition to updated value
- **WHEN** the UI receives updated probabilities from `POST /api/win-probability`
- **THEN** the bar transitions smoothly to the new split
- **AND** the White/Black boundary moves without jumps
