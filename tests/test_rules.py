import pytest

from app.chess.base.board import Board
from app.chess.base.move import Move
from app.chess.rules import (
    is_legal_move,
    apply_move,
    has_any_legal_move,
    is_in_check,
    pseudo_legal_moves_for_piece,
    update_castling_rights,
)
from app.chess.base import notation
from app.chess.rules.rules import is_square_attacked


def empty_board():
    return Board.from_matrix([[None for _ in range(8)] for _ in range(8)])


def board_from_positions(positions):
    b = [[None for _ in range(8)] for _ in range(8)]
    for (f, r), code in positions.items():
        b[r][f] = code
    return Board.from_matrix(b)


def test_out_of_bounds_and_no_piece_and_wrong_color_and_ally_occupied():
    b = empty_board()
    # out of bounds
    legal, reason, _ = is_legal_move(b, Move(-1, 0, 0, 0), "white", "-", None)
    assert not legal and reason == "out_of_bounds"

    # no piece
    legal, reason, _ = is_legal_move(b, Move(0, 0, 1, 1), "white", "-", None)
    assert not legal and reason == "no_piece"

    # wrong color
    b = board_from_positions({(0, 0): "p"})
    legal, reason, _ = is_legal_move(b, Move(0, 0, 0, 1), "white", "-", None)
    assert not legal and reason == "wrong_color"

    # occupied by ally
    b = board_from_positions({(0, 0): "P", (0, 1): "N"})
    legal, reason, _ = is_legal_move(b, Move(0, 0, 0, 1), "white", "-", None)
    assert not legal and reason == "occupied_by_ally"


def test_knight_normal_move():
    b = board_from_positions({(1, 1): "N", (4, 7): "K", (0, 0): "k"})
    legal, reason, _ = is_legal_move(b, Move(1, 1, 2, 3), "white", "-", None)
    assert legal and reason == "ok"


def test_is_in_check_and_self_check_prevention():
    # white king on file 4 rank 4, black rook on same file
    b = board_from_positions({(4, 4): "K", (4, 0): "r"})
    assert is_in_check(b, "white")

    # pinned rook: moving rook exposes king to check
    b = board_from_positions({(4, 7): "K", (4, 6): "R", (4, 0): "r"})
    # attempt to move white rook off file
    legal, reason, _ = is_legal_move(b, Move(4, 6, 5, 6), "white", "-", None)
    assert not legal and reason == "king_in_check"


def test_castling_success_and_blocked():
    # white castle kingside
    b = board_from_positions({(4, 7): "K", (7, 7): "R"})
    legal, reason, special = is_legal_move(b, Move(4, 7, 6, 7), "white", "KQ", None)
    assert legal and reason == "ok" and special.get("is_castle")

    # blocked castle
    b = board_from_positions({(4, 7): "K", (7, 7): "R", (5, 7): "N"})
    legal, reason, _ = is_legal_move(b, Move(4, 7, 6, 7), "white", "KQ", None)
    assert not legal and reason == "castle_blocked"


def test_en_passant_capture():
    # white pawn at (4,3) can capture en passant at (3,2) capturing black pawn at (3,3)
    b = board_from_positions({(4, 3): "P", (3, 3): "p", (4, 7): "K", (0, 0): "k"})
    move = Move(4, 3, 3, 2)
    legal, reason, special = is_legal_move(b, move, "white", "-", (3, 2))
    assert legal and special.get("is_en_passant")
    ok, result = apply_move(b, move, "white", "-", (3, 2), halfmove=0, fullmove=1)
    assert ok and result["legal"]
    # captured pawn removed
    assert b.piece_at(3, 3) is None


def test_promotion_auto_queen_and_halfmove_fullmove():
    # white pawn promotes moving to rank 0
    b = board_from_positions({(0, 1): "P", (4, 7): "K", (7, 0): "k"})
    move = Move(0, 1, 0, 0)
    ok, result = apply_move(b, move, "white", "-", None, halfmove=5, fullmove=10)
    assert ok and result["legal"]
    assert result["promotion"] == "Q"
    assert result["halfmove"] == 0


def test_update_castling_rights_on_king_and_rook_and_capture():
    # moving white king clears KQ
    class Dummy:
        def __init__(self, kind, color):
            self.kind = kind
            self.color = color

    rights = update_castling_rights("KQkq", Move(4, 7, 5, 7), moving_piece=Dummy("K", "white"), captured_piece=None)
    assert rights == "kq"

    # moving white rook from h1 clears K
    rights = update_castling_rights("KQ", Move(7, 7, 7, 6), moving_piece=Dummy("R", "white"), captured_piece=None)
    assert rights == "Q"


