from typing import List, Optional, Tuple


def algebraic(file: int, rank: int) -> str:
    """Converts 0-based coordinates to algebraic square notation.

    Bridges engine coordinates with player-facing notation.

    Args:
        file: File index (0=a, 7=h).
        rank: Rank index (0=8th rank, 7=1st rank).

    Returns:
        Square in algebraic form, such as "e4".
    """
    return f"{chr(97 + file)}{8 - rank}"


def fen_from(
    board: List[List[Optional[str]]],
    turn: str,
    castling: str,
    en_passant: Optional[Tuple[int, int]],
    halfmove: int,
    fullmove: int,
) -> str:
    """Builds a FEN string from board state values.

    Provides a compact, standard snapshot of a position.

    Args:
        board: 8x8 matrix of piece codes or None.
        turn: Side to move ("white" or "black").
        castling: Castling rights string (e.g., "KQkq" or "-").
        en_passant: Optional en passant target square as (file, rank).
        halfmove: Halfmove clock for the fifty-move rule.
        fullmove: Fullmove number starting at 1 for White's first move.

    Returns:
        A full FEN string for the given position.
    """
    rows = []
    for rank in board:
        empty = 0
        row = ""
        for cell in rank:
            if cell is None:
                empty += 1
            else:
                if empty:
                    row += str(empty)
                    empty = 0
                row += cell
        if empty:
            row += str(empty)
        rows.append(row)
    board_part = "/".join(rows)
    side = "w" if turn == "white" else "b"
    castling_part = castling if castling else "-"
    en_passant_part = "-" if en_passant is None else algebraic(en_passant[0], en_passant[1])
    return f"{board_part} {side} {castling_part} {en_passant_part} {halfmove} {fullmove}"


def move_to_lan(
    from_file: int,
    from_rank: int,
    to_file: int,
    to_rank: int,
    promotion: Optional[str] = None,
) -> str:
    """Formats a move in long algebraic notation (LAN).

    Returns a clear, coordinate-based move string for UI/logging.

    Args:
        from_file: Source file index.
        from_rank: Source rank index.
        to_file: Destination file index.
        to_rank: Destination rank index.
        promotion: Optional promotion piece letter (e.g., "Q").

    Returns:
        LAN string such as "e2e4" or "e7e8=Q".
    """
    text = f"{algebraic(from_file, from_rank)}{algebraic(to_file, to_rank)}"
    if promotion:
        text = f"{text}={promotion}"
    return text
