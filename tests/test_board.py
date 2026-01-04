from app.chess.base.board import Board, Piece


def test_piece_color_and_kind():
    white = Piece("P")
    black = Piece("q")
    assert white.color == "white"
    assert white.kind == "P"
    assert black.color == "black"
    assert black.kind == "Q"


def test_board_round_trip_matrix():
    matrix = [
        list("rnbqkbnr"),
        list("pppppppp"),
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        list("PPPPPPPP"),
        list("RNBQKBNR"),
    ]
    board = Board.from_matrix(matrix)
    assert board.to_matrix() == matrix


def test_board_clone_is_independent():
    board = Board.from_matrix([[None] * 8 for _ in range(8)])
    clone = board.clone()
    clone.set_piece(0, 0, Piece("K"))
    assert board.piece_at(0, 0) is None
    assert clone.piece_at(0, 0) is not None
