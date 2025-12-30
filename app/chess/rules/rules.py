from typing import Dict, List, Optional, Tuple

from app.chess.base.board import Board, Piece
from app.chess.base.move import Move

KNIGHT_STEPS = [
    (1, 2),
    (2, 1),
    (2, -1),
    (1, -2),
    (-1, -2),
    (-2, -1),
    (-2, 1),
    (-1, 2),
]
KING_STEPS = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
]


def in_bounds(file: int, rank: int) -> bool:
    """Checks if coordinates fall within the 8x8 board.

    Guards against illegal indexing when generating moves.

    Args:
        file: File index (0=a, 7=h).
        rank: Rank index (0=8th rank, 7=1st rank).

    Returns:
        True if the square is on the board.
    """
    return 0 <= file < 8 and 0 <= rank < 8


def find_king(board: Board, color: str) -> Optional[Tuple[int, int]]:
    """Finds the king position for a color.

    Supports check detection and legality tests.

    Args:
        board: Board to search.
        color: "white" or "black".

    Returns:
        (file, rank) for the king, or None if missing.
    """
    for rank in range(8):
        for file in range(8):
            piece = board.piece_at(file, rank)
            if piece and piece.kind == "K" and piece.color == color:
                return file, rank
    return None


def attacked_squares_for_piece(board: Board, file: int, rank: int, piece: Piece) -> List[Move]:
    """Lists squares a piece attacks from a given square.

    This ignores whether the moving side's king is in check; it is used for
    attack maps and check detection.

    Provides a fast attack map independent of full legality.

    Args:
        board: Current board position.
        file: Piece file index.
        rank: Piece rank index.
        piece: The piece to generate attacks for.

    Returns:
        Move objects that point to attacked squares.
    """
    moves: List[Move] = []
    if piece.kind == "P":
        direction = -1 if piece.color == "white" else 1
        for df in (-1, 1):
            nf, nr = file + df, rank + direction
            if in_bounds(nf, nr):
                moves.append(Move(file, rank, nf, nr))
        return moves

    if piece.kind == "N":
        for df, dr in KNIGHT_STEPS:
            nf, nr = file + df, rank + dr
            if in_bounds(nf, nr):
                moves.append(Move(file, rank, nf, nr))
        return moves

    if piece.kind in {"B", "R", "Q"}:
        directions = []
        if piece.kind in {"B", "Q"}:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
        if piece.kind in {"R", "Q"}:
            directions.extend([(1, 0), (-1, 0), (0, 1), (0, -1)])
        for df, dr in directions:
            nf, nr = file + df, rank + dr
            while in_bounds(nf, nr):
                moves.append(Move(file, rank, nf, nr))
                if board.piece_at(nf, nr) is not None:
                    break
                nf += df
                nr += dr
        return moves

    if piece.kind == "K":
        for df, dr in KING_STEPS:
            nf, nr = file + df, rank + dr
            if in_bounds(nf, nr):
                moves.append(Move(file, rank, nf, nr))
        return moves

    return moves


def is_square_attacked(board: Board, file: int, rank: int, by_color: str) -> bool:
    """Reports whether a square is attacked by a given color.

    Answers check and castling safety questions.

    Args:
        board: Current board position.
        file: File index of the target square.
        rank: Rank index of the target square.
        by_color: Attacking side ("white" or "black").

    Returns:
        True if any opposing piece attacks the square.
    """
    for r in range(8):
        for f in range(8):
            piece = board.piece_at(f, r)
            if not piece or piece.color != by_color:
                continue
            if any(
                move.to_file == file and move.to_rank == rank
                for move in attacked_squares_for_piece(board, f, r, piece)
            ):
                return True
    return False


def is_in_check(board: Board, color: str) -> bool:
    """Checks whether the given color's king is currently in check.

    Detects check, checkmate, and illegal moves.

    Args:
        board: Current board position.
        color: Side to evaluate.

    Returns:
        True if the king is attacked.
    """
    king_pos = find_king(board, color)
    if not king_pos:
        return False
    return is_square_attacked(
        board,
        king_pos[0],
        king_pos[1],
        "black" if color == "white" else "white",
    )


