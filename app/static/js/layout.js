import { boardShell, root } from "./context.js";

const updateLayoutVars = () => {
  if (!boardShell) return;
  const rect = boardShell.getBoundingClientRect();
  const totalHeight = rect.height;
  const panelWidth = Math.max(210, Math.min(280, rect.width * 0.32));
  const fenHeight = Math.max(140, Math.min(200, totalHeight * 0.26));
  root.style.setProperty("--board-total", `${Math.round(totalHeight)}px`);
  root.style.setProperty("--panel-width", `${Math.round(panelWidth)}px`);
  root.style.setProperty("--fen-height", `${Math.round(fenHeight)}px`);
};

const initLayout = () => {
  updateLayoutVars();
  window.addEventListener("resize", () => requestAnimationFrame(updateLayoutVars));
};

export { initLayout, updateLayoutVars };