def test_bishop_rook_queen_king_moves():
    b = board_from_positions({(2, 2): "B", (0, 0): "k", (4, 7): "K"})
    legal, reason, _ = is_legal_move(b, Move(2, 2, 5, 5), "white", "-", None)
    assert legal and reason == "ok"

    b = board_from_positions({(0, 0): "r", (4, 7): "K", (7, 7): "k"})
    legal, reason, _ = is_legal_move(b, Move(0, 0, 0, 5), "black", "-", None)
    assert legal and reason == "ok"

    b = board_from_positions({(3, 3): "q", (4, 7): "K", (7, 7): "k"})
    legal, reason, _ = is_legal_move(b, Move(3, 3, 6, 6), "black", "-", None)
    assert legal and reason == "ok"

    b = board_from_positions({(4, 7): "K", (4, 6): None, (0, 0): "k"})
    legal, reason, _ = is_legal_move(b, Move(4, 7, 4, 6), "white", "-", None)
    assert legal and reason == "ok"


def test_en_passant_creation_and_fullmove_halfmove():
    # white pawn double-step creates en-passant and resets halfmove
    b = board_from_positions({(4, 6): "P", (4, 7): "K", (0, 0): "k"})
    move = Move(4, 6, 4, 4)
    ok, result = apply_move(b, move, "white", "-", None, halfmove=3, fullmove=10)
    assert ok and result["legal"]
    assert result["en_passant"] == (4, 5)
    # fullmove should remain same after white move
    assert result["fullmove"] == 10

    # black move should increment fullmove
    b2 = board_from_positions({(4, 1): "p", (4, 0): "k", (0, 7): "K"})
    move2 = Move(4, 1, 4, 2)
    ok2, result2 = apply_move(b2, move2, "black", "-", None, halfmove=0, fullmove=5)
    assert ok2 and result2["legal"]
    assert result2["fullmove"] == 6


def test_castle_missing_rights_and_rook_missing_and_through_check_and_queenside():
    # missing rights
    b = board_from_positions({(4, 7): "K", (7, 7): "R"})
    legal, reason, _ = is_legal_move(b, Move(4, 7, 6, 7), "white", "-", None)
    assert not legal and reason == "castle_rights"

    # rook missing
    b = board_from_positions({(4, 7): "K"})
    legal, reason, _ = is_legal_move(b, Move(4, 7, 6, 7), "white", "KQ", None)
    assert not legal and reason == "rook_missing"

    # through-check: black attacks f1 (5,7) so can't castle through
    b = board_from_positions({(4, 7): "K", (7, 7): "R", (5, 5): "r", (0, 0): "k"})
    legal, reason, _ = is_legal_move(b, Move(4, 7, 6, 7), "white", "KQ", None)
    assert not legal and reason == "castle_through_check"

    # queenside success
    b = board_from_positions({(4, 7): "K", (0, 7): "R"})
    legal, reason, special = is_legal_move(b, Move(4, 7, 2, 7), "white", "KQ", None)
    assert legal and special.get("is_castle")


def test_castling_rights_cleared_when_rook_captured():
    # black captures white rook on h1 clears K
    moving_piece = type("P", (), {"kind": "R", "color": "black"})()
    captured = type("P", (), {"kind": "R", "color": "white"})()
    rights = update_castling_rights("KQ", Move(7, 0, 7, 7), moving_piece=moving_piece, captured_piece=captured)
    # capturing white rook on h1 should remove K
    assert rights == "Q" or rights == "-"


def test_move_to_lan_with_promotion():
    lan = notation.move_to_lan(0, 1, 0, 0, promotion="Q")
    assert lan == "a7a8=Q"


def test_is_square_attacked_rook_line():
    b = board_from_positions({(4, 0): "k", (4, 7): "K", (4, 3): "r"})
    assert is_square_attacked(b, 4, 7, "black")


def test_has_any_legal_move_false_for_checkmate():
    b = board_from_positions({(0, 0): "k", (2, 2): "K", (1, 1): "Q"})
    assert has_any_legal_move(b, "black", "-", None) is False


def test_pseudo_legal_pawn_blocked_and_diagonal_capture():
    b = board_from_positions({(4, 6): "P", (4, 5): "P", (5, 5): "p"})
    pawn = b.piece_at(4, 6)
    moves = pseudo_legal_moves_for_piece(b, 4, 6, pawn)
    assert not any(m.to_file == 4 and m.to_rank == 5 for m in moves)
    assert not any(m.to_file == 4 and m.to_rank == 4 for m in moves)
    assert any(m.to_file == 5 and m.to_rank == 5 for m in moves)


def test_pseudo_legal_pawn_en_passant_target():
    b = board_from_positions({(4, 3): "P", (3, 3): "p"})
    pawn = b.piece_at(4, 3)
    moves = pseudo_legal_moves_for_piece(b, 4, 3, pawn, en_passant=(3, 2))
    assert any(m.to_file == 3 and m.to_rank == 2 for m in moves)


def test_pseudo_legal_rook_blocked_by_ally():
    b = board_from_positions({(0, 0): "R", (0, 1): "P", (0, 2): "p"})
    rook = b.piece_at(0, 0)
    moves = pseudo_legal_moves_for_piece(b, 0, 0, rook)
    assert not any(m.to_file == 0 and m.to_rank == 1 for m in moves)
    assert not any(m.to_file == 0 and m.to_rank == 2 for m in moves)


def test_has_any_legal_move_true():
    b = board_from_positions({(4, 7): "K", (0, 0): "k"})
    assert has_any_legal_move(b, "white", "-", None) is True
