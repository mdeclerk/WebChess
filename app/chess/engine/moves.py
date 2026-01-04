from typing import List, Optional, Tuple

from app.chess.base.move import Move
from app.chess.base.board import Board
from app.chess.rules import generate_legal_moves


def legal_moves(
    board: Board,
    color: str,
    castling_rights: str,
    en_passant: Optional[Tuple[int, int]],
) -> List[Move]:
    """Generates all legal moves for the side to move.

    Provides a complete move list for search and validation.

    Args:
        board: Current board position.
        color: Side to move ("white" or "black").
        castling_rights: Castling availability string.
        en_passant: Optional en passant target square.

    Returns:
        Sorted list of legal moves.
    """
    moves = list(generate_legal_moves(board, color, castling_rights, en_passant))
    return sorted(moves, key=move_sort_key)


def move_sort_key(move: Move) -> tuple[int, int, int, int]:
    """Defines a stable ordering for moves to keep results deterministic.

    Ensures reproducible engine choices when scores tie.

    Args:
        move: Move to sort.

    Returns:
        Tuple used for sorting in a consistent order.
    """
    return (move.from_file, move.from_rank, move.to_file, move.to_rank)


def move_to_uci(move: Move) -> str:
    """Formats a move in UCI notation (e.g., "e2e4").

    Provides a compact engine-friendly move string.

    Args:
        move: Move to format.

    Returns:
        UCI string representation.
    """
    return (
        f"{_file_to_char(move.from_file)}{_rank_to_char(move.from_rank)}"
        f"{_file_to_char(move.to_file)}{_rank_to_char(move.to_rank)}"
    )


def _file_to_char(file: int) -> str:
    """Converts a file index to a lowercase file letter.

    Keeps file rendering consistent across notation helpers.

    Args:
        file: File index (0=a, 7=h).

    Returns:
        Lowercase file letter.
    """
    return chr(ord("a") + file)


def _rank_to_char(rank: int) -> str:
    """Converts a rank index to a 1-based rank number.

    Keeps rank rendering consistent across notation helpers.

    Args:
        rank: Rank index (0=8th rank, 7=1st rank).

    Returns:
        Rank number as a string.
    """
    return str(8 - rank)
