import {
  canvas,
  newGameButton,
  undoButton,
  restartButton,
  engineDepthInput,
  engineDepthValue,
  engineThinking,
  fenCopyButton,
  fenCopyFeedback,
  boardFrame,
  winProbabilityBar,
  squareSize,
} from "./context.js";
import {
  state,
  gameState,
  createPieces,
  setTurn,
  updateFenOutput,
  clearGameOver,
  pieceAt,
  renderMoveList,
  undoPlayerTurn,
} from "./state.js";
import { loadSprites, updatePieces, renderFrame } from "./render.js";
import { applyValidatedMove, bindInputHandlers } from "./interaction.js";
import { requestFen, requestEngineMove, validateMove, requestWinProbability } from "./api.js";

let fenCopyTimer = null;
let autoMoveTimer = null;
let winProbabilityRequestId = 0;

const setEngineThinking = (thinking) => {
  state.engineThinking = thinking;
  if (engineThinking) {
    engineThinking.classList.toggle("hidden", !thinking);
  }
};

const cancelPendingEngine = () => {
  state.engineRequestId += 1;
  setEngineThinking(false);
  state.validating = false;
  if (autoMoveTimer) {
    clearTimeout(autoMoveTimer);
    autoMoveTimer = null;
  }
};

const clampProbability = (value) => Math.min(1, Math.max(0, value));

const setWinProbability = (whiteValue) => {
  const white = clampProbability(whiteValue);
  const black = clampProbability(1 - white);
  state.winProbability = { white, black, hasValue: true };
  if (winProbabilityBar) {
    winProbabilityBar.style.setProperty("--white-pct", `${white * 100}%`);
  }
};

const refreshWinProbability = async () => {
  const requestId = winProbabilityRequestId + 1;
  winProbabilityRequestId = requestId;
  const result = await requestWinProbability();
  if (requestId !== winProbabilityRequestId) return;
  if (!result || !Number.isFinite(result.white)) {
    return;
  }
  setWinProbability(result.white);
};

const updateProbabilityBarLayout = () => {
  if (!winProbabilityBar || !boardFrame || !canvas) return;
  const layoutSection = document.querySelector("#app > section");
  const frameRect = boardFrame.getBoundingClientRect();
  const canvasRect = canvas.getBoundingClientRect();
  if (!canvasRect.width || !canvasRect.height) return;
  const scale = canvasRect.width / canvas.width;
  const barWidth = squareSize * scale * 0.5;
  const gapValue = layoutSection ? getComputedStyle(layoutSection).gap : "24px";
  const panelGap = Number.parseFloat(gapValue) || 24;
  winProbabilityBar.style.left = `${-(panelGap + barWidth)}px`;
  winProbabilityBar.style.top = "0px";
  winProbabilityBar.style.width = `${barWidth}px`;
  winProbabilityBar.style.height = `${frameRect.height}px`;
};

const resetGame = () => {
  cancelPendingEngine();
  state.pieces = createPieces();
  state.dragging = null;
  state.hover = null;
  state.validating = false;
  state.lastMove = null;
  setTurn("White");
  gameState.castling = "KQkq";
  gameState.enPassant = null;
  gameState.halfmove = 0;
  gameState.fullmove = 1;
  gameState.moveHistory = [];
  gameState.undoStack = [];
  gameState.fen = "";
  clearGameOver();
  renderMoveList();
  updateFenOutput("Loading FEN...");
  requestFen();
  refreshWinProbability();
};

const updateEngineDepth = (value) => {
  const depthValue = Number.parseInt(value, 10);
  if (!Number.isNaN(depthValue)) {
    state.engineDepth = depthValue;
  }
  if (engineDepthValue) {
    engineDepthValue.textContent = `${state.engineDepth}`;
  }
};

const requestComputerMove = async () => {
  if (gameState.gameOver || state.engineThinking || state.validating) {
    return;
  }
  const requestId = state.engineRequestId + 1;
  state.engineRequestId = requestId;
  setEngineThinking(true);
  state.validating = true;
  try {
    const result = await requestEngineMove(state.engineDepth);
    if (requestId !== state.engineRequestId) return;
    if (!result || result.error || !result.from || !result.to) {
      return;
    }
    const piece = pieceAt(result.from.file, result.from.rank);
    if (!piece) {
      return;
    }
    const validation = await validateMove(
      result.from.file,
      result.from.rank,
      result.to.file,
      result.to.rank
    );
    if (requestId !== state.engineRequestId) return;
    applyValidatedMove(
      piece,
      result.from.file,
      result.from.rank,
      result.to.file,
      result.to.rank,
      validation
    );
  } catch (error) {
    // Silent failure for engine actions.
  } finally {
    if (requestId === state.engineRequestId) {
      setEngineThinking(false);
      state.validating = false;
    }
  }
};

const scheduleComputerMove = () => {
  if (autoMoveTimer) {
    clearTimeout(autoMoveTimer);
  }
  const attempt = () => {
    if (gameState.gameOver || state.turn !== "Black") {
      autoMoveTimer = null;
      return;
    }
    if (state.engineThinking || state.validating) {
      autoMoveTimer = setTimeout(attempt, 50);
      return;
    }
    autoMoveTimer = null;
    requestComputerMove();
  };
  autoMoveTimer = setTimeout(attempt, 0);
};

const copyFenToClipboard = async () => {
  if (!gameState.fen) {
    return;
  }
  try {
    await navigator.clipboard.writeText(gameState.fen);
  } catch (error) {
    const textarea = document.createElement("textarea");
    textarea.value = gameState.fen;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "absolute";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }
  if (fenCopyFeedback) {
    fenCopyFeedback.classList.remove("hidden");
    if (fenCopyTimer) {
      clearTimeout(fenCopyTimer);
    }
    fenCopyTimer = setTimeout(() => {
      fenCopyFeedback.classList.add("hidden");
    }, 1200);
  }
};

let lastTime = performance.now();
const tick = (now) => {
  const dt = now - lastTime;
  lastTime = now;
  updatePieces(dt);
  renderFrame();
  requestAnimationFrame(tick);
};

const init = () => {
  state.pieces = createPieces();
  setTurn(state.turn);
  bindInputHandlers();
  loadSprites();
  updateFenOutput("Loading FEN...");
  requestFen();
  updateEngineDepth(engineDepthInput?.value ?? state.engineDepth);

  document.addEventListener("chess:move-applied", () => {
    refreshWinProbability();
    if (gameState.gameOver) return;
    if (state.turn === "Black") {
      scheduleComputerMove();
    }
  });

  if (engineDepthInput) {
    engineDepthInput.addEventListener("input", (event) => {
      updateEngineDepth(event.target.value);
    });
  }

  if (newGameButton) {
    newGameButton.addEventListener("click", resetGame);
  }

  if (undoButton) {
    undoButton.addEventListener("click", () => {
      cancelPendingEngine();
      const undone = undoPlayerTurn();
      if (undone) {
        updateFenOutput(gameState.fen);
        refreshWinProbability();
      }
    });
  }

  if (fenCopyButton) {
    fenCopyButton.addEventListener("click", copyFenToClipboard);
  }

  if (restartButton) {
    restartButton.addEventListener("click", resetGame);
  }

  updateProbabilityBarLayout();
  window.addEventListener("resize", updateProbabilityBarLayout);
  refreshWinProbability();

  requestAnimationFrame(tick);
};

init();
