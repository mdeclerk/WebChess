from typing import Optional, Tuple

from app.chess.base.board import Board
from app.chess.base.move import Move
from app.chess.engine.evaluate import evaluate_board
from app.chess.engine.moves import legal_moves
from app.chess.rules import apply_move, is_in_check

MATE_SCORE = 100000


def search_best_move(
    board: Board,
    color: str,
    castling_rights: str,
    en_passant: Optional[Tuple[int, int]],
    halfmove: int,
    fullmove: int,
    depth: int,
) -> tuple[Optional[Move], dict]:
    """Finds the best move using minimax with alpha-beta pruning.

    Selects a strong move while keeping the algorithm educational.
    It generates all legal moves for the side to move, then simulates each
    candidate with a depth-limited minimax search. The result is the move
    with the best evaluation for the current player, along with metadata
    that explains how much of the game tree was searched.

    Args:
        board: Current board position.
        color: Side to move ("white" or "black").
        castling_rights: Castling availability string.
        en_passant: Optional en passant target square.
        halfmove: Halfmove clock.
        fullmove: Fullmove number.
        depth: Search depth in plies.

    Returns:
        Best move (or None) and metadata including depth, nodes, and score.
        If there are no legal moves, the move is None and the metadata marks
        the position as terminal.
    """
    nodes = 0
    best_move: Optional[Move] = None
    best_score = None

    moves = legal_moves(board, color, castling_rights, en_passant)
    if not moves:
        score = terminal_score(board, color)
        return None, {"depth": depth, "nodes": 1, "score": score, "no_legal_moves": True}

    for move in moves:
        next_state = apply_move_to_clone(
            board,
            move,
            color,
            castling_rights,
            en_passant,
            halfmove,
            fullmove,
        )
        if not next_state:
            continue
        next_board, next_castling, next_en_passant, next_halfmove, next_fullmove = next_state
        score, child_nodes = minimax(
            next_board,
            "black" if color == "white" else "white",
            next_castling,
            next_en_passant,
            next_halfmove,
            next_fullmove,
            depth - 1,
            -MATE_SCORE,
            MATE_SCORE,
        )
        nodes += child_nodes
        if best_score is None:
            best_score = score
            best_move = move
            continue
        if color == "white":
            if score > best_score:
                best_score = score
                best_move = move
        else:
            if score < best_score:
                best_score = score
                best_move = move

    if best_score is None:
        best_score = evaluate_board(board)

    return best_move, {"depth": depth, "nodes": nodes, "score": best_score, "no_legal_moves": False}


def minimax(
    board: Board,
    color: str,
    castling_rights: str,
    en_passant: Optional[Tuple[int, int]],
    halfmove: int,
    fullmove: int,
    depth: int,
    alpha: int,
    beta: int,
) -> tuple[int, int]:
    """Evaluates a position with depth-limited minimax.

    Explores the game tree with bounded depth and pruning. At each level,
    the side to move chooses the best score for itself: White tries to
    maximize the evaluation, Black tries to minimize it. Alpha-beta pruning
    skips branches that cannot improve the final result, which keeps the
    search fast enough for a teaching engine.

    Args:
        board: Current board position.
        color: Side to move.
        castling_rights: Castling availability string.
        en_passant: Optional en passant target square.
        halfmove: Halfmove clock.
        fullmove: Fullmove number.
        depth: Remaining search depth.
        alpha: Best score for the maximizing side so far.
        beta: Best score for the minimizing side so far.

    Returns:
        Tuple of (score, nodes_searched). The score is from White's
        perspective; positive favors White, negative favors Black.
    """
    moves = legal_moves(board, color, castling_rights, en_passant)
    if depth <= 0 or not moves:
        score = terminal_score(board, color) if not moves else evaluate_board(board)
        return score, 1

    nodes = 0
    if color == "white":
        value = -MATE_SCORE
        for move in moves:
            next_state = apply_move_to_clone(
                board,
                move,
                color,
                castling_rights,
                en_passant,
                halfmove,
                fullmove,
            )
            if not next_state:
                continue
            next_board, next_castling, next_en_passant, next_halfmove, next_fullmove = next_state
            score, child_nodes = minimax(
                next_board,
                "black",
                next_castling,
                next_en_passant,
                next_halfmove,
                next_fullmove,
                depth - 1,
                alpha,
                beta,
            )
            nodes += child_nodes
            value = max(value, score)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value, nodes

    value = MATE_SCORE
    for move in moves:
        next_state = apply_move_to_clone(
            board,
            move,
            color,
            castling_rights,
            en_passant,
            halfmove,
            fullmove,
        )
        if not next_state:
            continue
        next_board, next_castling, next_en_passant, next_halfmove, next_fullmove = next_state
        score, child_nodes = minimax(
            next_board,
            "white",
            next_castling,
            next_en_passant,
            next_halfmove,
            next_fullmove,
            depth - 1,
            alpha,
            beta,
        )
        nodes += child_nodes
        value = min(value, score)
        beta = min(beta, value)
        if beta <= alpha:
            break
    return value, nodes


def apply_move_to_clone(
    board: Board,
    move: Move,
    color: str,
    castling_rights: str,
    en_passant: Optional[Tuple[int, int]],
    halfmove: int,
    fullmove: int,
) -> Optional[tuple[Board, str, Optional[Tuple[int, int]], int, int]]:
    """Applies a move to a cloned board for search.

    Simulates moves safely without mutating the original board.

    Args:
        board: Current board position.
        move: Move to apply.
        color: Side to move.
        castling_rights: Castling availability string.
        en_passant: Optional en passant target square.
        halfmove: Halfmove clock.
        fullmove: Fullmove number.

    Returns:
        Tuple of updated board state values, or None if move is illegal.
    """
    cloned = board.clone()
    legal, result = apply_move(
        cloned,
        move,
        color,
        castling_rights,
        en_passant,
        halfmove,
        fullmove,
    )
    if not legal:
        return None
    return (
        result["board"],
        result["castling"],
        result["en_passant"],
        result["halfmove"],
        result["fullmove"],
    )


def terminal_score(board: Board, color: str) -> int:
    """Scores terminal positions (checkmate or stalemate) from the side to move.

    Distinguishes checkmate from stalemate in search leaves.

    Args:
        board: Current board position.
        color: Side to move.

    Returns:
        Mate score if checkmated, otherwise 0 for stalemate or non-terminal.
    """
    if is_in_check(board, color):
        return -MATE_SCORE if color == "white" else MATE_SCORE
    return 0
