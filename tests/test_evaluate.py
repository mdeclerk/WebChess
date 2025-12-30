import pytest

from app.chess.base.board import Board
from app.chess.engine.evaluate import evaluate_board, score_to_win_probability


def test_evaluate_board_is_deterministic():
    board = Board.from_matrix(
        [
            [None, None, None, None, "k", None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, "P", None, None, None],
            [None, None, None, None, "K", None, None, None],
        ]
    )
    score_a = evaluate_board(board)
    score_b = evaluate_board(board)
    assert score_a == score_b


def test_score_to_win_probability_balanced():
    assert score_to_win_probability(0) == pytest.approx(0.5)