def has_any_legal_move(
    board: Board,
    color: str,
    castling_rights: str,
    en_passant: Optional[Tuple[int, int]],
) -> bool:
    """Determines if a side has at least one legal move.

    This is used to detect checkmate and stalemate.

    Decides whether the game is over.

    Args:
        board: Current board position.
        color: Side to move.
        castling_rights: Castling availability string.
        en_passant: Optional en passant target square.

    Returns:
        True if at least one legal move exists.
    """
    for rank in range(8):
        for file in range(8):
            piece = board.piece_at(file, rank)
            if not piece or piece.color != color:
                continue
            candidates = pseudo_legal_moves_for_piece(board, file, rank, piece, en_passant)
            if piece.kind == "K":
                candidates.append(Move(file, rank, file + 2, rank))
                candidates.append(Move(file, rank, file - 2, rank))
            for move in candidates:
                legal, _, _ = is_legal_move(board, move, color, castling_rights, en_passant)
                if legal:
                    return True
    return False


def pseudo_legal_moves_for_piece(
    board: Board,
    file: int,
    rank: int,
    piece: Piece,
    en_passant: Optional[Tuple[int, int]] = None,
) -> List[Move]:
    """Generates piece moves without considering check.

    Applies movement rules before king-safety filtering.

    Args:
        board: Current board position.
        file: Piece file index.
        rank: Piece rank index.
        piece: The piece to move.
        en_passant: Optional en passant target square.

    Returns:
        Move objects that are valid by movement rules only.
    """
    moves: List[Move] = []
    if piece.kind == "P":
        direction = -1 if piece.color == "white" else 1
        start_rank = 6 if piece.color == "white" else 1
        one_rank = rank + direction
        if in_bounds(file, one_rank) and board.piece_at(file, one_rank) is None:
            moves.append(Move(file, rank, file, one_rank))
            two_rank = rank + 2 * direction
            if rank == start_rank and board.piece_at(file, two_rank) is None:
                moves.append(Move(file, rank, file, two_rank))
        for df in (-1, 1):
            capture_file = file + df
            if in_bounds(capture_file, one_rank):
                target = board.piece_at(capture_file, one_rank)
                if target and target.color != piece.color:
                    moves.append(Move(file, rank, capture_file, one_rank))
                if en_passant and (capture_file, one_rank) == en_passant:
                    moves.append(Move(file, rank, capture_file, one_rank))
        return moves

    if piece.kind == "N":
        for df, dr in KNIGHT_STEPS:
            nf, nr = file + df, rank + dr
            if not in_bounds(nf, nr):
                continue
            target = board.piece_at(nf, nr)
            if target is None or target.color != piece.color:
                moves.append(Move(file, rank, nf, nr))
        return moves

    if piece.kind in {"B", "R", "Q"}:
        directions = []
        if piece.kind in {"B", "Q"}:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
        if piece.kind in {"R", "Q"}:
            directions.extend([(1, 0), (-1, 0), (0, 1), (0, -1)])
        for df, dr in directions:
            nf, nr = file + df, rank + dr
            while in_bounds(nf, nr):
                target = board.piece_at(nf, nr)
                if target is None:
                    moves.append(Move(file, rank, nf, nr))
                else:
                    if target.color != piece.color:
                        moves.append(Move(file, rank, nf, nr))
                    break
                nf += df
                nr += dr
        return moves

    if piece.kind == "K":
        for df, dr in KING_STEPS:
            nf, nr = file + df, rank + dr
            if not in_bounds(nf, nr):
                continue
            target = board.piece_at(nf, nr)
            if target is None or target.color != piece.color:
                moves.append(Move(file, rank, nf, nr))
        return moves

    return moves


