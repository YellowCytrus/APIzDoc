import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type {
  Element,
  TextElement,
  VariableElement,
  LineElement,
  Paper,
} from "../types/pageEditor";

const PX_PER_MM = 2;

function generateId(): string {
  return "el-" + Math.random().toString(36).slice(2, 11);
}

function createElement(
  type: "text" | "variable" | "line",
  payload: Partial<TextElement> | Partial<VariableElement> | Partial<LineElement>
): Element {
  const id = generateId();
  if (type === "text") {
    const p = payload as Partial<TextElement>;
    return {
      type: "text",
      id,
      x_mm: p.x_mm ?? 50,
      y_mm: p.y_mm ?? 50,
      content: p.content ?? "Sample Text",
    };
  }
  if (type === "variable") {
    const p = payload as Partial<VariableElement>;
    return {
      type: "variable",
      id,
      x_mm: p.x_mm ?? 50,
      y_mm: p.y_mm ?? 50,
      width_mm: p.width_mm ?? 50,
      height_lines: p.height_lines ?? 2,
      var_name: p.var_name ?? "var",
    };
  }
  const p = payload as Partial<LineElement>;
  return {
    type: "line",
    id,
    x1_mm: p.x1_mm ?? 30,
    y1_mm: p.y1_mm ?? 30,
    x2_mm: p.x2_mm ?? 80,
    y2_mm: p.y2_mm ?? 80,
  };
}

export const usePageEditorStore = defineStore("pageEditor", () => {
  const elements = ref<Element[]>([]);
  const variables = ref<Record<string, string>>({});
  const ignoreDocumentStyles = ref(true);
  const paper = ref<Paper>({
    name: "a4",
    width: 210,
    height: 297,
    margin: 20,
  });
  const selectedId = ref<string | null>(null);
  const showGrid = ref(true);
  const snapEnabled = ref(true);
  const snapThresholdMm = ref(2);

  const selected = computed(() => {
    const id = selectedId.value;
    if (!id) return null;
    return elements.value.find((e) => e.id === id) ?? null;
  });

  function setSelected(id: string | null) {
    selectedId.value = id;
  }

  function setPaper(p: Paper) {
    paper.value = { ...p };
  }

  function addText(x_mm: number, y_mm: number) {
    const el = createElement("text", { x_mm, y_mm });
    elements.value = [...elements.value, el];
    return el;
  }

  function addVariable(x_mm: number, y_mm: number) {
    const el = createElement("variable", { x_mm, y_mm }) as VariableElement;
    elements.value = [...elements.value, el];
    const v = variables.value;
    variables.value = { ...v, [el.var_name ?? "var"]: "" };
    return el;
  }

  function addLine(x1: number, y1: number, x2: number, y2: number) {
    const el = createElement("line", { x1_mm: x1, y1_mm: y1, x2_mm: x2, y2_mm: y2 });
    elements.value = [...elements.value, el];
    return el;
  }

  function updatePosition(id: string, x_mm: number, y_mm: number) {
    elements.value = elements.value.map((e) => {
      if (e.id !== id) return e;
      if (e.type === "line") return e;
      return { ...e, x_mm, y_mm };
    });
  }

  function updateSize(id: string, width_mm: number, height_lines: number) {
    elements.value = elements.value.map((e) => {
      if (e.id !== id || e.type !== "variable") return e;
      return { ...e, width_mm, height_lines };
    });
  }

  function updateLineEndpoints(
    id: string,
    x1_mm: number,
    y1_mm: number,
    x2_mm: number,
    y2_mm: number
  ) {
    elements.value = elements.value.map((e) => {
      if (e.id !== id || e.type !== "line") return e;
      return { ...e, x1_mm, y1_mm, x2_mm, y2_mm };
    });
  }

  function updateTextContent(id: string, content: string) {
    elements.value = elements.value.map((e) => {
      if (e.id !== id || e.type !== "text") return e;
      return { ...e, content };
    });
  }

  function updateTextStyle(id: string, fieldKey: string, value: unknown) {
    elements.value = elements.value.map((e) => {
      if (e.id !== id || (e.type !== "text" && e.type !== "variable")) return e;
      const prev = (e.type === "text" || e.type === "variable") ? e.text_style ?? {} : {};
      const next =
        value === undefined || value === null || value === ""
          ? { ...prev }
          : { ...prev, [fieldKey]: value };
      if (value === undefined || value === null || value === "") {
        delete (next as Record<string, unknown>)[fieldKey];
      }
      const cleaned = Object.fromEntries(
        Object.entries(next).filter(([, v]) => v !== undefined && v !== null && v !== "")
      );
      return { ...e, text_style: Object.keys(cleaned).length ? cleaned : undefined };
    });
  }

  function updateVariableName(id: string, var_name: string) {
    const el = elements.value.find((e) => e.id === id && e.type === "variable");
    if (!el || el.type !== "variable") return;
    const oldName = el.var_name;
    const v = { ...variables.value };
    if (oldName in v) {
      v[var_name] = v[oldName] ?? "";
      delete v[oldName];
    } else {
      v[var_name] = "";
    }
    variables.value = v;
    elements.value = elements.value.map((e) => {
      if (e.id !== id || e.type !== "variable") return e;
      return { ...e, var_name };
    });
  }

  function setVariableValue(varName: string, value: string) {
    variables.value = { ...variables.value, [varName]: value };
  }

  function loadContent(data: {
    elements: Element[];
    paper: { name?: string; width?: number; height?: number; margin?: number };
    variables?: Record<string, string>;
    ignore_document_styles?: boolean;
  }) {
    elements.value = data.elements;
    paper.value = {
      name: data.paper.name ?? "a4",
      width: data.paper.width ?? 210,
      height: data.paper.height ?? 297,
      margin: data.paper.margin ?? 20,
    } as Paper;
    variables.value = data.variables ? { ...data.variables } : {};
    ignoreDocumentStyles.value = data.ignore_document_styles ?? true;
    selectedId.value = null;
  }

  function reset() {
    elements.value = [];
    variables.value = {};
    ignoreDocumentStyles.value = true;
    paper.value = {
      name: "a4",
      width: 210,
      height: 297,
      margin: 20,
    };
    selectedId.value = null;
  }

  function toggleGrid() {
    showGrid.value = !showGrid.value;
  }

  function setSnapEnabled(v: boolean) {
    snapEnabled.value = v;
  }
  function toggleSnap() {
    snapEnabled.value = !snapEnabled.value;
  }
  function setSnapThresholdMm(v: number) {
    snapThresholdMm.value = Math.max(0.5, v);
  }

  return {
    elements,
    variables,
    ignoreDocumentStyles,
    paper,
    selectedId,
    selected,
    showGrid,
    snapEnabled,
    snapThresholdMm,
    PX_PER_MM,
    setSelected,
    setSnapEnabled,
    toggleSnap,
    setSnapThresholdMm,
    setPaper,
    addText,
    addVariable,
    addLine,
    updatePosition,
    updateSize,
    updateLineEndpoints,
    updateTextContent,
    updateTextStyle,
    updateVariableName,
    setVariableValue,
    loadContent,
    reset,
    toggleGrid,
  };
});
