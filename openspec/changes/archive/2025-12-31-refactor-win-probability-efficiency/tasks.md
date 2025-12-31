## 1. Implementation
- [x] 1.1 Update `WinProbabilityResponse` model (remove `depth`, `nodes`; keep `white`, `black`, `score`)
- [x] 1.2 Replace `search_best_move` with `evaluate_board` in `win_probability` endpoint
- [x] 1.3 Remove unused depth validation logic from endpoint

## 2. Tests
- [x] 2.1 Update existing `win_probability` tests to match new response schema
- [x] 2.2 Add test verifying instant response (no search overhead)
- [x] 2.3 Add test for material-advantage probability ordering
- [x] 2.4 Add test verifying `white + black == 1.0`
- [x] 2.5 Add test for starting position returning ~0.5 probabilities
- [x] 2.6 Add test for invalid board validation error

## 3. Documentation
- [x] 3.1 Update API spec in `openspec/specs/api/spec.md`
- [x] 3.2 Update README if endpoint usage is documented there