def is_legal_move(
    board: Board,
    move: Move,
    color: str,
    castling_rights: str,
    en_passant: Optional[Tuple[int, int]],
) -> Tuple[bool, str, Dict[str, bool]]:
    """Validates a move against chess rules and king safety.

    Centralizes legality checks for API and engine usage.

    Args:
        board: Current board position.
        move: Proposed move.
        color: Side to move ("white" or "black").
        castling_rights: Castling availability string.
        en_passant: Optional en passant target square.

    Returns:
        Tuple of (is_legal, reason, special_flags). The flags include
        `is_castle` and `is_en_passant`.
    """
    special = {"is_castle": False, "is_en_passant": False}
    if not in_bounds(move.from_file, move.from_rank) or not in_bounds(
        move.to_file, move.to_rank
    ):
        return False, "out_of_bounds", special

    piece = board.piece_at(move.from_file, move.from_rank)
    if not piece:
        return False, "no_piece", special
    if piece.color != color:
        return False, "wrong_color", special

    target = board.piece_at(move.to_file, move.to_rank)
    if target and target.color == color:
        return False, "occupied_by_ally", special

    if piece.kind == "K" and move.from_rank == move.to_rank and abs(
        move.to_file - move.from_file
    ) == 2:
        rights = set(castling_rights) if castling_rights != "-" else set()
        if color == "white":
            rank = 7
            king_side = "K"
            queen_side = "Q"
        else:
            rank = 0
            king_side = "k"
            queen_side = "q"
        if move.from_rank != rank or move.to_rank != rank:
            return False, "illegal_castle", special
        if move.to_file == 6:
            if king_side not in rights:
                return False, "castle_rights", special
            rook_file = 7
            between = [5, 6]
            pass_through = [4, 5, 6]
        elif move.to_file == 2:
            if queen_side not in rights:
                return False, "castle_rights", special
            rook_file = 0
            between = [1, 2, 3]
            pass_through = [4, 3, 2]
        else:
            return False, "illegal_castle", special
        rook = board.piece_at(rook_file, rank)
        if not rook or rook.kind != "R" or rook.color != color:
            return False, "rook_missing", special
        if any(board.piece_at(f, rank) for f in between):
            return False, "castle_blocked", special
        if is_square_attacked(board, move.from_file, rank, "black" if color == "white" else "white"):
            return False, "king_in_check", special
        for f in pass_through[1:]:
            if is_square_attacked(board, f, rank, "black" if color == "white" else "white"):
                return False, "castle_through_check", special
        special["is_castle"] = True
    else:
        pseudo_moves = pseudo_legal_moves_for_piece(
            board, move.from_file, move.from_rank, piece, en_passant
        )
        if not any(
            m.to_file == move.to_file and m.to_rank == move.to_rank for m in pseudo_moves
        ):
            return False, "illegal_move", special
        if (
            piece.kind == "P"
            and en_passant
            and (move.to_file, move.to_rank) == en_passant
            and target is None
        ):
            special["is_en_passant"] = True

    test_board = board.clone()
    if special["is_en_passant"]:
        capture_rank = move.from_rank
        test_board.set_piece(move.to_file, capture_rank, None)
    if special["is_castle"]:
        if move.to_file == 6:
            rook_from, rook_to = 7, 5
        else:
            rook_from, rook_to = 0, 3
        rook = test_board.piece_at(rook_from, move.from_rank)
        test_board.set_piece(rook_to, move.from_rank, rook)
        test_board.set_piece(rook_from, move.from_rank, None)
    test_board.set_piece(move.to_file, move.to_rank, piece)
    test_board.set_piece(move.from_file, move.from_rank, None)

    king_pos = find_king(test_board, color)
    if not king_pos:
        return False, "king_missing", special
    if is_square_attacked(test_board, king_pos[0], king_pos[1], "black" if color == "white" else "white"):
        return False, "king_in_check", special

    return True, "ok", special


