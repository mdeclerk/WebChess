import pytest

from app.chess.base.board import Board, Piece
from app.chess.engine.evaluate import evaluate_board, positional_bonus, score_to_win_probability


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


def test_positional_bonus_mirrors_for_black():
    white_bonus = positional_bonus(Piece("P"), 0, 6)
    black_bonus = positional_bonus(Piece("p"), 0, 1)
    assert white_bonus == black_bonus


def test_positional_bonus_unknown_piece_returns_zero():
    assert positional_bonus(Piece("x"), 0, 0) == 0


def test_evaluate_board_reflects_positional_table():
    board_a2 = Board.from_matrix([[None] * 8 for _ in range(8)])
    board_a2.set_piece(0, 6, Piece("P"))
    board_a3 = Board.from_matrix([[None] * 8 for _ in range(8)])
    board_a3.set_piece(0, 5, Piece("P"))

    score_a2 = evaluate_board(board_a2)
    score_a3 = evaluate_board(board_a3)
    expected_delta = positional_bonus(Piece("P"), 0, 5) - positional_bonus(Piece("P"), 0, 6)
    assert score_a3 - score_a2 == expected_delta
