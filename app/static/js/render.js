import { ctx, boardPadding, boardPixelSize, boardSize, squareSize } from "./context.js";
import { centerForSquare } from "./boardMath.js";
import { state, pieceAt } from "./state.js";

const colors = {
  dark: "#6b3f22",
  light: "#d2a679",
  glow: "rgba(212, 177, 106, 0.5)",
  shadow: "rgba(0, 0, 0, 0.25)",
  legal: "rgba(80, 170, 110, 0.8)",
  illegal: "rgba(190, 80, 80, 0.85)",
  lastMove: "rgba(235, 206, 141, 0.55)",
  lastMoveEdge: "rgba(120, 70, 35, 0.6)",
};

const spritePaths = {
  white: {
    K: "/assets/white_king.svg",
    Q: "/assets/white_queen.svg",
    R: "/assets/white_rook.svg",
    B: "/assets/white_bishop.svg",
    N: "/assets/white_knight.svg",
    P: "/assets/white_pawn.svg",
  },
  black: {
    K: "/assets/black_king.svg",
    Q: "/assets/black_queen.svg",
    R: "/assets/black_rook.svg",
    B: "/assets/black_bishop.svg",
    N: "/assets/black_knight.svg",
    P: "/assets/black_pawn.svg",
  },
};

const sprites = { white: {}, black: {} };
let spritesReady = false;

const drawBoard = () => {
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  for (let rank = 0; rank < boardSize; rank += 1) {
    for (let file = 0; file < boardSize; file += 1) {
      const isDark = (rank + file) % 2 === 1;
      ctx.fillStyle = isDark ? colors.dark : colors.light;
      ctx.fillRect(
        boardPadding + file * squareSize,
        boardPadding + rank * squareSize,
        squareSize,
        squareSize
      );
    }
  }
  ctx.fillStyle = "rgba(255, 255, 255, 0.08)";
  ctx.fillRect(boardPadding, boardPadding, boardPixelSize, boardPixelSize);
  drawLabels();
};

const drawLabels = () => {
  ctx.save();
  ctx.font = `${squareSize * 0.18}px "Georgia", serif`;
  ctx.fillStyle = "rgba(245, 232, 210, 0.9)";
  ctx.shadowColor = "rgba(40, 24, 12, 0.55)";
  ctx.shadowBlur = 4;
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  for (let file = 0; file < boardSize; file += 1) {
    const label = String.fromCharCode(97 + file);
    ctx.fillText(
      label,
      boardPadding + file * squareSize + squareSize / 2,
      boardPadding + boardPixelSize + 6
    );
  }
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  for (let rank = 0; rank < boardSize; rank += 1) {
    const label = `${8 - rank}`;
    ctx.fillText(
      label,
      boardPadding - 14,
      boardPadding + rank * squareSize + squareSize / 2
    );
  }
  ctx.restore();
};

