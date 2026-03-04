export interface VerticalGuide {
  x_mm: number;
  y1_mm: number;
  y2_mm: number;
}
export interface HorizontalGuide {
  y_mm: number;
  x1_mm: number;
  x2_mm: number;
}
export interface ActiveGuides {
  vertical: VerticalGuide[];
  horizontal: HorizontalGuide[];
}

export type GuideShapePoint = { x: number; y: number };
export type GuideShapeBox = { x: number; y: number; w: number; h: number };

const GUIDE_EPSILON = 0.01;

function matches(a: number, b: number, epsilon: number): boolean {
  return Math.abs(a - b) <= epsilon;
}

/** Compute active alignment guides with segment extent (full paper or between elements). */
export function getActiveGuides(
  shape: GuideShapePoint | GuideShapeBox,
  paperWidth: number,
  paperHeight: number,
  otherBounds: { x: number; y: number; w: number; h: number }[],
  epsilon: number = GUIDE_EPSILON
): ActiveGuides {
  const vertical: VerticalGuide[] = [];
  const horizontal: HorizontalGuide[] = [];

  const selfX = "w" in shape ? [shape.x, shape.x + shape.w / 2, shape.x + shape.w] : [shape.x];
  const selfY = "h" in shape ? [shape.y, shape.y + shape.h / 2, shape.y + shape.h] : [shape.y];
  const selfMinY = "h" in shape ? shape.y : shape.y;
  const selfMaxY = "h" in shape ? shape.y + shape.h : shape.y;
  const selfMinX = "w" in shape ? shape.x : shape.x;
  const selfMaxX = "w" in shape ? shape.x + shape.w : shape.x;

  const paperX = [0, paperWidth / 2, paperWidth];
  const paperY = [0, paperHeight / 2, paperHeight];

  for (const x of selfX) {
    if (paperX.some((t) => matches(x, t, epsilon))) {
      vertical.push({ x_mm: x, y1_mm: 0, y2_mm: paperHeight });
      continue;
    }
    for (const b of otherBounds) {
      const tx = [b.x, b.x + b.w / 2, b.x + b.w];
      if (tx.some((t) => matches(x, t, epsilon))) {
        const y1 = Math.min(selfMinY, b.y);
        const y2 = Math.max(selfMaxY, b.y + b.h);
        vertical.push({ x_mm: x, y1_mm: y1, y2_mm: y2 });
        break;
      }
    }
  }

  for (const y of selfY) {
    if (paperY.some((t) => matches(y, t, epsilon))) {
      horizontal.push({ y_mm: y, x1_mm: 0, x2_mm: paperWidth });
      continue;
    }
    for (const b of otherBounds) {
      const ty = [b.y, b.y + b.h / 2, b.y + b.h];
      if (ty.some((t) => matches(y, t, epsilon))) {
        const x1 = Math.min(selfMinX, b.x);
        const x2 = Math.max(selfMaxX, b.x + b.w);
        horizontal.push({ y_mm: y, x1_mm: x1, x2_mm: x2 });
        break;
      }
    }
  }

  return { vertical, horizontal };
}

/** Snap value to nearest target within threshold. */
function snapAxis(value: number, targets: number[], threshold: number): number {
  let best = value;
  let bestDist = threshold + 1;
  for (const t of targets) {
    const d = Math.abs(t - value);
    if (d <= threshold && d < bestDist) {
      bestDist = d;
      best = t;
    }
  }
  return best;
}

export function snapPoint(
  x: number,
  y: number,
  xTargets: number[],
  yTargets: number[],
  threshold: number
): { x_mm: number; y_mm: number } {
  return {
    x_mm: snapAxis(x, xTargets, threshold),
    y_mm: snapAxis(y, yTargets, threshold),
  };
}

/** Snap box by any of 6 points: corners + top/bottom edge centers. Returns top-left (x_mm, y_mm). */
export function snapBox(
  x: number,
  y: number,
  w: number,
  h: number,
  xTargets: number[],
  yTargets: number[],
  threshold: number
): { x_mm: number; y_mm: number } {
  const candX: number[] = [];
  [x, x + w / 2, x + w].forEach((key, i) => {
    const t = snapAxis(key, xTargets, threshold);
    if (t !== key) candX.push(t - [0, w / 2, w][i]!);
  });
  const candY: number[] = [];
  [y, y + h].forEach((key, i) => {
    const t = snapAxis(key, yTargets, threshold);
    if (t !== key) candY.push(t - [0, h][i]!);
  });
  return {
    x_mm: candX.length ? candX.reduce((a, c) => (Math.abs(c - x) < Math.abs(a - x) ? c : a)) : x,
    y_mm: candY.length ? candY.reduce((a, c) => (Math.abs(c - y) < Math.abs(a - y) ? c : a)) : y,
  };
}
