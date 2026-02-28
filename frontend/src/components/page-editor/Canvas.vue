<template>
  <div ref="containerRef" class="canvas-container">
    <canvas
      ref="canvasRef"
      :width="canvasWidth"
      :height="canvasHeight"
      class="canvas"
      @mousedown="onMouseDown"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
      @mouseleave="onMouseUp"
      @wheel.prevent="onWheel"
      @contextmenu.prevent
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { storeToRefs } from "pinia";
import { usePageEditorStore } from "../../stores/pageEditor";
import { useCanvas } from "../../composables/useCanvas";
import type { Element, TextElement, VariableElement, LineElement } from "../../types/pageEditor";
import { isVariableElement, isLineElement } from "../../types/pageEditor";
import { snapPoint, snapBox } from "../../utils/snap";
import {
  PX_PER_MM,
  TEXT_SIZE_PT,
  TEXT_LEADING,
  ptToPx,
  resolveTextStyle,
  buildCanvasFont,
  getTextBoundsMm,
} from "../../composables/useCanvasText";

const VARIABLE_FONT_SIZE_PT = 10;
const VARIABLE_BOX_FILL = "#fafafa";

const TEXT_SIZE_PX = ptToPx(TEXT_SIZE_PT);
const VARIABLE_FONT_SIZE_PX = ptToPx(VARIABLE_FONT_SIZE_PT);

const store = usePageEditorStore();
const { elements, paper, selectedId, showGrid, snapEnabled, snapThresholdMm } = storeToRefs(store);

const containerRef = ref<HTMLDivElement | null>(null);
const canvasRef = ref<HTMLCanvasElement | null>(null);
const containerSize = ref({ width: 800, height: 600 });

const { scale, offsetX, offsetY, isPanning, screenToPaper, zoom, startPan, movePan, endPan } = useCanvas();

const canvasWidth = computed(() => containerSize.value.width);
const canvasHeight = computed(() => containerSize.value.height);

const HANDLE_SIZE = 8;
const HIT_PAD = 4;
const MIN_VARIABLE_WIDTH_MM = 10;
const MIN_VARIABLE_HEIGHT_LINES = 1;
const VARIABLE_LINE_HEIGHT_MM = 5;

interface ResizeState {
  w: number;
  h: number;
  elementX: number;
  elementY: number;
}

const handleTransformations: Record<
  number,
  (dx: number, dy: number, s: ResizeState) => ResizeState
> = {
  0: (dx, dy, { w, h, elementX, elementY }) => ({
    elementX: elementX + dx,
    elementY: elementY + dy,
    w: Math.max(MIN_VARIABLE_WIDTH_MM, w - dx),
    h: Math.max(MIN_VARIABLE_HEIGHT_LINES, h - dy / VARIABLE_LINE_HEIGHT_MM),
  }),
  1: (dx, dy, { w, h, elementX, elementY }) => ({
    elementX,
    elementY: elementY + dy,
    w: Math.max(MIN_VARIABLE_WIDTH_MM, w + dx),
    h: Math.max(MIN_VARIABLE_HEIGHT_LINES, h - dy / VARIABLE_LINE_HEIGHT_MM),
  }),
  2: (dx, dy, { w, h, elementX, elementY }) => ({
    elementX,
    elementY,
    w: Math.max(MIN_VARIABLE_WIDTH_MM, w + dx),
    h: Math.max(MIN_VARIABLE_HEIGHT_LINES, h + dy / VARIABLE_LINE_HEIGHT_MM),
  }),
  3: (dx, dy, { w, h, elementX, elementY }) => ({
    elementX: elementX + dx,
    elementY,
    w: Math.max(MIN_VARIABLE_WIDTH_MM, w - dx),
    h: Math.max(MIN_VARIABLE_HEIGHT_LINES, h + dy / VARIABLE_LINE_HEIGHT_MM),
  }),
  4: (_dx, dy, { w, h, elementX, elementY }) => ({
    elementX,
    elementY: elementY + dy,
    w,
    h: Math.max(MIN_VARIABLE_HEIGHT_LINES, h - dy / VARIABLE_LINE_HEIGHT_MM),
  }),
  5: (dx, _dy, { w, h, elementX, elementY }) => ({
    elementX,
    elementY,
    w: Math.max(MIN_VARIABLE_WIDTH_MM, w + dx),
    h,
  }),
  6: (_dx, dy, { w, h, elementX, elementY }) => ({
    elementX,
    elementY,
    w,
    h: Math.max(MIN_VARIABLE_HEIGHT_LINES, h + dy / VARIABLE_LINE_HEIGHT_MM),
  }),
  7: (dx, _dy, { w, h, elementX, elementY }) => ({
    elementX: elementX + dx,
    elementY,
    w: Math.max(MIN_VARIABLE_WIDTH_MM, w - dx),
    h,
  }),
};

