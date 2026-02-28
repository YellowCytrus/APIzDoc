import type { TextElement } from "../types/pageEditor";

export const PX_PER_MM = 2;
export const TEXT_SIZE_PT = 12;
export const TEXT_LEADING = 1.2;
const TEXT_FILL = "#000000";

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

export function ptToPx(pt: number): number {
  return pt * (25.4 / 72) * PX_PER_MM;
}

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

export function resolveTextStyle(
  text_style: Record<string, unknown> | undefined,
  defaultSizePt: number
): { sizePx: number; font: string; fill: string; weight: string; style: string } {
  const ts = text_style ?? {};
  const sizePt = (ts.font_size as number) ?? defaultSizePt;
  const font = (ts.font as string) || "Libertinus Serif";
  const fill = fillToCss(ts.fill as string);
  const weight = (ts.weight as string) ?? "regular";
  const style = (ts.style as string) ?? "normal";
  const fontFamily = font.toLowerCase().includes("libertinus")
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

export function buildCanvasFont(resolved: {
  sizePx: number;
  font: string;
  weight: string;
  style: string;
}): string {
  const parts: string[] = [];
  if (resolved.style && resolved.style !== "normal") parts.push(resolved.style);
  if (resolved.weight && resolved.weight !== "400") parts.push(String(resolved.weight));
  parts.push(`${resolved.sizePx}px`);
  parts.push(resolved.font);
  return parts.join(" ");
}

/** Text element bounds in mm (same as blue selection rect: measureText + 4px padding). */
export function getTextBoundsMm(
  te: TextElement,
  ctx: CanvasRenderingContext2D
): { w: number; h: number } {
  const resolved = resolveTextStyle(
    te.text_style as Record<string, unknown> | undefined,
    TEXT_SIZE_PT
  );
  ctx.font = buildCanvasFont(resolved);
  const m = ctx.measureText(te.content);
  return {
    w: (m.width + 4) / PX_PER_MM,
    h: (resolved.sizePx * TEXT_LEADING) / PX_PER_MM,
  };
}
