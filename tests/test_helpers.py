import pytest
from fastapi import HTTPException

from app.api.helpers import build_castle, build_notation, build_validate_response, validate_state_payload
from app.api.schemas import MoveCoord, MovePayload, ValidatePayload
from app.chess.base.move import Move
from conftest import board_from_positions


def _payload(turn: str = "white") -> ValidatePayload:
    return ValidatePayload(
        board=[[None] * 8 for _ in range(8)],
        turn=turn,
        castling="KQkq",
        en_passant=None,
        halfmove=0,
        fullmove=1,
        move=MovePayload(
            from_=MoveCoord(file=4, rank=6),
            to_=MoveCoord(file=4, rank=4),
        ),
    )


def test_build_notation_castle_and_promotion():
    move = Move(4, 7, 6, 7)
    result = {
        "castle": {"rook_from": {"file": 7, "rank": 7}, "rook_to": {"file": 5, "rank": 7}},
        "promotion": None,
    }
    assert build_notation(move, result) == "O-O"

    result["castle"] = {"rook_from": {"file": 0, "rank": 7}, "rook_to": {"file": 3, "rank": 7}}
    assert build_notation(move, result) == "O-O-O"

    result["castle"] = None
    result["promotion"] = "Q"
    assert build_notation(move, result) == "e1g1=Q"


def test_build_castle_returns_move_details():
    result = {
        "castle": {"rook_from": {"file": 7, "rank": 7}, "rook_to": {"file": 5, "rank": 7}},
    }
    castle = build_castle(result)
    assert castle is not None
    assert castle.rook_from == MoveCoord(file=7, rank=7)
    assert castle.rook_to == MoveCoord(file=5, rank=7)

    assert build_castle({"castle": None}) is None


def test_build_validate_response_checkmate():
    board = board_from_positions(
        {(0, 0): "k", (2, 2): "K", (1, 1): "Q"}
    )
    payload = _payload(turn="white")
    result = {
        "board": board,
        "castling": "-",
        "en_passant": None,
        "halfmove": 0,
        "fullmove": 2,
        "capture": None,
        "castle": None,
        "promotion": None,
    }
    response = build_validate_response(Move(4, 6, 4, 4), payload, result)
    assert response.game_over is True
    assert response.outcome == "checkmate"
    assert response.winner == "white"
    assert response.check is True


def test_build_validate_response_stalemate():
    board = board_from_positions(
        {(0, 0): "k", (2, 2): "K", (1, 2): "Q"}
    )
    payload = _payload(turn="white")
    result = {
        "board": board,
        "castling": "-",
        "en_passant": None,
        "halfmove": 0,
        "fullmove": 2,
        "capture": None,
        "castle": None,
        "promotion": None,
    }
    response = build_validate_response(Move(4, 6, 4, 4), payload, result)
    assert response.game_over is True
    assert response.outcome == "stalemate"
    assert response.winner is None
    assert response.check is False


def test_validate_state_payload_errors():
    with pytest.raises(HTTPException) as exc:
        validate_state_payload("green", [[None] * 8 for _ in range(8)])
    assert exc.value.status_code == 400
    assert exc.value.detail == "invalid_turn"

    with pytest.raises(HTTPException) as exc:
        validate_state_payload("white", [[None] * 7 for _ in range(8)])
    assert exc.value.status_code == 400
    assert exc.value.detail == "invalid_board"
