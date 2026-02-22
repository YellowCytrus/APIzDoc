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

const PX_PER_MM = 2;
const TEXT_SIZE_PT = 12;
const VARIABLE_FONT_SIZE_PT = 10;
const TEXT_LEADING = 1.2;
const TEXT_FILL = "#000000";
const VARIABLE_BOX_FILL = "#fafafa";

function ptToPx(pt: number): number {
  return pt * (25.4 / 72) * PX_PER_MM;
}
const TEXT_SIZE_PX = ptToPx(TEXT_SIZE_PT);
const VARIABLE_FONT_SIZE_PX = ptToPx(VARIABLE_FONT_SIZE_PT);

const WEIGHT_TO_CSS: Record<string, number | string> = {
  thin: 100,
  extralight: 200,
  light: 300,
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
  extrabold: 800,
  black: 900,
};

function fillToCss(fill: string | undefined): string {
  if (!fill || !String(fill).trim()) return TEXT_FILL;
  const s = String(fill).trim();
  const lower = s.toLowerCase();
  if (lower === "black") return "#000000";
  if (lower === "white") return "#ffffff";
  const rgbMatch = s.match(/rgb\s*\(\s*["']?#?([0-9a-fA-F]{3,6})["']?\s*\)/i);
  if (rgbMatch?.[1]) {
    const hex = rgbMatch[1];
    return hex.length === 3 ? `#${hex[0]}${hex[0]}${hex[1]}${hex[1]}${hex[2]}${hex[2]}` : `#${hex}`;
  }
  if (s.startsWith("#") && /^#[0-9a-fA-F]{3,8}$/.test(s)) return s;
  if (s.startsWith("rgb(")) return s;
  return s;
}

function resolveTextStyle(
  text_style: Record<string, unknown> | undefined,
  defaultSizePt: number
): { sizePx: number; font: string; fill: string; weight: string; style: string } {
  const ts = text_style ?? {};
  const sizePt = (ts.font_size as number) ?? defaultSizePt;
  const font = (ts.font as string) || "Libertinus Serif";
  const fill = fillToCss(ts.fill as string);
  const weight = (ts.weight as string) ?? "regular";
  const style = (ts.style as string) ?? "normal";
  const fontFamily = font.toLowerCase().includes('libertinus')
    ? `"Libertinus Serif", serif`
    : `${font}, sans-serif`;
  return {
    sizePx: ptToPx(sizePt),
    font: fontFamily,
    fill,
    weight: String(WEIGHT_TO_CSS[weight] ?? weight),
    style,
  };
}

function buildCanvasFont(resolved: { sizePx: number; font: string; weight: string; style: string }): string {
  const parts: string[] = [];
  if (resolved.style && resolved.style !== "normal") parts.push(resolved.style);
  if (resolved.weight && resolved.weight !== "400") parts.push(String(resolved.weight));
  parts.push(`${resolved.sizePx}px`);
  parts.push(resolved.font);
  return parts.join(" ");
}

const store = usePageEditorStore();
const { elements, paper, selectedId, showGrid } = storeToRefs(store);

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

function getElementBounds(e: Element): { x: number; y: number; w: number; h: number } {
  if (e.type === "text") {
    const te = e as TextElement;
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
    if (drag.kind === "move") {
      const el = elements.value.find((e) => e.id === drag.id);
      if (!el) return;
      if (el.type === "line") {
        const dx = x_mm - drag.startX_mm;
        const dy = y_mm - drag.startY_mm;
        store.updateLineEndpoints(
          drag.id,
          (drag.startX1 ?? 0) + dx,
          (drag.startY1 ?? 0) + dy,
          (drag.startX2 ?? 0) + dx,
          (drag.startY2 ?? 0) + dy
        );
      } else {
        const newX = drag.startX_mm + (x_mm - (drag.startMouseX_mm ?? drag.startX_mm));
        const newY = drag.startY_mm + (y_mm - (drag.startMouseY_mm ?? drag.startY_mm));
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
        if (drag.endIndex === 0) store.updateLineEndpoints(drag.id, x_mm, y_mm, le.x2_mm, le.y2_mm);
        else store.updateLineEndpoints(drag.id, le.x1_mm, le.y1_mm, x_mm, y_mm);
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
      const m = ctx.measureText(te.content);
      ctx.strokeStyle = "#3b82f6";
      ctx.lineWidth = 2 / s;
      const lineH = resolved.sizePx * TEXT_LEADING;
      ctx.strokeRect(x, y, m.width + 4, lineH);
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