interface DragState {
  id: string;
  kind: "move" | "resize" | "line-end";
  handleIndex?: number;
  startX_mm: number;
  startY_mm: number;
  startMouseX_mm?: number;
  startMouseY_mm?: number;
  startElementX_mm?: number;
  startElementY_mm?: number;
  startW?: number;
  startH?: number;
  startX1?: number;
  startY1?: number;
  startX2?: number;
  startY2?: number;
  startWidth_mm?: number;
  startHeight_mm?: number;
  endIndex?: number;
  otherEndX?: number;
  otherEndY?: number;
}
const dragState = ref<DragState | null>(null);
const spacePressed = ref(false);

function getElementBounds(
  e: Element,
  ctx?: CanvasRenderingContext2D | null
): { x: number; y: number; w: number; h: number } {
  if (e.type === "text") {
    const te = e as TextElement;
    if (ctx) {
      const { w, h } = getTextBoundsMm(te, ctx);
      return { x: te.x_mm, y: te.y_mm, w, h };
    }
    const resolved = resolveTextStyle(
      te.text_style as Record<string, unknown> | undefined,
      TEXT_SIZE_PT
    );
    const wMm = Math.max(20, (te.content.length * resolved.sizePx * 0.6) / PX_PER_MM);
    const hMm = (resolved.sizePx / PX_PER_MM) * TEXT_LEADING;
    return { x: te.x_mm, y: te.y_mm, w: wMm, h: hMm };
  }
  if (e.type === "variable") {
    const ve = e as VariableElement;
    return { x: ve.x_mm, y: ve.y_mm, w: ve.width_mm, h: ve.height_lines * VARIABLE_LINE_HEIGHT_MM };
  }
  const le = e as LineElement;
  const minX = Math.min(le.x1_mm, le.x2_mm);
  const minY = Math.min(le.y1_mm, le.y2_mm);
  const maxX = Math.max(le.x1_mm, le.x2_mm);
  const maxY = Math.max(le.y1_mm, le.y2_mm);
  return { x: minX, y: minY, w: Math.max(1, maxX - minX), h: Math.max(1, maxY - minY) };
}

function getSnapTargets(
  excludeId: string,
  ctx?: CanvasRenderingContext2D | null
): { xTargets: number[]; yTargets: number[] } {
  const { width: w, height: h } = paper.value;
  const xTargets = [0, w / 2, w];
  const yTargets = [0, h / 2, h];
  for (const e of elements.value) {
    if (e.id === excludeId) continue;
    const b = getElementBounds(e, ctx);
    xTargets.push(b.x, b.x + b.w / 2, b.x + b.w);
    yTargets.push(b.y, b.y + b.h / 2, b.y + b.h);
  }
  return { xTargets, yTargets };
}

interface SnapOptions {
  enabled: boolean;
  excludeId: string;
  ctx: CanvasRenderingContext2D | null;
  threshold: number;
}

function snapPointIfNeeded(
  x_mm: number,
  y_mm: number,
  options: SnapOptions
): { x_mm: number; y_mm: number } {
  if (!options.enabled) return { x_mm, y_mm };
  const t = getSnapTargets(options.excludeId, options.ctx);
  return snapPoint(x_mm, y_mm, t.xTargets, t.yTargets, options.threshold);
}

function snapBoxIfNeeded(
  x_mm: number,
  y_mm: number,
  w_mm: number,
  h_mm: number,
  options: SnapOptions
): { x_mm: number; y_mm: number } {
  if (!options.enabled) return { x_mm, y_mm };
  const t = getSnapTargets(options.excludeId, options.ctx);
  return snapBox(x_mm, y_mm, w_mm, h_mm, t.xTargets, t.yTargets, options.threshold);
}

