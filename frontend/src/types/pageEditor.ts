/** Page editor types aligned with backend Pydantic models. */

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
}

export interface VariableElement {
  type: "variable";
  id: string;
  x_mm: number;
  y_mm: number;
  width_mm: number;
  height_lines: number;
  var_name: string;
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