const drawFallbackPiece = (piece, isDragging) => {
  const { cx, cy } = centerForSquare(piece.x, piece.y);
  const radius = squareSize * 0.32;
  const lift = isDragging ? 1.08 : 1;
  const offsetY = isDragging ? -squareSize * 0.08 : 0;
  ctx.save();
  ctx.translate(cx, cy + offsetY);
  ctx.scale(lift, lift);
  ctx.shadowColor = colors.shadow;
  ctx.shadowBlur = isDragging ? 18 : 10;
  ctx.shadowOffsetY = isDragging ? 8 : 4;
  ctx.fillStyle = piece.color === "white" ? "#e6d1b6" : "#4a2b1a";
  ctx.beginPath();
  ctx.arc(0, 0, radius, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = piece.color === "white" ? "#b67b52" : "#d7b48a";
  ctx.font = `${squareSize * 0.32}px "Georgia", serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(piece.type, 0, 2);
  ctx.restore();
};

const drawSpritePiece = (piece, isDragging) => {
  const sprite = spritesReady ? sprites[piece.color]?.[piece.type] : null;
  if (!sprite || !sprite.complete) {
    drawFallbackPiece(piece, isDragging);
    return;
  }
  const { cx, cy } = centerForSquare(piece.x, piece.y);
  const lift = isDragging ? 1.08 : 1;
  const offsetY = isDragging ? -squareSize * 0.08 : 0;
  const size = squareSize * 0.94;
  ctx.save();
  ctx.translate(cx, cy + offsetY);
  ctx.scale(lift, lift);
  ctx.shadowColor = colors.shadow;
  ctx.shadowBlur = isDragging ? 18 : 12;
  ctx.shadowOffsetY = isDragging ? 8 : 5;
  ctx.drawImage(sprite, -size / 2, -size / 2, size, size);
  ctx.restore();
};

const loadSprites = () => {
  const tasks = [];
  ["white", "black"].forEach((color) => {
    Object.entries(spritePaths[color]).forEach(([type, src]) => {
      const img = new Image();
      sprites[color][type] = img;
      tasks.push(
        new Promise((resolve) => {
          img.onload = () => resolve();
          img.onerror = () => resolve();
          img.src = src;
        })
      );
    });
  });
  return Promise.all(tasks).then(() => {
    spritesReady = true;
  });
};

const drawHover = () => {
  if (!state.hover) return;
  if (!state.dragging) {
    const piece = pieceAt(state.hover.file, state.hover.rank);
    if (!piece || piece.color.toLowerCase() !== state.turn.toLowerCase()) {
      return;
    }
  }
  const isDark = (state.hover.rank + state.hover.file) % 2 === 1;
  const isDragging = Boolean(state.dragging);
  const isHintSquare =
    state.dragHint &&
    state.dragHint.file === state.hover.file &&
    state.dragHint.rank === state.hover.rank;
  const hintColor =
    isDragging && isHintSquare && state.dragHint.legal !== null
      ? state.dragHint.legal
        ? colors.legal
        : colors.illegal
      : null;
  ctx.save();
  ctx.strokeStyle = hintColor || (isDark ? colors.glow : "rgba(88, 53, 28, 0.8)");
  ctx.lineWidth = hintColor ? 5 : isDark ? 4 : 5;
  ctx.strokeRect(
    boardPadding + state.hover.file * squareSize + 2,
    boardPadding + state.hover.rank * squareSize + 2,
    squareSize - 4,
    squareSize - 4
  );
  if (!isDark && !hintColor) {
    ctx.fillStyle = "rgba(255, 255, 255, 0.08)";
    ctx.fillRect(
      boardPadding + state.hover.file * squareSize + 3,
      boardPadding + state.hover.rank * squareSize + 3,
      squareSize - 6,
      squareSize - 6
    );
  }
  if (hintColor) {
    ctx.fillStyle = hintColor.replace("0.8", "0.12").replace("0.85", "0.12");
    ctx.fillRect(
      boardPadding + state.hover.file * squareSize + 3,
      boardPadding + state.hover.rank * squareSize + 3,
      squareSize - 6,
      squareSize - 6
    );
  }
  ctx.restore();
};

const drawLastMove = () => {
  if (!state.lastMove) return;
  const squares = [state.lastMove.from, state.lastMove.to];
  ctx.save();
  squares.forEach((square) => {
    if (!square) return;
    ctx.fillStyle = colors.lastMove;
    ctx.fillRect(
      boardPadding + square.file * squareSize + 3,
      boardPadding + square.rank * squareSize + 3,
      squareSize - 6,
      squareSize - 6
    );
    ctx.strokeStyle = colors.lastMoveEdge;
    ctx.lineWidth = 3;
    ctx.strokeRect(
      boardPadding + square.file * squareSize + 3,
      boardPadding + square.rank * squareSize + 3,
      squareSize - 6,
      squareSize - 6
    );
  });
  ctx.restore();
};

const updatePieces = (dt) => {
  state.pieces.forEach((piece) => {
    if (!piece.anim) return;
    piece.anim.elapsed += dt;
    const t = Math.min(1, piece.anim.elapsed / piece.anim.duration);
    const eased = 1 - Math.pow(1 - t, 3);
    piece.x = piece.anim.fromX + (piece.anim.toX - piece.anim.fromX) * eased;
    piece.y = piece.anim.fromY + (piece.anim.toY - piece.anim.fromY) * eased;
    if (t >= 1) {
      piece.x = piece.anim.toX;
      piece.y = piece.anim.toY;
      piece.targetX = piece.anim.toX;
      piece.targetY = piece.anim.toY;
      piece.anim = null;
    }
  });
};

const drawPieces = () => {
  const draggingId = state.dragging ? state.dragging.id : null;
  state.pieces.forEach((piece) => {
    if (piece.id === draggingId) return;
    drawSpritePiece(piece, false);
  });
  if (state.dragging) {
    drawSpritePiece(state.dragging, true);
  }
};

const renderFrame = () => {
  drawBoard();
  drawLastMove();
  drawHover();
  drawPieces();
};

export { loadSprites, updatePieces, renderFrame };
