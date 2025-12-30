from dataclasses import dataclass


@dataclass(frozen=True)
class Move:
    """Represents a move using 0-based from/to coordinates.

    Keeps move data lightweight and engine-friendly.

    Args:
        from_file: Source file (0=a, 7=h).
        from_rank: Source rank (0=8th rank, 7=1st rank).
        to_file: Destination file (0=a, 7=h).
        to_rank: Destination rank (0=8th rank, 7=1st rank).
    """

    from_file: int
    from_rank: int
    to_file: int
    to_rank: int