function hitTest(screenX: number, screenY: number): { element: Element; handleIndex?: number } | null {
  const { x_mm: mx, y_mm: my } = screenToPaper(screenX, screenY);
  const padMm = HIT_PAD / PX_PER_MM;
  for (let i = elements.value.length - 1; i >= 0; i--) {
    const e = elements.value[i];
    if (!e) continue;
    if (e.type === "line") {
      const le = e as LineElement;
      const d1 = Math.hypot(mx - le.x1_mm, my - le.y1_mm);
      const d2 = Math.hypot(mx - le.x2_mm, my - le.y2_mm);
      const linePad = 3;
      if (d1 <= linePad) return { element: e, handleIndex: 0 };
      if (d2 <= linePad) return { element: e, handleIndex: 1 };
      const dist = pointToLineDist(mx, my, le.x1_mm, le.y1_mm, le.x2_mm, le.y2_mm);
      if (dist <= linePad) return { element: e };
    } else {
      const b = getElementBounds(e);
      if (e.type === "variable" && e.id === selectedId.value) {
        const ve = e as VariableElement;
        const handles = getResizeHandles(ve);
        for (let h = 0; h < handles.length; h++) {
          const handle = handles[h];
          if (!handle) continue;
          const [hx, hy] = handle;
          if (Math.abs(mx - hx) <= padMm && Math.abs(my - hy) <= padMm) return { element: e, handleIndex: h };
        }
      }
      if (mx >= b.x - padMm && mx <= b.x + b.w + padMm && my >= b.y - padMm && my <= b.y + b.h + padMm) {
        return { element: e };
      }
    }
  }
  return null;
}

function pointToLineDist(px: number, py: number, x1: number, y1: number, x2: number, y2: number): number {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.hypot(dx, dy) || 1e-6;
  const t = Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / (len * len)));
  const nx = x1 + t * dx;
  const ny = y1 + t * dy;
  return Math.hypot(px - nx, py - ny);
}

function getResizeHandles(ve: VariableElement): [number, number][] {
  const { x, y, w, h } = { x: ve.x_mm, y: ve.y_mm, w: ve.width_mm, h: ve.height_lines * VARIABLE_LINE_HEIGHT_MM };
  return [
    [x, y], [x + w, y], [x + w, y + h], [x, y + h],
    [x + w / 2, y], [x + w, y + h / 2], [x + w / 2, y + h], [x, y + h / 2],
  ];
}

function onMouseDown(ev: MouseEvent) {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const screenX = ev.clientX - rect.left;
  const screenY = ev.clientY - rect.top;
  if (ev.button === 1 || (ev.button === 0 && spacePressed.value)) {
    startPan(screenX, screenY);
    return;
  }
  if (ev.button !== 0) return;
  const mousePaper = screenToPaper(screenX, screenY);
  const hit = hitTest(screenX, screenY);
  if (hit) {
    const e = hit.element;
    const ctx = canvas.getContext("2d") ?? null;
    if (e.type === "line") {
      const le = e as LineElement;
      if (hit.handleIndex === 0) {
        dragState.value = {
          id: e.id, kind: "line-end", endIndex: 0,
          startX_mm: le.x1_mm, startY_mm: le.y1_mm,
          otherEndX: le.x2_mm, otherEndY: le.y2_mm,
        };
      } else if (hit.handleIndex === 1) {
        dragState.value = {
          id: e.id, kind: "line-end", endIndex: 1,
          startX_mm: le.x2_mm, startY_mm: le.y2_mm,
          otherEndX: le.x1_mm, otherEndY: le.y1_mm,
        };
      } else {
        dragState.value = {
          id: e.id, kind: "move",
          startX_mm: mousePaper.x_mm,
          startY_mm: mousePaper.y_mm,
          startX1: le.x1_mm, startY1: le.y1_mm, startX2: le.x2_mm, startY2: le.y2_mm,
        };
      }
    } else if (e.type === "variable" && hit.handleIndex != null && hit.handleIndex < 8) {
      const ve = e as VariableElement;
      dragState.value = {
        id: e.id, kind: "resize", handleIndex: hit.handleIndex,
        startX_mm: mousePaper.x_mm,
        startY_mm: mousePaper.y_mm,
        startElementX_mm: ve.x_mm, startElementY_mm: ve.y_mm,
        startW: ve.width_mm, startH: ve.height_lines,
      };
    } else {
      const el = e as TextElement | VariableElement;
      const bounds = getElementBounds(e, ctx);
      dragState.value = {
        id: e.id, kind: "move",
        startX_mm: el.x_mm,
        startY_mm: el.y_mm,
        startMouseX_mm: mousePaper.x_mm,
        startMouseY_mm: mousePaper.y_mm,
        startWidth_mm: bounds.w,
        startHeight_mm: bounds.h,
      };
    }
    store.setSelected(e.id);
  } else {
    store.setSelected(null);
  }
}

