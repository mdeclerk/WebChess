const canvas = document.getElementById("chess-board");
const ctx = canvas.getContext("2d");
const boardFrame = document.getElementById("board-frame");
const winProbabilityBar = document.getElementById("win-probability-bar");
const winProbabilityWhite = document.getElementById("win-probability-white");
const winProbabilityBlack = document.getElementById("win-probability-black");
const moveList = document.getElementById("move-list");
const gameOverlay = document.getElementById("game-overlay");
const gameMessage = document.getElementById("game-message");
const restartButton = document.getElementById("restart-game");
const newGameButton = document.getElementById("new-game");
const undoButton = document.getElementById("undo-move");
const fenValue = document.getElementById("fen-value");
const fenCopyButton = document.getElementById("fen-copy");
const fenCopyFeedback = document.getElementById("fen-copy-feedback");
const engineDepthInput = document.getElementById("engine-depth");
const engineDepthValue = document.getElementById("engine-depth-value");
const engineThinking = document.getElementById("engine-thinking");
const boardSize = 8;
const boardPadding = 28;
const boardPixelSize = canvas.width - boardPadding * 2;
const squareSize = boardPixelSize / boardSize;

export {
  canvas,
  ctx,
  boardFrame,
  winProbabilityBar,
  winProbabilityWhite,
  winProbabilityBlack,
  moveList,
  gameOverlay,
  gameMessage,
  restartButton,
  newGameButton,
  undoButton,
  fenValue,
  fenCopyButton,
  fenCopyFeedback,
  engineDepthInput,
  engineDepthValue,
  engineThinking,
  boardSize,
  boardPadding,
  boardPixelSize,
  squareSize,
};
