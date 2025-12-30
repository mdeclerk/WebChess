from fastapi.testclient import TestClient

from app.main import app
client = TestClient(app)


def initial_board_matrix():
    return [
        list("rnbqkbnr"),
        list("pppppppp"),
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        list("PPPPPPPP"),
        list("RNBQKBNR"),
    ]


def test_illegal_move_no_piece():
    payload = {
        "board": [[None] * 8 for _ in range(8)],
        "turn": "white",
        "move": {"from": {"file": 0, "rank": 0}, "to": {"file": 0, "rank": 1}},
    }
    r = client.post("/api/validate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["legal"] is False and data["reason"] == "no_piece"


def test_health_endpoint():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_game_fen_endpoint_returns_fen():
    payload = {
        "board": initial_board_matrix(),
        "turn": "white",
        "castling": "KQkq",
        "en_passant": None,
        "halfmove": 0,
        "fullmove": 1,
    }
    r = client.post("/api/fen", json=payload)
    assert r.status_code == 200
    assert r.json() == {"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}


def test_engine_move_endpoint_returns_move():
    payload = {
        "board": initial_board_matrix(),
        "turn": "white",
        "castling": "KQkq",
        "en_passant": None,
        "halfmove": 0,
        "fullmove": 1,
        "depth": 1,
    }
    r = client.post("/api/move", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["move"] is not None
    assert data["from"] is not None
    assert data["to"] is not None
    assert isinstance(data["depth"], int)
    assert isinstance(data["nodes"], int)
    assert isinstance(data["score"], int)


def test_win_probability_endpoint_is_deterministic_and_normalized():
    payload = {
        "board": initial_board_matrix(),
        "turn": "white",
        "castling": "KQkq",
        "en_passant": None,
        "halfmove": 0,
        "fullmove": 1,
        "depth": 1,
    }
    r1 = client.post("/api/win-probability", json=payload)
    r2 = client.post("/api/win-probability", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    data1 = r1.json()
    data2 = r2.json()
    assert data1 == data2
    total = data1["white"] + data1["black"]
    assert abs(total - 1.0) < 1e-6


def test_legal_pawn_double_step_returns_en_passant_and_fen_and_notation():
    board = initial_board_matrix()
    payload = {
        "board": board,
        "turn": "white",
        "castling": "KQkq",
        "en_passant": None,
        "halfmove": 0,
        "fullmove": 1,
        "move": {"from": {"file": 4, "rank": 6}, "to": {"file": 4, "rank": 4}},
    }
    r = client.post("/api/validate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["legal"] is True
    assert data["notation"] == "e2e4"
    assert data["en_passant"] == {"file": 4, "rank": 5}
    assert data["castling"] == "KQkq"
    assert data["halfmove"] == 0
    assert data["fullmove"] == 1


def test_checkmate_fools_mate_black_delivers_checkmate():
    # Position after 1. f3 e5 2. g4  (white pawns moved f3 and g4, black pawn e5)
    board = [
        list("rnbqkbnr"),
        list("pppppppp"),
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        list("PPPPPPPP"),
        list("RNBQKBNR"),
    ]
    # apply white moves on the matrix
    # f2 -> f3
    board[6][5] = None
    board[5][5] = "P"
    # g2 -> g4
    board[6][6] = None
    board[4][6] = "P"
    # e7 -> e5
    board[1][4] = None
    board[3][4] = "p"

    payload = {
        "board": board,
        "turn": "black",
        "castling": "KQkq",
        "en_passant": None,
        "halfmove": 0,
        "fullmove": 1,
        "move": {"from": {"file": 3, "rank": 0}, "to": {"file": 7, "rank": 4}},
    }
    r = client.post("/api/validate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["legal"] is True
    assert data["game_over"] is True
    assert data["outcome"] == "checkmate"
    assert data["winner"] == "black"


def test_engine_move_invalid_turn():
    payload = {
        "board": initial_board_matrix(),
        "turn": "green",
        "castling": "KQkq",
        "en_passant": None,
        "halfmove": 0,
        "fullmove": 1,
        "depth": 1,
    }
    r = client.post("/api/move", json=payload)
    assert r.status_code == 400
    assert r.json()["detail"] == "invalid_turn"


def test_engine_move_invalid_board_shape():
    payload = {
        "board": [[None] * 7 for _ in range(8)],
        "turn": "white",
        "castling": "KQkq",
        "en_passant": None,
        "halfmove": 0,
        "fullmove": 1,
        "depth": 1,
    }
    r = client.post("/api/move", json=payload)
    assert r.status_code == 400
    assert r.json()["detail"] == "invalid_board"


def test_engine_move_invalid_depth():
    payload = {
        "board": initial_board_matrix(),
        "turn": "white",
        "castling": "KQkq",
        "en_passant": None,
        "halfmove": 0,
        "fullmove": 1,
        "depth": 5,
    }
    r = client.post("/api/move", json=payload)
    assert r.status_code == 400
    assert r.json()["detail"] == "invalid_depth"


def test_validate_move_invalid_coordinates():
    payload = {
        "board": initial_board_matrix(),
        "turn": "white",
        "move": {"from": {"file": 9, "rank": 0}, "to": {"file": 0, "rank": 1}},
    }
    r = client.post("/api/validate", json=payload)
    assert r.status_code == 422


def test_validate_move_missing_payload_fields():
    payload = {
        "board": initial_board_matrix(),
        "turn": "white",
    }
    r = client.post("/api/validate", json=payload)
    assert r.status_code == 422


def test_win_probability_invalid_turn():
    payload = {
        "board": initial_board_matrix(),
        "turn": "green",
        "castling": "KQkq",
        "en_passant": None,
        "halfmove": 0,
        "fullmove": 1,
        "depth": 1,
    }
    r = client.post("/api/win-probability", json=payload)
    assert r.status_code == 400
    assert r.json()["detail"] == "invalid_turn"


def test_win_probability_invalid_board_shape():
    payload = {
        "board": [[None] * 7 for _ in range(8)],
        "turn": "white",
        "castling": "KQkq",
        "en_passant": None,
        "halfmove": 0,
        "fullmove": 1,
        "depth": 1,
    }
    r = client.post("/api/win-probability", json=payload)
    assert r.status_code == 400
    assert r.json()["detail"] == "invalid_board"