function handlePan(screenX: number, screenY: number) {
  movePan(screenX, screenY);
}

function handleMoveDrag(drag: DragState, x_mm: number, y_mm: number, snapOpts: SnapOptions) {
  if (drag.startX1 != null && drag.startY1 != null && drag.startX2 != null && drag.startY2 != null) {
    const x1 = drag.startX1 + (x_mm - drag.startX_mm);
    const y1 = drag.startY1 + (y_mm - drag.startY_mm);
    const x2 = drag.startX2 + (x_mm - drag.startX_mm);
    const y2 = drag.startY2 + (y_mm - drag.startY_mm);
    const centerX = (x1 + x2) / 2;
    const centerY = (y1 + y2) / 2;
    const snapped = snapPointIfNeeded(centerX, centerY, snapOpts);
    const offsetX = snapped.x_mm - centerX;
    const offsetY = snapped.y_mm - centerY;
    store.updateLineEndpoints(drag.id, x1 + offsetX, y1 + offsetY, x2 + offsetX, y2 + offsetY);
  } else if (drag.startWidth_mm != null && drag.startHeight_mm != null) {
    const newX = drag.startX_mm + (x_mm - (drag.startMouseX_mm ?? drag.startX_mm));
    const newY = drag.startY_mm + (y_mm - (drag.startMouseY_mm ?? drag.startY_mm));
    const snapped = snapBoxIfNeeded(newX, newY, drag.startWidth_mm, drag.startHeight_mm, snapOpts);
    store.updatePosition(drag.id, snapped.x_mm, snapped.y_mm);
  }
}

function handleResizeDrag(drag: DragState, x_mm: number, y_mm: number, _snapOpts: SnapOptions) {
  if (drag.handleIndex == null || drag.startW == null || drag.startH == null || drag.startElementX_mm == null || drag.startElementY_mm == null) return;
  const dx = x_mm - drag.startX_mm;
  const dy = y_mm - drag.startY_mm;
  let state: ResizeState = {
    w: drag.startW,
    h: drag.startH,
    elementX: drag.startElementX_mm,
    elementY: drag.startElementY_mm,
  };
  const transform = handleTransformations[drag.handleIndex];
  if (transform) {
    state = transform(dx, dy, state);
  }
  store.updatePosition(drag.id, state.elementX, state.elementY);
  store.updateSize(drag.id, state.w, state.h);
}

function handleLineEndDrag(drag: DragState, x_mm: number, y_mm: number, snapOpts: SnapOptions) {
  if (drag.endIndex === undefined || drag.otherEndX == null || drag.otherEndY == null) return;
  const snapped = snapPointIfNeeded(x_mm, y_mm, snapOpts);
  if (drag.endIndex === 0) store.updateLineEndpoints(drag.id, snapped.x_mm, snapped.y_mm, drag.otherEndX, drag.otherEndY);
  else store.updateLineEndpoints(drag.id, drag.otherEndX, drag.otherEndY, snapped.x_mm, snapped.y_mm);
}

type DragHandler = (drag: DragState, x_mm: number, y_mm: number, snapOpts: SnapOptions) => void;

const dragHandlers: Record<DragState["kind"], DragHandler> = {
  move: handleMoveDrag,
  resize: handleResizeDrag,
  "line-end": handleLineEndDrag,
};

function handleDrag(drag: DragState, x_mm: number, y_mm: number, snapOpts: SnapOptions) {
  dragHandlers[drag.kind](drag, x_mm, y_mm, snapOpts);
}