def update_castling_rights(
    castling_rights: str,
    move: Move,
    moving_piece: Piece,
    captured_piece: Optional[Piece],
) -> str:
    """Updates castling rights after a move and optional capture.

    Tracks rook/king movement to enforce future castling rules.

    Args:
        castling_rights: Current castling availability string.
        move: Move that was played.
        moving_piece: The piece that moved.
        captured_piece: Captured piece, if any.

    Returns:
        Updated castling rights string.
    """
    rights = set(castling_rights) if castling_rights != "-" else set()
    if moving_piece.kind == "K":
        if moving_piece.color == "white":
            rights.discard("K")
            rights.discard("Q")
        else:
            rights.discard("k")
            rights.discard("q")
    if moving_piece.kind == "R":
        if moving_piece.color == "white":
            if move.from_file == 0 and move.from_rank == 7:
                rights.discard("Q")
            if move.from_file == 7 and move.from_rank == 7:
                rights.discard("K")
        else:
            if move.from_file == 0 and move.from_rank == 0:
                rights.discard("q")
            if move.from_file == 7 and move.from_rank == 0:
                rights.discard("k")
    if captured_piece and captured_piece.kind == "R":
        if captured_piece.color == "white":
            if move.to_file == 0 and move.to_rank == 7:
                rights.discard("Q")
            if move.to_file == 7 and move.to_rank == 7:
                rights.discard("K")
        else:
            if move.to_file == 0 and move.to_rank == 0:
                rights.discard("q")
            if move.to_file == 7 and move.to_rank == 0:
                rights.discard("k")
    ordered = "".join([c for c in "KQkq" if c in rights])
    return ordered if ordered else "-"


def apply_move(
    board: Board,
    move: Move,
    color: str,
    castling_rights: str,
    en_passant: Optional[Tuple[int, int]],
    halfmove: int,
    fullmove: int,
) -> Tuple[bool, Dict[str, object]]:
    """Applies a legal move and returns updated game state details.

    Mutates game state while preserving chess rule invariants.

    Args:
        board: Board to mutate in-place.
        move: Proposed move.
        color: Side to move ("white" or "black").
        castling_rights: Current castling rights string.
        en_passant: Optional en passant target square.
        halfmove: Halfmove clock before the move.
        fullmove: Fullmove number before the move.

    Returns:
        (is_legal, result) where result holds updated board state fields.
    """
    legal, reason, special = is_legal_move(board, move, color, castling_rights, en_passant)
    if not legal:
        return False, {"legal": False, "reason": reason}

    moving_piece = board.piece_at(move.from_file, move.from_rank)
    target_piece = board.piece_at(move.to_file, move.to_rank)
    capture_square: Optional[Tuple[int, int]] = None

    if special["is_en_passant"]:
        capture_square = (move.to_file, move.from_rank)
        board.set_piece(capture_square[0], capture_square[1], None)
        target_piece = Piece("p" if color == "white" else "P")
    elif target_piece:
        capture_square = (move.to_file, move.to_rank)

    board.set_piece(move.to_file, move.to_rank, moving_piece)
    board.set_piece(move.from_file, move.from_rank, None)

    castle_move = None
    if special["is_castle"]:
        if move.to_file == 6:
            rook_from, rook_to = 7, 5
        else:
            rook_from, rook_to = 0, 3
        rook = board.piece_at(rook_from, move.from_rank)
        board.set_piece(rook_to, move.from_rank, rook)
        board.set_piece(rook_from, move.from_rank, None)
        castle_move = {
            "rook_from": {"file": rook_from, "rank": move.from_rank},
            "rook_to": {"file": rook_to, "rank": move.from_rank},
        }

    promotion = None
    if moving_piece and moving_piece.kind == "P":
        if (moving_piece.color == "white" and move.to_rank == 0) or (
            moving_piece.color == "black" and move.to_rank == 7
        ):
            new_code = "Q" if moving_piece.color == "white" else "q"
            board.set_piece(move.to_file, move.to_rank, Piece(new_code))
            promotion = "Q"

    updated_castling = update_castling_rights(castling_rights, move, moving_piece, target_piece)

    new_en_passant = None
    if moving_piece and moving_piece.kind == "P" and abs(move.to_rank - move.from_rank) == 2:
        direction = -1 if moving_piece.color == "white" else 1
        new_en_passant = (move.from_file, move.from_rank + direction)

    reset_halfmove = (moving_piece and moving_piece.kind == "P") or capture_square is not None
    new_halfmove = 0 if reset_halfmove else halfmove + 1
    new_fullmove = fullmove + 1 if color == "black" else fullmove

    result = {
        "legal": True,
        "reason": "ok",
        "board": board,
        "castling": updated_castling,
        "en_passant": new_en_passant,
        "halfmove": new_halfmove,
        "fullmove": new_fullmove,
        "capture": capture_square,
        "castle": castle_move,
        "promotion": promotion,
    }
    return True, result
