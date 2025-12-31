import { state, gameState, boardMatrixFromPieces, updateFenOutput } from "./state.js";

const validateMove = async (fromFile, fromRank, toFile, toRank) => {
  const payload = {
    board: boardMatrixFromPieces(),
    move: {
      from: { file: fromFile, rank: fromRank },
      to: { file: toFile, rank: toRank },
    },
    turn: state.turn.toLowerCase(),
    castling: gameState.castling,
    en_passant: gameState.enPassant,
    halfmove: gameState.halfmove,
    fullmove: gameState.fullmove,
  };
  const response = await fetch("/api/validate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    return { legal: false, reason: "validate_failed" };
  }
  return response.json();
};

const requestFen = async () => {
  const payload = {
    board: boardMatrixFromPieces(),
    turn: state.turn.toLowerCase(),
    castling: gameState.castling,
    en_passant: gameState.enPassant,
    halfmove: gameState.halfmove,
    fullmove: gameState.fullmove,
  };
  try {
    const response = await fetch("/api/fen", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (response.ok) {
      const data = await response.json();
      updateFenOutput(data.fen);
      return data.fen;
    }
  } catch (error) {
    updateFenOutput("FEN unavailable");
  }
  return null;
};

const requestEngineMove = async (depth = null) => {
  const payload = {
    board: boardMatrixFromPieces(),
    turn: state.turn.toLowerCase(),
    castling: gameState.castling,
    en_passant: gameState.enPassant,
    halfmove: gameState.halfmove,
    fullmove: gameState.fullmove,
  };
  if (typeof depth === "number") {
    payload.depth = depth;
  }
  const response = await fetch("/api/move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    return { move: null, error: "request_failed" };
  }
  return response.json();
};

const requestWinProbability = async () => {
  const payload = {
    board: boardMatrixFromPieces(),
    turn: state.turn.toLowerCase(),
    castling: gameState.castling,
    en_passant: gameState.enPassant,
    halfmove: gameState.halfmove,
    fullmove: gameState.fullmove,
  };
  try {
    const response = await fetch("/api/win-probability", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      return null;
    }
    return response.json();
  } catch (error) {
    return null;
  }
};

export { validateMove, requestEngineMove, requestFen, requestWinProbability };