function onMouseMove(ev: MouseEvent) {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const screenX = ev.clientX - rect.left;
  const screenY = ev.clientY - rect.top;
  if (isPanning.value) {
    handlePan(screenX, screenY);
    redraw();
    return;
  }
  const drag = dragState.value;
  if (!drag) {
    redraw();
    return;
  }
  const { x_mm, y_mm } = screenToPaper(screenX, screenY);
  const snapOpts: SnapOptions = {
    enabled: snapEnabled.value && !ev.altKey,
    excludeId: drag.id,
    ctx: canvasRef.value?.getContext("2d") ?? null,
    threshold: snapThresholdMm.value,
  };
  handleDrag(drag, x_mm, y_mm, snapOpts);
  redraw();
}

function onMouseUp() {
  endPan();
  dragState.value = null;
  redraw();
}

function onWheel(ev: WheelEvent) {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const x = ev.clientX - rect.left;
  const y = ev.clientY - rect.top;
  zoom(-ev.deltaY, x, y);
  redraw();
}

let rafId = 0;
function redraw() {
  if (rafId) cancelAnimationFrame(rafId);
  rafId = requestAnimationFrame(() => {
    rafId = 0;
    const canvas = canvasRef.value;
    const ctx = canvas?.getContext("2d");
    if (!ctx) return;
    const w = canvasWidth.value;
    const h = canvasHeight.value;
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = "#27272a";
    ctx.fillRect(0, 0, w, h);
    ctx.restore();
    ctx.save();
    ctx.translate(offsetX.value, offsetY.value);
    ctx.scale(scale.value, scale.value);
    const paperW = paper.value.width * PX_PER_MM;
    const paperH = paper.value.height * PX_PER_MM;
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, paperW, paperH);
    ctx.strokeStyle = "#52525b";
    ctx.lineWidth = 1;
    ctx.strokeRect(0, 0, paperW, paperH);
    if (showGrid.value) {
      ctx.strokeStyle = "#3f3f46";
      ctx.lineWidth = 0.5;
      for (let x = 0; x <= paper.value.width; x++) {
        const px = x * PX_PER_MM;
        ctx.beginPath();
        ctx.moveTo(px, 0);
        ctx.lineTo(px, paperH);
        ctx.stroke();
      }
      for (let y = 0; y <= paper.value.height; y++) {
        const py = y * PX_PER_MM;
        ctx.beginPath();
        ctx.moveTo(0, py);
        ctx.lineTo(paperW, py);
        ctx.stroke();
      }
    }
    elements.value.forEach((e) => drawElement(ctx, e));
    const sel = selectedId.value ? elements.value.find((e) => e.id === selectedId.value) : null;
    if (sel && isVariableElement(sel)) {
      drawHandles(ctx, sel as VariableElement);
    }
    if (sel && isLineElement(sel)) {
      drawLineHandles(ctx, sel as LineElement);
    }
    ctx.restore();
  });
}

function drawElement(ctx: CanvasRenderingContext2D, e: Element) {
  const s = scale.value;
  ctx.save();
  if (e.type === "text") {
    const te = e as TextElement;
    const resolved = resolveTextStyle(
      te.text_style as Record<string, unknown> | undefined,
      TEXT_SIZE_PT
    );
    const x = te.x_mm * PX_PER_MM;
    const y = te.y_mm * PX_PER_MM;
    ctx.fillStyle = resolved.fill;
    ctx.font = buildCanvasFont(resolved);
    ctx.fillText(te.content, x, y + resolved.sizePx);
    if (e.id === selectedId.value) {
      const b = getTextBoundsMm(te, ctx);
      ctx.strokeStyle = "#3b82f6";
      ctx.lineWidth = 2 / s;
      ctx.strokeRect(x, y, b.w * PX_PER_MM, b.h * PX_PER_MM);
    }
  } else if (e.type === "variable") {
    const ve = e as VariableElement;
    const resolved = resolveTextStyle(
      ve.text_style as Record<string, unknown> | undefined,
      VARIABLE_FONT_SIZE_PT
    );
    const x = ve.x_mm * PX_PER_MM;
    const y = ve.y_mm * PX_PER_MM;
    const w = ve.width_mm * PX_PER_MM;
    const h = Math.max(resolved.sizePx * TEXT_LEADING, ve.height_lines * VARIABLE_LINE_HEIGHT_MM * PX_PER_MM);
    ctx.fillStyle = VARIABLE_BOX_FILL;
    ctx.fillRect(x, y, w, h);
    ctx.fillStyle = resolved.fill;
    ctx.font = buildCanvasFont(resolved);
    const align = (ve.text_style as Record<string, unknown> | undefined)?.align as string | undefined;
    const textAlign = align === "center" ? "center" : align === "right" ? "right" : "left";
    ctx.textAlign = textAlign;
    const pad = 4;
    const textX = align === "center" ? x + w / 2 : align === "right" ? x + w - pad : x + pad;
    ctx.fillText(ve.var_name, textX, y + resolved.sizePx);
    ctx.textAlign = "left";
    if (e.id === selectedId.value) {
      ctx.strokeStyle = "#3b82f6";
      ctx.lineWidth = 2 / s;
      ctx.strokeRect(x, y, w, h);
    }
  } else {
    const le = e as LineElement;
    const x1 = le.x1_mm * PX_PER_MM;
    const y1 = le.y1_mm * PX_PER_MM;
    const x2 = le.x2_mm * PX_PER_MM;
    const y2 = le.y2_mm * PX_PER_MM;
    ctx.strokeStyle = e.id === selectedId.value ? "#3b82f6" : "#52525b";
    ctx.lineWidth = (e.id === selectedId.value ? 2 : 1) / s;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  }
  ctx.restore();
}

