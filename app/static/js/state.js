import { moveList, fenValue, gameOverlay, gameMessage } from "./context.js";

const state = {
  pieces: [],
  dragging: null,
  hover: null,
  turn: "White",
  validating: false,
  dragHint: null,
  dragHintTimer: null,
  lastMove: null,
  engineThinking: false,
  engineRequestId: 0,
  engineDepth: 2,
  winProbability: {
    white: 0.5,
    black: 0.5,
    hasValue: false,
  },
};

const gameState = {
  castling: "KQkq",
  enPassant: null,
  halfmove: 0,
  fullmove: 1,
  moveHistory: [],
  fen: "",
  undoStack: [],
  gameOver: false,
  outcome: null,
  winner: null,
};

const pieceTemplates = [
  { type: "R", color: "black", x: 0, y: 0 },
  { type: "N", color: "black", x: 1, y: 0 },
  { type: "B", color: "black", x: 2, y: 0 },
  { type: "Q", color: "black", x: 3, y: 0 },
  { type: "K", color: "black", x: 4, y: 0 },
  { type: "B", color: "black", x: 5, y: 0 },
  { type: "N", color: "black", x: 6, y: 0 },
  { type: "R", color: "black", x: 7, y: 0 },
  { type: "P", color: "black", x: 0, y: 1 },
  { type: "P", color: "black", x: 1, y: 1 },
  { type: "P", color: "black", x: 2, y: 1 },
  { type: "P", color: "black", x: 3, y: 1 },
  { type: "P", color: "black", x: 4, y: 1 },
  { type: "P", color: "black", x: 5, y: 1 },
  { type: "P", color: "black", x: 6, y: 1 },
  { type: "P", color: "black", x: 7, y: 1 },
  { type: "P", color: "white", x: 0, y: 6 },
  { type: "P", color: "white", x: 1, y: 6 },
  { type: "P", color: "white", x: 2, y: 6 },
  { type: "P", color: "white", x: 3, y: 6 },
  { type: "P", color: "white", x: 4, y: 6 },
  { type: "P", color: "white", x: 5, y: 6 },
  { type: "P", color: "white", x: 6, y: 6 },
  { type: "P", color: "white", x: 7, y: 6 },
  { type: "R", color: "white", x: 0, y: 7 },
  { type: "N", color: "white", x: 1, y: 7 },
  { type: "B", color: "white", x: 2, y: 7 },
  { type: "Q", color: "white", x: 3, y: 7 },
  { type: "K", color: "white", x: 4, y: 7 },
  { type: "B", color: "white", x: 5, y: 7 },
  { type: "N", color: "white", x: 6, y: 7 },
  { type: "R", color: "white", x: 7, y: 7 },
];

const createPieces = () =>
  pieceTemplates.map((piece, idx) => ({
    id: idx + 1,
    type: piece.type,
    color: piece.color,
    x: piece.x,
    y: piece.y,
    targetX: piece.x,
    targetY: piece.y,
    anim: null,
    dragOriginX: piece.x,
    dragOriginY: piece.y,
  }));

const setTurn = (turn) => {
  state.turn = turn;
};

const toggleTurn = () => setTurn(state.turn === "White" ? "Black" : "White");

const clearDragHint = () => {
  state.dragHint = null;
  if (state.dragHintTimer) {
    clearTimeout(state.dragHintTimer);
    state.dragHintTimer = null;
  }
};

const pieceAt = (file, rank) =>
  state.pieces.find(
    (piece) => Math.round(piece.targetX) === file && Math.round(piece.targetY) === rank
  );

const pickPieceAt = (file, rank) =>
  state.pieces.find((piece) => Math.round(piece.x) === file && Math.round(piece.y) === rank);

const removePieceAt = (file, rank) => {
  const index = state.pieces.findIndex(
    (piece) => Math.round(piece.targetX) === file && Math.round(piece.targetY) === rank
  );
  if (index >= 0) {
    state.pieces.splice(index, 1);
  }
};

const pieceCode = (piece) => (piece.color === "white" ? piece.type : piece.type.toLowerCase());

const boardMatrixFromPieces = () => {
  const matrix = Array.from({ length: 8 }, () => Array.from({ length: 8 }, () => null));
  state.pieces.forEach((piece) => {
    const file = Math.round(piece.targetX);
    const rank = Math.round(piece.targetY);
    if (file < 0 || file > 7 || rank < 0 || rank > 7) return;
    matrix[rank][file] = pieceCode(piece);
  });
  return matrix;
};

const appendMoveEntry = (entryData, ply) => {
  if (!moveList) return;
  const moveNumber = Math.ceil(ply / 2);
  const prefix = ply % 2 === 1 ? `${moveNumber}. ` : `${moveNumber}... `;
  const entry = document.createElement("li");
  entry.className = "flex flex-wrap items-center gap-2";
  const text = document.createElement("span");
  text.className = "font-mono text-[#3f2b1d]";
  text.textContent = `${prefix}${entryData.notation}`;
  entry.appendChild(text);
  if (entryData.capture) {
    const badge = document.createElement("span");
    badge.className =
      "rounded-full bg-[#f2d6b6] px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-[#5b2f12]";
    badge.textContent = "Capture";
    entry.appendChild(badge);
  }
  if (entryData.outcome === "checkmate") {
    const badge = document.createElement("span");
    badge.className =
      "rounded-full bg-[#d64545] px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-[#f6ead9]";
    badge.textContent = "Checkmate";
    entry.appendChild(badge);
  } else if (entryData.outcome === "stalemate") {
    const badge = document.createElement("span");
    badge.className =
      "rounded-full bg-[#8b5a35] px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-[#f6ead9]";
    badge.textContent = "Stalemate";
    entry.appendChild(badge);
  } else if (entryData.check) {
    const badge = document.createElement("span");
    badge.className =
      "rounded-full bg-[#f5e1c6] px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-[#7b3c1c]";
    badge.textContent = "Check";
    entry.appendChild(badge);
  }
  moveList.appendChild(entry);
  moveList.scrollTop = moveList.scrollHeight;
};

