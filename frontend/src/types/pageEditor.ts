/** Page editor types aligned with backend Pydantic models. */

/** Text style for title page elements (text, variable). Mirrors TextOverrideStyles. */
export interface TextStyle {
  font?: string;
  font_size?: number;
  weight?: string;
  style?: string;
  fill?: string;
  tracking?: number;
  word_spacing?: number;
  lang?: string;
  region?: string;
  hyphenate?: boolean | string;
  ligatures?: boolean;
  number_type?: string;
  number_width?: string;
  /** Horizontal alignment for variable elements: left, center, right, justify */
  align?: "left" | "center" | "right" | "justify";
}

export interface Paper {
  name: string;
  width: number;
  height: number;
  margin: number;
}

export interface TextElement {
  type: "text";
  id: string;
  x_mm: number;
  y_mm: number;
  content: string;
  text_style?: TextStyle;
}

export interface VariableElement {
  type: "variable";
  id: string;
  x_mm: number;
  y_mm: number;
  width_mm: number;
  height_lines: number;
  var_name: string;
  text_style?: TextStyle;
}

export interface LineElement {
  type: "line";
  id: string;
  x1_mm: number;
  y1_mm: number;
  x2_mm: number;
  y2_mm: number;
}

export type Element = TextElement | VariableElement | LineElement;

export function isTextElement(e: Element): e is TextElement {
  return e.type === "text";
}
export function isVariableElement(e: Element): e is VariableElement {
  return e.type === "variable";
}
export function isLineElement(e: Element): e is LineElement {
  return e.type === "line";
}

export const PAPER_PRESETS: Record<string, Paper> = {
  a4: { name: "a4", width: 210, height: 297, margin: 20 },
  a3: { name: "a3", width: 297, height: 420, margin: 20 },
  custom: { name: "custom", width: 210, height: 297, margin: 20 },
};
