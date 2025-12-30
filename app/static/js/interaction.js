import { canvas, boardPadding, squareSize } from "./context.js";
import { squareFromPoint, centerForSquare } from "./boardMath.js";
import { validateMove } from "./api.js";
import {
  state,
  gameState,
  toggleTurn,
  clearDragHint,
  pieceAt,
  pickPieceAt,
  removePieceAt,
  appendMove,
  updateFenOutput,
  setGameOver,
  pushUndoState,
} from "./state.js";

const updateHover = (x, y) => {
  const square = squareFromPoint(x, y);
  if (!square) {
    state.hover = null;
    return;
  }
  state.hover = square;
};

const updateDragPosition = (x, y) => {
  if (!state.dragging) return;
  const offsetX = state.dragging.dragOffsetX ?? 0;
  const offsetY = state.dragging.dragOffsetY ?? 0;
  state.dragging.x = (x - offsetX - boardPadding - squareSize / 2) / squareSize;
  state.dragging.y = (y - offsetY - boardPadding - squareSize / 2) / squareSize;
};

const snapPiece = (piece, file, rank) => {
  piece.targetX = file;
  piece.targetY = rank;
  piece.anim = {
    fromX: piece.x,
    fromY: piece.y,
    toX: file,
    toY: rank,
    elapsed: 0,
    duration: 180,
  };
};

const applyValidatedMove = (piece, originFile, originRank, targetFile, targetRank, result) => {
  if (!piece) {
    return false;
  }
  if (!result.legal) {
    snapPiece(piece, originFile, originRank);
    return false;
  }
  pushUndoState();
  if (result.capture) {
    removePieceAt(result.capture.file, result.capture.rank);
  }
  if (result.castle) {
    const rook = pieceAt(result.castle.rook_from.file, result.castle.rook_from.rank);
    if (rook) {
      snapPiece(rook, result.castle.rook_to.file, result.castle.rook_to.rank);
    }
  }
  if (result.promotion) {
    piece.type = result.promotion;
  }
  snapPiece(piece, targetFile, targetRank);
  toggleTurn();
  if (result.notation) {
    appendMove(result.notation, { capture: Boolean(result.capture), check: Boolean(result.check) });
  }
  if (result.castling) {
    gameState.castling = result.castling;
  }
  if (result.en_passant) {
    gameState.enPassant = { file: result.en_passant.file, rank: result.en_passant.rank };
  } else {
    gameState.enPassant = null;
  }
  if (typeof result.halfmove === "number") {
    gameState.halfmove = result.halfmove;
  }
  if (typeof result.fullmove === "number") {
    gameState.fullmove = result.fullmove;
  }
  if (result.fen) {
    updateFenOutput(result.fen);
  }
  if (result.game_over) {
    setGameOver({ outcome: result.outcome, winner: result.winner });
  }
  state.lastMove = {
    from: { file: originFile, rank: originRank },
    to: { file: targetFile, rank: targetRank },
  };
  document.dispatchEvent(
    new CustomEvent("chess:move-applied", {
      detail: {
        from: { file: originFile, rank: originRank },
        to: { file: targetFile, rank: targetRank },
        result,
      },
    })
  );
  return true;
};

const scheduleDragValidation = (square, piece) => {
  if (!square || !piece) {
    clearDragHint();
    return;
  }
  const originFile = Math.round(piece.dragOriginX);
  const originRank = Math.round(piece.dragOriginY);
  if (originFile === square.file && originRank === square.rank) {
    state.dragHint = { file: square.file, rank: square.rank, legal: true };
    return;
  }
  const prev = state.dragHint;
  if (prev && prev.file === square.file && prev.rank === square.rank) {
    return;
  }
  state.dragHint = { file: square.file, rank: square.rank, legal: null };
  if (state.dragHintTimer) {
    clearTimeout(state.dragHintTimer);
  }
  state.dragHintTimer = setTimeout(async () => {
    try {
      const result = await validateMove(originFile, originRank, square.file, square.rank);
      state.dragHint = { file: square.file, rank: square.rank, legal: result.legal };
    } catch (error) {
      state.dragHint = { file: square.file, rank: square.rank, legal: false };
    }
  }, 120);
};

const handlePointerDown = (event) => {
  if (gameState.gameOver) return;
  if (state.validating) return;
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  const square = squareFromPoint(x, y);
  if (!square) return;
  const piece = pickPieceAt(square.file, square.rank);
  if (!piece) return;
  if (piece.color.toLowerCase() !== state.turn.toLowerCase()) return;
  state.dragging = piece;
  state.dragging.dragOriginX = piece.targetX;
  state.dragging.dragOriginY = piece.targetY;
  state.dragHint = { file: square.file, rank: square.rank, legal: true };
  const center = centerForSquare(piece.x, piece.y);
  state.dragging.dragOffsetX = x - center.cx;
  state.dragging.dragOffsetY = y - center.cy;
};

const handlePointerMove = (event) => {
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  updateHover(x, y);
  if (state.dragging) {
    updateDragPosition(x, y);
    const square = squareFromPoint(x, y);
    scheduleDragValidation(square, state.dragging);
  }
};

const handlePointerUp = async (event) => {
  if (gameState.gameOver) return;
  if (!state.dragging) return;
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  const square = squareFromPoint(x, y);
  const piece = state.dragging;
  const originFile = Math.round(piece.dragOriginX);
  const originRank = Math.round(piece.dragOriginY);
  const targetFile = square ? square.file : originFile;
  const targetRank = square ? square.rank : originRank;
  const isSameSquare = originFile === targetFile && originRank === targetRank;
  state.validating = true;
  if (isSameSquare) {
    snapPiece(piece, originFile, originRank);
    state.validating = false;
  } else {
    try {
      const result = await validateMove(originFile, originRank, targetFile, targetRank);
      applyValidatedMove(piece, originFile, originRank, targetFile, targetRank, result);
    } catch (error) {
      snapPiece(piece, originFile, originRank);
    } finally {
      state.validating = false;
    }
  }
  state.dragging.dragOffsetX = null;
  state.dragging.dragOffsetY = null;
  state.dragging = null;
  clearDragHint();
};

const bindInputHandlers = () => {
  canvas.addEventListener("pointerdown", handlePointerDown);
  canvas.addEventListener("pointermove", handlePointerMove);
  canvas.addEventListener("pointerup", handlePointerUp);
  canvas.addEventListener("pointerleave", () => {
    state.hover = null;
  });
};

export { applyValidatedMove, bindInputHandlers };
