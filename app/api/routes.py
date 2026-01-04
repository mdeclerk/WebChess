from fastapi import APIRouter

from app.api.helpers import (
    build_validate_response,
    en_passant_tuple,
    validate_engine_payload,
    validate_state_payload,
)
from app.api.schemas import (
    EngineMovePayload,
    EngineMoveResponse,
    MoveCoord,
    StatePayload,
    ValidatePayload,
    ValidateResponse,
    WinProbabilityResponse,
)
from app.chess.base.board import Board
from app.chess.base.move import Move
from app.chess.base.notation import fen_from
from app.chess.engine import move_to_uci, score_to_win_probability, search_best_move
from app.chess.engine.evaluate import evaluate_board
from app.chess.rules import apply_move

router = APIRouter()


@router.get("/health")
def health():
    """Health check endpoint for service monitoring.

    Provides a lightweight signal for uptime checks.

    Returns:
        Status payload indicating the API is reachable.
    """
    return {"status": "ok"}


@router.post("/validate", response_model=ValidateResponse)
def validate_move(payload: ValidatePayload):
    """Validates a proposed move and returns updated game state details.

    Centralizes legality checks and state updates for the UI.

    Args:
        payload: Game state and proposed move.

    Returns:
        Validation response with legality, notation, and next state.
    """
    board = Board.from_matrix(payload.board)
    move = Move(
        from_file=payload.move.from_.file,
        from_rank=payload.move.from_.rank,
        to_file=payload.move.to_.file,
        to_rank=payload.move.to_.rank,
    )
    en_passant = en_passant_tuple(payload.en_passant)
    legal, result = apply_move(
        board,
        move,
        payload.turn,
        payload.castling,
        en_passant,
        payload.halfmove,
        payload.fullmove,
    )
    if not legal:
        return ValidateResponse(legal=False, reason=result["reason"])
    return build_validate_response(move, payload, result)


@router.post("/move", response_model=EngineMoveResponse)
def engine_move(payload: EngineMovePayload):
    """Returns an engine-selected move for the current position.

    Exposes a server-side move suggestion for the UI.

    Args:
        payload: Game state and optional depth.

    Returns:
        Engine response containing the selected move and analysis metadata.
    """
    depth = validate_engine_payload(payload)
    board = Board.from_matrix(payload.board)
    move, meta = search_best_move(
        board,
        payload.turn,
        payload.castling,
        en_passant_tuple(payload.en_passant),
        payload.halfmove,
        payload.fullmove,
        depth,
    )
    if not move or meta.get("no_legal_moves"):
        return EngineMoveResponse(
            move=None,
            from_=None,
            to=None,
            depth=meta["depth"],
            nodes=meta["nodes"],
            score=meta["score"],
            no_legal_moves=True,
        )
    return EngineMoveResponse(
        move=move_to_uci(move),
        from_=MoveCoord(file=move.from_file, rank=move.from_rank),
        to=MoveCoord(file=move.to_file, rank=move.to_rank),
        depth=meta["depth"],
        nodes=meta["nodes"],
        score=meta["score"],
        no_legal_moves=False,
    )


@router.post("/win-probability", response_model=WinProbabilityResponse)
def win_probability(payload: EngineMovePayload):
    """Estimates win probabilities from a static board evaluation.

    Provides an instant strength signal for the current position using
    static evaluation without search. Much faster than move generation.

    Args:
        payload: Game state (depth parameter ignored if present).

    Returns:
        Win probability response for White and Black.
    """
    validate_state_payload(payload.turn, payload.board)
    board = Board.from_matrix(payload.board)
    score = evaluate_board(board)
    white = score_to_win_probability(score)
    return WinProbabilityResponse(
        white=white,
        black=1.0 - white,
        score=score,
    )


@router.post("/fen")
def fen(payload: StatePayload):
    """Returns the FEN string for the provided game state.

    Provides a compact position snapshot for clients.

    Args:
        payload: Game state values.

    Returns:
        Payload containing the generated FEN string.
    """
    fen_value = fen_from(
        payload.board,
        payload.turn,
        payload.castling,
        en_passant_tuple(payload.en_passant),
        payload.halfmove,
        payload.fullmove,
    )
    return {"fen": fen_value}
