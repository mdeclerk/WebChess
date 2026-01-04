from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Piece:
    """Represents a chess piece using a single-letter code.

    Keeps color and kind derivations consistent across the engine.

    Args:
        code: Piece code, uppercase for white and lowercase for black (e.g., "P", "k").
    """

    code: str

    @property
    def color(self) -> str:
        """Returns the piece color derived from the code casing.

        Centralizes the uppercase/white vs lowercase/black rule.
        """
        return "white" if self.code.isupper() else "black"

    @property
    def kind(self) -> str:
        """Returns the normalized piece kind (always uppercase).

        Normalizes piece comparisons regardless of color.
        """
        return self.code.upper()


class Board:
    def __init__(self, grid: List[List[Optional[Piece]]]):
        """Creates a board from an 8x8 grid of Piece objects or None.

        Keeps board indexing stable for rules, search, and API payloads.

        Args:
            grid: Board matrix indexed as [rank][file] with rank 0 at the top.
        """
        self.grid = grid

    @classmethod
    def from_matrix(cls, matrix: List[List[Optional[str]]]) -> "Board":
        """Builds a Board from a matrix of piece codes.

        Converts API payloads into domain objects.

        Args:
            matrix: 8x8 array of piece codes (e.g., "P") or None.

        Returns:
            A Board instance with Piece objects.
        """
        grid: List[List[Optional[Piece]]] = []
        for rank in matrix:
            row: List[Optional[Piece]] = []
            for cell in rank:
                if cell is None:
                    row.append(None)
                else:
                    row.append(Piece(cell))
            grid.append(row)
        return cls(grid)

    def to_matrix(self) -> List[List[Optional[str]]]:
        """Serializes the board into a matrix of piece codes.

        Emits a transport-friendly view of the board.

        Returns:
            8x8 array of piece codes or None, suitable for API payloads.
        """
        matrix: List[List[Optional[str]]] = []
        for rank in self.grid:
            row: List[Optional[str]] = []
            for cell in rank:
                row.append(cell.code if cell else None)
            matrix.append(row)
        return matrix

    def piece_at(self, file: int, rank: int) -> Optional[Piece]:
        """Returns the piece at a square, or None if empty.

        Provides a single access point for board lookups.

        Args:
            file: File index (0=a, 7=h).
            rank: Rank index (0=8th rank, 7=1st rank).

        Returns:
            Piece at the square, or None.
        """
        return self.grid[rank][file]

    def set_piece(self, file: int, rank: int, piece: Optional[Piece]) -> None:
        """Places a piece on a square, replacing any existing piece.

        Mutates board state in a predictable, local way.

        Args:
            file: File index (0=a, 7=h).
            rank: Rank index (0=8th rank, 7=1st rank).
            piece: Piece to place, or None to clear the square.
        """
        self.grid[rank][file] = piece

    def clone(self) -> "Board":
        """Returns a shallow copy of the board grid for safe simulation.

        Allows search/rules to simulate moves without touching the original board.

        Returns:
            New Board with copied grid references.
        """
        copied = [list(row) for row in self.grid]
        return Board(copied)
