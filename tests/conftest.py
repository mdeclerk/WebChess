import os
import random

from app.chess.base.board import Board


def pytest_configure(config):
    # ensure markers are available in pytest UI
    config.addinivalue_line("markers", "slow: mark slow tests")
    config.addinivalue_line("markers", "api: mark api tests")


def initial_board_matrix():
    """Return the starting position board matrix."""
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
    """Create a Board from a dict of {(file, rank): piece_code}."""
    b = [[None for _ in range(8)] for _ in range(8)]
    for (f, r), code in positions.items():
        b[r][f] = code
    return Board.from_matrix(b)


def seed_all(seed: int) -> None:
    random.seed(seed)
    try:
        import numpy as _np  # pylint: disable=import-error

        _np.random.seed(seed)
    except Exception:
        pass
    os.environ["PYTHONHASHSEED"] = str(seed)


def pytest_sessionstart(session):
    # deterministic seeding for any randomized tests; overridable with env var
    seed = int(os.environ.get("PYTEST_DETERMINISTIC_SEED", "0"))
    seed_all(seed)
