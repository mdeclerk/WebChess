from app.chess.base.board import Board
from app.chess.base.move import Move
from app.chess.engine.evaluate import evaluate_board
from app.chess.engine import search as search_module
from app.chess.engine.search import minimax, terminal_score
from conftest import board_from_positions


def test_minimax_depth_zero_uses_evaluate():
    board = Board.from_matrix(
        [
            [None, None, None, None, "k", None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, "K", None, None, None],
        ]
    )
    score, nodes = minimax(board, "white", "-", None, 0, 1, 0, -100000, 100000)
    assert score == evaluate_board(board)
    assert nodes == 1


def test_terminal_score_stalemate_is_zero():
    board = board_from_positions(
        {(0, 0): "k", (2, 2): "K", (1, 2): "Q"}
    )
    assert terminal_score(board, "black") == 0


def test_apply_move_to_clone_returns_none_for_illegal_move():
    board = Board.from_matrix([[None] * 8 for _ in range(8)])
    move = Move(0, 0, 0, 1)
    assert search_module.apply_move_to_clone(board, move, "white", "-", None, 0, 1) is None


def test_search_best_move_falls_back_to_evaluate_on_invalid_moves(monkeypatch):
    board = Board.from_matrix([[None] * 8 for _ in range(8)])

    def fake_moves(*_args, **_kwargs):
        return [Move(0, 0, 0, 1)]

    monkeypatch.setattr(search_module, "legal_moves", fake_moves)
    monkeypatch.setattr(search_module, "apply_move_to_clone", lambda *args, **kwargs: None)

    move, meta = search_module.search_best_move(board, "white", "-", None, 0, 1, 1)
    assert move is None
    assert meta["score"] == evaluate_board(board)


def test_minimax_white_and_black_paths():
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
    score_white, nodes_white = minimax(board, "white", "K", None, 0, 1, 1, -100000, 100000)
    score_black, nodes_black = minimax(board, "black", "K", None, 0, 1, 1, -100000, 100000)
    assert nodes_white >= 1
    assert nodes_black >= 1
    assert isinstance(score_white, int)
    assert isinstance(score_black, int)


def test_search_best_move_updates_for_black(monkeypatch):
    board = Board.from_matrix([[None] * 8 for _ in range(8)])
    moves = [Move(0, 0, 0, 1), Move(0, 0, 0, 2)]
    scores = [10, -5]

    monkeypatch.setattr(search_module, "legal_moves", lambda *args, **kwargs: moves)
    monkeypatch.setattr(
        search_module,
        "apply_move_to_clone",
        lambda *args, **kwargs: (board, "-", None, 0, 1),
    )

    def fake_minimax(*_args, **_kwargs):
        return scores.pop(0), 1

    monkeypatch.setattr(search_module, "minimax", fake_minimax)
    move, meta = search_module.search_best_move(board, "black", "-", None, 0, 1, 1)
    assert move == moves[1]
    assert meta["score"] == -5


def test_minimax_skips_illegal_child_paths(monkeypatch):
    board = Board.from_matrix([[None] * 8 for _ in range(8)])
    moves = [Move(0, 0, 0, 1)]
    monkeypatch.setattr(search_module, "legal_moves", lambda *args, **kwargs: moves)
    monkeypatch.setattr(search_module, "apply_move_to_clone", lambda *args, **kwargs: None)

    score_white, nodes_white = search_module.minimax(board, "white", "-", None, 0, 1, 1, -100000, 100000)
    score_black, nodes_black = search_module.minimax(board, "black", "-", None, 0, 1, 1, -100000, 100000)
    assert nodes_white == 0
    assert nodes_black == 0
    assert isinstance(score_white, int)
    assert isinstance(score_black, int)


def test_minimax_prunes_when_alpha_exceeds_beta():
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
    score_white, nodes_white = minimax(board, "white", "K", None, 0, 1, 1, 1, 0)
    score_black, nodes_black = minimax(board, "black", "K", None, 0, 1, 1, 0, -1)
    assert nodes_white >= 1
    assert nodes_black >= 1
    assert isinstance(score_white, int)
    assert isinstance(score_black, int)