const appendMove = (notation, meta = {}) => {
  const entryData = {
    notation,
    capture: Boolean(meta.capture),
    check: Boolean(meta.check),
    outcome: meta.outcome,
  };
  gameState.moveHistory.push(entryData);
  appendMoveEntry(entryData, gameState.moveHistory.length);
};

const renderMoveList = () => {
  if (!moveList) return;
  moveList.innerHTML = "";
  gameState.moveHistory.forEach((entryData, index) => {
    appendMoveEntry(entryData, index + 1);
  });
};

const updateFenOutput = (fen) => {
  gameState.fen = fen;
  if (fenValue) {
    fenValue.textContent = fen || "";
  }
};

const setGameOver = ({ outcome, winner }) => {
  gameState.gameOver = true;
  gameState.outcome = outcome;
  gameState.winner = winner;
  if (gameOverlay) {
    gameOverlay.classList.add("is-visible");
    gameOverlay.setAttribute("aria-hidden", "false");
  }
  if (gameMessage) {
    if (outcome === "stalemate") {
      gameMessage.textContent = "Stalemate";
    } else if (winner) {
      const label = winner === "white" ? "White" : "Black";
      gameMessage.textContent = `${label} wins by checkmate`;
    } else {
      gameMessage.textContent = "Game over";
    }
  }
};

const clearGameOver = () => {
  gameState.gameOver = false;
  gameState.outcome = null;
  gameState.winner = null;
  if (gameOverlay) {
    gameOverlay.classList.remove("is-visible");
    gameOverlay.setAttribute("aria-hidden", "true");
  }
  if (gameMessage) {
    gameMessage.textContent = "";
  }
};

const snapshotState = () => ({
  pieces: state.pieces.map((piece) => ({
    id: piece.id,
    type: piece.type,
    color: piece.color,
    x: piece.x,
    y: piece.y,
    targetX: piece.targetX,
    targetY: piece.targetY,
  })),
  turn: state.turn,
  lastMove: state.lastMove ? { ...state.lastMove } : null,
  gameState: {
    castling: gameState.castling,
    enPassant: gameState.enPassant ? { ...gameState.enPassant } : null,
    halfmove: gameState.halfmove,
    fullmove: gameState.fullmove,
    moveHistory: gameState.moveHistory.map((entry) => ({ ...entry })),
    fen: gameState.fen,
    gameOver: gameState.gameOver,
    outcome: gameState.outcome,
    winner: gameState.winner,
  },
});

const pushUndoState = () => {
  gameState.undoStack.push(snapshotState());
};

const restoreSnapshot = (snapshot) => {
  state.pieces = snapshot.pieces.map((piece) => ({
    ...piece,
    x: piece.targetX,
    y: piece.targetY,
    anim: null,
    dragOriginX: piece.targetX,
    dragOriginY: piece.targetY,
  }));
  state.dragging = null;
  state.hover = null;
  state.dragHint = null;
  state.dragHintTimer = null;
  state.turn = snapshot.turn;
  state.lastMove = snapshot.lastMove ? { ...snapshot.lastMove } : null;
  gameState.castling = snapshot.gameState.castling;
  gameState.enPassant = snapshot.gameState.enPassant ? { ...snapshot.gameState.enPassant } : null;
  gameState.halfmove = snapshot.gameState.halfmove;
  gameState.fullmove = snapshot.gameState.fullmove;
  gameState.moveHistory = snapshot.gameState.moveHistory.map((entry) => ({ ...entry }));
  gameState.fen = snapshot.gameState.fen;
  renderMoveList();
  updateFenOutput(snapshot.gameState.fen);
  if (snapshot.gameState.gameOver) {
    setGameOver({ outcome: snapshot.gameState.outcome, winner: snapshot.gameState.winner });
  } else {
    clearGameOver();
  }
};

const undoLastMove = () => {
  if (!gameState.undoStack.length) {
    return false;
  }
  const snapshot = gameState.undoStack.pop();
  if (!snapshot) {
    return false;
  }
  restoreSnapshot(snapshot);
  return true;
};

const undoPlayerTurn = () => {
  if (!gameState.undoStack.length) {
    return false;
  }
  const wasWhiteTurn = state.turn === "White";
  let undone = undoLastMove();
  if (wasWhiteTurn && gameState.undoStack.length) {
    undone = undoLastMove() || undone;
  }
  return undone;
};

export {
  state,
  gameState,
  createPieces,
  setTurn,
  toggleTurn,
  clearDragHint,
  pieceAt,
  pickPieceAt,
  removePieceAt,
  pieceCode,
  boardMatrixFromPieces,
  appendMove,
  renderMoveList,
  updateFenOutput,
  setGameOver,
  clearGameOver,
  pushUndoState,
  undoLastMove,
  undoPlayerTurn,
};
