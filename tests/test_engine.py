from app.chess.base.board import Board
from app.chess.base.move import Move
from app.chess.engine.search import MATE_SCORE, search_best_move, terminal_score
from app.chess.engine.moves import legal_moves, move_to_uci, move_sort_key
from app.chess.rules import is_legal_move


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


def board_from_positions(positions):
    b = [[None for _ in range(8)] for _ in range(8)]
    for (f, r), code in positions.items():
        b[r][f] = code
    return Board.from_matrix(b)



def test_engine_selects_legal_move():
    board = Board.from_matrix(initial_board_matrix())
    move, meta = search_best_move(board, "white", "KQkq", None, 0, 1, 1)
    assert move is not None
    legal, reason, _ = is_legal_move(board, move, "white", "KQkq", None)
    assert legal is True and reason == "ok"
    assert meta["nodes"] > 0


def test_engine_deterministic_move():
    board = Board.from_matrix(initial_board_matrix())
    move_a, meta_a = search_best_move(board, "white", "KQkq", None, 0, 1, 1)
    move_b, meta_b = search_best_move(board, "white", "KQkq", None, 0, 1, 1)
    assert move_a == move_b
    assert meta_a["score"] == meta_b["score"]


def test_move_to_uci_formats_coordinates():
    move = Move(0, 6, 0, 4)
    assert move_to_uci(move) == "a2a4"


def test_legal_moves_are_deterministically_sorted():
    board = Board.from_matrix(
        [
            [None, None, None, None, "k", None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ["R", None, None, None, "K", None, None, None],
        ]
    )
    moves = legal_moves(board, "white", "KQ", None)
    assert len(moves) > 1
    assert moves == sorted(moves, key=move_sort_key)


def test_terminal_score_for_checkmated_sides():
    black_mated = board_from_positions({(0, 0): "k", (2, 2): "K", (1, 1): "Q"})
    assert terminal_score(black_mated, "black") == MATE_SCORE

    white_mated = board_from_positions({(7, 7): "K", (5, 5): "k", (6, 6): "q"})
    assert terminal_score(white_mated, "white") == -MATE_SCORE


def test_search_best_move_reports_no_legal_moves_on_checkmate():
    board = board_from_positions({(0, 0): "k", (2, 2): "K", (1, 1): "Q"})
    move, meta = search_best_move(board, "black", "-", None, 0, 1, 1)
    assert move is None
    assert meta["no_legal_moves"] is True
