import { ref } from "vue";

const PX_PER_MM = 2;

export function useCanvas() {
  const scale = ref(1);
  const offsetX = ref(0);
  const offsetY = ref(0);
  const isPanning = ref(false);
  const lastPan = ref({ x: 0, y: 0 });

  function mmToPx(mm: number): number {
    return mm * PX_PER_MM;
  }

  function pxToMm(px: number): number {
    return px / PX_PER_MM;
  }

  /** Screen (canvas-relative) coords to paper mm. */
  function screenToPaper(screenX: number, screenY: number): { x_mm: number; y_mm: number } {
    const x = (screenX - offsetX.value) / scale.value;
    const y = (screenY - offsetY.value) / scale.value;
    return { x_mm: pxToMm(x), y_mm: pxToMm(y) };
  }

  /** Paper mm to screen (canvas) coords. */
  function paperToScreen(x_mm: number, y_mm: number): { x: number; y: number } {
    const x = mmToPx(x_mm) * scale.value + offsetX.value;
    const y = mmToPx(y_mm) * scale.value + offsetY.value;
    return { x, y };
  }

  function zoom(delta: number, centerX?: number, centerY?: number) {
    const factor = delta > 0 ? 1.1 : 1 / 1.1;
    const newScale = Math.min(5, Math.max(0.2, scale.value * factor));
    if (centerX != null && centerY != null) {
      const sx = (centerX - offsetX.value) / scale.value;
      const sy = (centerY - offsetY.value) / scale.value;
      offsetX.value = centerX - sx * newScale;
      offsetY.value = centerY - sy * newScale;
    }
    scale.value = newScale;
  }

  function startPan(screenX: number, screenY: number) {
    isPanning.value = true;
    lastPan.value = { x: screenX, y: screenY };
  }

  function movePan(screenX: number, screenY: number) {
    if (!isPanning.value) return;
    offsetX.value += screenX - lastPan.value.x;
    offsetY.value += screenY - lastPan.value.y;
    lastPan.value = { x: screenX, y: screenY };
  }

  function endPan() {
    isPanning.value = false;
  }

  return {
    scale,
    offsetX,
    offsetY,
    isPanning,
    PX_PER_MM,
    mmToPx,
    pxToMm,
    screenToPaper,
    paperToScreen,
    zoom,
    startPan,
    movePan,
    endPan,
  };
}
