from typing import Optional

from fastapi import HTTPException

from app.api.schemas import CastleMove, EngineMovePayload, MoveCoord, ValidatePayload, ValidateResponse
from app.chess.base.board import Board
from app.chess.base.move import Move
from app.chess.base.notation import fen_from, move_to_lan
from app.chess.rules import has_any_legal_move, is_in_check

ENGINE_MIN_DEPTH = 1
ENGINE_MAX_DEPTH = 4
ENGINE_DEFAULT_DEPTH = 2


def en_passant_tuple(en_passant: Optional[MoveCoord]):
    """Converts an optional MoveCoord into a tuple for rule helpers."""
    return (en_passant.file, en_passant.rank) if en_passant else None


def validate_engine_payload(payload: EngineMovePayload) -> int:
    """Validates engine payload basics and resolves search depth."""
    validate_state_payload(payload.turn, payload.board)
    depth = payload.depth if payload.depth is not None else ENGINE_DEFAULT_DEPTH
    if depth < ENGINE_MIN_DEPTH or depth > ENGINE_MAX_DEPTH:
        raise HTTPException(status_code=400, detail="invalid_depth")
    return depth


def validate_state_payload(turn: str, board) -> None:
    """Validates shared state fields for endpoints."""
    if turn not in {"white", "black"}:
        raise HTTPException(status_code=400, detail="invalid_turn")
    if len(board) != 8 or any(len(rank) != 8 for rank in board):
        raise HTTPException(status_code=400, detail="invalid_board")


def build_fen(board: Board, turn: str, castling: str, en_passant, halfmove: int, fullmove: int):
    """Builds a FEN string from a Board and state fields."""
    return fen_from(board.to_matrix(), turn, castling, en_passant, halfmove, fullmove)


def build_castle(result):
    """Builds the castle move payload if castling occurred."""
    if not result["castle"]:
        return None
    return CastleMove(
        rook_from=MoveCoord(**result["castle"]["rook_from"]),
        rook_to=MoveCoord(**result["castle"]["rook_to"]),
    )


def build_notation(move: Move, result):
    """Creates LAN notation (or castling notation) for a validated move."""
    if result["castle"] and result["castle"]["rook_from"]["file"] == 7:
        return "O-O"
    if result["castle"] and result["castle"]["rook_from"]["file"] == 0:
        return "O-O-O"
    return move_to_lan(
        move.from_file,
        move.from_rank,
        move.to_file,
        move.to_rank,
        result["promotion"],
    )


def build_validate_response(move: Move, payload: ValidatePayload, result) -> ValidateResponse:
    """Assembles the validation response including check and game status."""
    next_turn = "black" if payload.turn == "white" else "white"
    in_check = is_in_check(result["board"], next_turn)
    has_moves = has_any_legal_move(
        result["board"],
        next_turn,
        result["castling"],
        result["en_passant"],
    )
    game_over = not has_moves
    outcome = None
    winner = None
    if game_over:
        if in_check:
            outcome = "checkmate"
            winner = "white" if next_turn == "black" else "black"
        else:
            outcome = "stalemate"
    return ValidateResponse(
        legal=True,
        reason="ok",
        notation=build_notation(move, result),
        fen=build_fen(
            result["board"],
            next_turn,
            result["castling"],
            result["en_passant"],
            result["halfmove"],
            result["fullmove"],
        ),
        castling=result["castling"],
        en_passant=(
            MoveCoord(file=result["en_passant"][0], rank=result["en_passant"][1])
            if result["en_passant"]
            else None
        ),
        halfmove=result["halfmove"],
        fullmove=result["fullmove"],
        capture=(
            MoveCoord(file=result["capture"][0], rank=result["capture"][1])
            if result["capture"]
            else None
        ),
        castle=build_castle(result),
        promotion=result["promotion"],
        check=in_check,
        game_over=game_over,
        outcome=outcome,
        winner=winner,
    )
