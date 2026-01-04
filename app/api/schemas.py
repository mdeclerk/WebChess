from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MoveCoord(BaseModel):
    """Board coordinate in file/rank form."""

    file: int = Field(ge=0, le=7)
    rank: int = Field(ge=0, le=7)


class MovePayload(BaseModel):
    """Move payload with origin and destination coordinates."""

    from_: MoveCoord = Field(alias="from")
    to_: MoveCoord = Field(alias="to")

    model_config = ConfigDict(populate_by_name=True)


class StatePayload(BaseModel):
    """Base game state payload shared by endpoints."""

    board: List[List[Optional[str]]]
    turn: str
    castling: str = "KQkq"
    en_passant: Optional[MoveCoord] = None
    halfmove: int = 0
    fullmove: int = 1


class ValidatePayload(StatePayload):
    """Validation request payload including a move."""

    move: MovePayload


class CastleMove(BaseModel):
    """Castling move detail for rook movement."""

    rook_from: MoveCoord
    rook_to: MoveCoord


class ValidateResponse(BaseModel):
    """Response describing move legality and resulting state."""

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
    """Engine request payload with optional search depth."""

    depth: Optional[int] = None


class EngineMoveResponse(BaseModel):
    """Engine response with chosen move and analysis metadata."""

    move: Optional[str] = None
    from_: Optional[MoveCoord] = Field(default=None, alias="from")
    to_: Optional[MoveCoord] = Field(default=None, alias="to")
    depth: int
    nodes: int
    score: int
    no_legal_moves: bool = False
    error: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class WinProbabilityResponse(BaseModel):
    """Static evaluation win probabilities for each side."""

    white: float
    black: float
    score: int
