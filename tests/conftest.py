import os
import random


def pytest_configure(config):
    # ensure markers are available in pytest UI
    config.addinivalue_line("markers", "slow: mark slow tests")
    config.addinivalue_line("markers", "api: mark api tests")


def seed_all(seed: int) -> None:
    random.seed(seed)
    try:
        import numpy as _np

        _np.random.seed(seed)
    except Exception:
        pass
    os.environ["PYTHONHASHSEED"] = str(seed)


def pytest_sessionstart(session):
    # deterministic seeding for any randomized tests; overridable with env var
    seed = int(os.environ.get("PYTEST_DETERMINISTIC_SEED", "0"))
    seed_all(seed)
