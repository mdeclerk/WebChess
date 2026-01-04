from app.chess.base import notation
from conftest import initial_board_matrix


def test_fen_initial_position():
    board = initial_board_matrix()
    fen = notation.fen_from(board, "white", "KQkq", None, 0, 1)
    assert fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_fen_with_en_passant_and_halfmove_fullmove():
    board = [[None] * 8 for _ in range(8)]
    board[4][4] = "P"  # e4 (rank index 4 => algebraic e4)
    board[0][0] = "k"
    board[7][7] = "K"
    # en_passant at e3 (file 4, rank 5 -> algebraic e3 because algebraic uses 8-rank)
    fen = notation.fen_from(board, "black", "-", (4, 5), 3, 10)
    assert "e3" in fen.split()[3]
    assert fen.endswith("3 10")


def test_move_to_lan_with_and_without_promotion():
    assert notation.move_to_lan(0, 1, 0, 0) == "a7a8"
    assert notation.move_to_lan(0, 1, 0, 0, promotion="Q") == "a7a8=Q"
