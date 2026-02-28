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

interface DragState {
  id: string;
  kind: "move" | "resize" | "line-end";
  handleIndex?: number;
  startX_mm: number;
  startY_mm: number;
  startMouseX_mm?: number;
  startMouseY_mm?: number;
  startElX_mm?: number;
  startElY_mm?: number;
  startW?: number;
  startH?: number;
  startX1?: number;
  startY1?: number;
  startX2?: number;
  startY2?: number;
  endIndex?: number;
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
    return { x: ve.x_mm, y: ve.y_mm, w: ve.width_mm, h: ve.height_lines * 5 };
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
  const { x, y, w, h } = { x: ve.x_mm, y: ve.y_mm, w: ve.width_mm, h: ve.height_lines * 5 };
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
    if (e.type === "line") {
      const le = e as LineElement;
      if (hit.handleIndex === 0) {
        dragState.value = { id: e.id, kind: "line-end", endIndex: 0, startX_mm: le.x1_mm, startY_mm: le.y1_mm };
      } else if (hit.handleIndex === 1) {
        dragState.value = { id: e.id, kind: "line-end", endIndex: 1, startX_mm: le.x2_mm, startY_mm: le.y2_mm };
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
        startElX_mm: ve.x_mm, startElY_mm: ve.y_mm,
        startW: ve.width_mm, startH: ve.height_lines,
      };
    } else {
      const el = e as TextElement | VariableElement;
      dragState.value = {
        id: e.id, kind: "move",
        startX_mm: el.x_mm,
        startY_mm: el.y_mm,
        startMouseX_mm: mousePaper.x_mm,
        startMouseY_mm: mousePaper.y_mm,
      };
    }
    store.setSelected(e.id);
  } else {
    store.setSelected(null);
  }
}

function onMouseMove(ev: MouseEvent) {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const screenX = ev.clientX - rect.left;
  const screenY = ev.clientY - rect.top;
  if (isPanning.value) {
    movePan(screenX, screenY);
    redraw();
    return;
  }
  const drag = dragState.value;
  if (drag) {
    const { x_mm, y_mm } = screenToPaper(screenX, screenY);
    const snap = snapEnabled.value && !ev.altKey;
    const thresh = snapThresholdMm.value;
    const ctx = canvasRef.value?.getContext("2d") ?? null;
    if (drag.kind === "move") {
      const el = elements.value.find((e) => e.id === drag.id);
      if (!el) return;
      if (el.type === "line") {
        const x1 = (drag.startX1 ?? 0) + (x_mm - drag.startX_mm);
        const y1 = (drag.startY1 ?? 0) + (y_mm - drag.startY_mm);
        const x2 = (drag.startX2 ?? 0) + (x_mm - drag.startX_mm);
        const y2 = (drag.startY2 ?? 0) + (y_mm - drag.startY_mm);
        if (snap) {
          const cx = (x1 + x2) / 2;
          const cy = (y1 + y2) / 2;
          const t = getSnapTargets(drag.id, ctx);
          const c = snapPoint(cx, cy, t.xTargets, t.yTargets, thresh);
          const ox = c.x_mm - cx;
          const oy = c.y_mm - cy;
          store.updateLineEndpoints(drag.id, x1 + ox, y1 + oy, x2 + ox, y2 + oy);
        } else {
          store.updateLineEndpoints(drag.id, x1, y1, x2, y2);
        }
      } else {
        let newX = drag.startX_mm + (x_mm - (drag.startMouseX_mm ?? drag.startX_mm));
        let newY = drag.startY_mm + (y_mm - (drag.startMouseY_mm ?? drag.startY_mm));
        if (snap) {
          const b = getElementBounds(el, ctx);
          const t = getSnapTargets(drag.id, ctx);
          const p = snapBox(newX, newY, b.w, b.h, t.xTargets, t.yTargets, thresh);
          newX = p.x_mm;
          newY = p.y_mm;
        }
        store.updatePosition(drag.id, newX, newY);
      }
    } else if (drag.kind === "resize" && drag.handleIndex != null && drag.startW != null && drag.startH != null && drag.startElX_mm != null && drag.startElY_mm != null) {
      const dx = x_mm - drag.startX_mm;
      const dy = y_mm - drag.startY_mm;
      let w = drag.startW;
      let h = drag.startH;
      let ex = drag.startElX_mm;
      let ey = drag.startElY_mm;
      const hi = drag.handleIndex;
      if (hi === 0) { ex += dx; ey += dy; w = Math.max(10, w - dx); h = Math.max(1, h - dy / 5); }
      else if (hi === 1) { ey += dy; w = Math.max(10, w + dx); h = Math.max(1, h - dy / 5); }
      else if (hi === 2) { w = Math.max(10, w + dx); h = Math.max(1, h + dy / 5); }
      else if (hi === 3) { ex += dx; w = Math.max(10, w - dx); h = Math.max(1, h + dy / 5); }
      else if (hi === 4) { ey += dy; h = Math.max(1, h - dy / 5); }
      else if (hi === 5) { w = Math.max(10, w + dx); }
      else if (hi === 6) { h = Math.max(1, h + dy / 5); }
      else if (hi === 7) { ex += dx; w = Math.max(10, w - dx); }
      store.updatePosition(drag.id, ex, ey);
      store.updateSize(drag.id, w, h);
    } else if (drag.kind === "line-end" && drag.endIndex !== undefined) {
      const le = elements.value.find((e) => e.id === drag.id) as LineElement | undefined;
      if (le) {
        let ex = x_mm;
        let ey = y_mm;
        if (snap) {
          const t = getSnapTargets(drag.id, ctx);
          const p = snapPoint(x_mm, y_mm, t.xTargets, t.yTargets, thresh);
          ex = p.x_mm;
          ey = p.y_mm;
        }
        if (drag.endIndex === 0) store.updateLineEndpoints(drag.id, ex, ey, le.x2_mm, le.y2_mm);
        else store.updateLineEndpoints(drag.id, le.x1_mm, le.y1_mm, ex, ey);
      }
    }
    redraw();
    return;
  }
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
    const h = Math.max(resolved.sizePx * TEXT_LEADING, ve.height_lines * 5 * PX_PER_MM);
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
