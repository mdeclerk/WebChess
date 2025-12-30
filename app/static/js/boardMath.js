import { boardPadding, boardPixelSize, squareSize } from "./context.js";

const squareFromPoint = (x, y) => {
  const localX = x - boardPadding;
  const localY = y - boardPadding;
  if (localX < 0 || localY < 0 || localX >= boardPixelSize || localY >= boardPixelSize) {
    return null;
  }
  return {
    file: Math.max(0, Math.min(7, Math.floor(localX / squareSize))),
    rank: Math.max(0, Math.min(7, Math.floor(localY / squareSize))),
  };
};

const centerForSquare = (file, rank) => ({
  cx: boardPadding + file * squareSize + squareSize / 2,
  cy: boardPadding + rank * squareSize + squareSize / 2,
});

export { squareFromPoint, centerForSquare };