function drawHandles(ctx: CanvasRenderingContext2D, ve: VariableElement) {
  const handles = getResizeHandles(ve);
  const size = HANDLE_SIZE / scale.value;
  ctx.fillStyle = "#3b82f6";
  ctx.strokeStyle = "#fff";
  ctx.lineWidth = 1 / scale.value;
  handles.forEach(([hx, hy]) => {
    const x = hx * PX_PER_MM - size / 2;
    const y = hy * PX_PER_MM - size / 2;
    ctx.fillRect(x, y, size, size);
    ctx.strokeRect(x, y, size, size);
  });
}

function drawLineHandles(ctx: CanvasRenderingContext2D, le: LineElement) {
  const size = HANDLE_SIZE / scale.value;
  ctx.fillStyle = "#3b82f6";
  ctx.strokeStyle = "#fff";
  ctx.lineWidth = 1 / scale.value;
  const pts: [number, number][] = [[le.x1_mm, le.y1_mm], [le.x2_mm, le.y2_mm]];
  for (const [gx, gy] of pts) {
    const x = gx * PX_PER_MM - size / 2;
    const y = gy * PX_PER_MM - size / 2;
    ctx.fillRect(x, y, size, size);
    ctx.strokeRect(x, y, size, size);
  }
}

onMounted(() => {
  const container = containerRef.value;
  if (!container) return;
  const ro = new ResizeObserver((entries) => {
    const entry = entries[0];
    if (entry) {
      const { width, height } = entry.contentRect;
      containerSize.value = { width: Math.max(100, width), height: Math.max(100, height) };
    }
  });
  ro.observe(container);

  (async () => {
    try {
      const fonts = (document as Document & { fonts?: FontFaceSet }).fonts;
      if (fonts?.load) {
        await fonts.load(`400 ${TEXT_SIZE_PX}px "Libertinus Serif"`);
        await fonts.load(`400 ${VARIABLE_FONT_SIZE_PX}px "Libertinus Serif"`);
        await fonts.load(`600 ${TEXT_SIZE_PX}px "Libertinus Serif"`);
        await fonts.load(`700 ${TEXT_SIZE_PX}px "Libertinus Serif"`);
      }
    } catch {
      // ignore
    } finally {
      redraw();
    }
  })();

  const keyDown = (e: KeyboardEvent) => { if (e.code === "Space") spacePressed.value = true; };
  const keyUp = (e: KeyboardEvent) => { if (e.code === "Space") { spacePressed.value = false; endPan(); } };
  window.addEventListener("keydown", keyDown);
  window.addEventListener("keyup", keyUp);
  onUnmounted(() => {
    ro.disconnect();
    window.removeEventListener("keydown", keyDown);
    window.removeEventListener("keyup", keyUp);
  });
});

watch([elements, paper, selectedId, showGrid, scale, offsetX, offsetY], () => redraw(), { deep: true });
onMounted(() => redraw());
</script>

<style scoped>
.canvas-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #27272a;
}
.canvas {
  display: block;
  width: 100%;
  height: 100%;
  cursor: default;
}
</style>
