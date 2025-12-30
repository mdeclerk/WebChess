from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.chess.base.board import Board
from app.chess.base.move import Move
from app.chess.engine import move_to_uci, score_to_win_probability, search_best_move
from app.chess.base.notation import fen_from, move_to_lan
from app.chess.rules import apply_move, has_any_legal_move, is_in_check

router = APIRouter()


@router.get("/health")
def health():
    """Health check endpoint for service monitoring.

    Provides a lightweight signal for uptime checks.

    Returns:
        Status payload indicating the API is reachable.
    """
    return {"status": "ok"}


class MoveCoord(BaseModel):
    file: int = Field(ge=0, le=7)
    rank: int = Field(ge=0, le=7)


class MovePayload(BaseModel):
    from_: MoveCoord = Field(alias="from")
    to: MoveCoord


class StatePayload(BaseModel):
    board: List[List[Optional[str]]]
    turn: str
    castling: str = "KQkq"
    en_passant: Optional[MoveCoord] = None
    halfmove: int = 0
    fullmove: int = 1


class ValidatePayload(StatePayload):
    move: MovePayload


class CastleMove(BaseModel):
    rook_from: MoveCoord
    rook_to: MoveCoord


class ValidateResponse(BaseModel):
    legal: bool
    reason: str
    notation: Optional[str] = None
    fen: Optional[str] = None
    castling: Optional[str] = None
    en_passant: Optional[MoveCoord] = None
    halfmove: Optional[int] = None
    fullmove: Optional[int] = None
    capture: Optional[MoveCoord] = None
    castle: Optional[CastleMove] = None
    promotion: Optional[str] = None
    check: bool = False
    game_over: bool = False
    outcome: Optional[str] = None
    winner: Optional[str] = None


class EngineMovePayload(StatePayload):
    depth: Optional[int] = None


class EngineMoveResponse(BaseModel):
    move: Optional[str] = None
    from_: Optional[MoveCoord] = Field(default=None, alias="from")
    to: Optional[MoveCoord] = None
    depth: int
    nodes: int
    score: int
    no_legal_moves: bool = False
    error: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class WinProbabilityResponse(BaseModel):
    white: float
    black: float
    depth: int
    nodes: int
    score: int


ENGINE_MIN_DEPTH = 1
ENGINE_MAX_DEPTH = 4
ENGINE_DEFAULT_DEPTH = 2


def en_passant_tuple(en_passant: Optional[MoveCoord]):
    """Converts an optional MoveCoord into a tuple for rule helpers.

    Normalizes en passant inputs for domain functions.

    Args:
        en_passant: Optional en passant target square.

    Returns:
        (file, rank) tuple or None.
    """
    return (en_passant.file, en_passant.rank) if en_passant else None


def validate_engine_payload(payload: EngineMovePayload) -> int:
    """Validates engine payload basics and resolves search depth.

    Fails fast on invalid engine requests with clear errors.

    Args:
        payload: Engine request payload.

    Returns:
        Resolved depth to use for search.

    Raises:
        HTTPException: If the payload is invalid or depth is out of range.
    """
    if payload.turn not in {"white", "black"}:
        raise HTTPException(status_code=400, detail="invalid_turn")
    if len(payload.board) != 8 or any(len(rank) != 8 for rank in payload.board):
        raise HTTPException(status_code=400, detail="invalid_board")
    depth = payload.depth if payload.depth is not None else ENGINE_DEFAULT_DEPTH
    if depth < ENGINE_MIN_DEPTH or depth > ENGINE_MAX_DEPTH:
        raise HTTPException(status_code=400, detail="invalid_depth")
    return depth


def build_fen(board: Board, turn: str, castling: str, en_passant, halfmove: int, fullmove: int):
    """Builds a FEN string from a Board and state fields.

    Keeps FEN construction consistent across endpoints.

    Args:
        board: Current board position.
        turn: Side to move ("white" or "black").
        castling: Castling availability string.
        en_passant: Optional en passant target square.
        halfmove: Halfmove clock.
        fullmove: Fullmove number.

    Returns:
        FEN string describing the position.
    """
    return fen_from(board.to_matrix(), turn, castling, en_passant, halfmove, fullmove)


def build_castle(result):
    """Builds the castle move payload if castling occurred.

    Shapes castle metadata for the API response.

    Args:
        result: Move application result dict.

    Returns:
        CastleMove payload or None.
    """
    if not result["castle"]:
        return None
    return CastleMove(
        rook_from=MoveCoord(**result["castle"]["rook_from"]),
        rook_to=MoveCoord(**result["castle"]["rook_to"]),
    )


def build_notation(move: Move, result):
    """Creates LAN notation (or castling notation) for a validated move.

    Returns a readable move label for the UI.

    Args:
        move: Move that was validated.
        result: Move application result dict.

    Returns:
        Notation string such as "e2e4" or "O-O".
    """
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
    """Assembles the validation response including check and game status.

    Provides the UI with all derived state in one response.

    Args:
        move: Move that was validated.
        payload: Incoming request payload.
        result: Move application result dict.

    Returns:
        Fully populated validation response.
    """
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
        to_file=payload.move.to.file,
        to_rank=payload.move.to.rank,
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
    """Estimates win probabilities from the engine evaluation score.

    Exposes a simple strength signal for the current position.

    Args:
        payload: Game state and optional depth.

    Returns:
        Win probability response for White and Black.
    """
    depth = validate_engine_payload(payload)
    board = Board.from_matrix(payload.board)
    _, meta = search_best_move(
        board,
        payload.turn,
        payload.castling,
        en_passant_tuple(payload.en_passant),
        payload.halfmove,
        payload.fullmove,
        depth,
    )
    white = score_to_win_probability(meta["score"])
    return WinProbabilityResponse(
        white=white,
        black=1.0 - white,
        depth=meta["depth"],
        nodes=meta["nodes"],
        score=meta["score"],
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
