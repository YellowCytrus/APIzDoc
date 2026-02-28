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
    if (t !== key) candX.push(t - [0, w / 2, w][i]);
  });
  const candY: number[] = [];
  [y, y + h].forEach((key, i) => {
    const t = snapAxis(key, yTargets, threshold);
    if (t !== key) candY.push(t - [0, h][i]);
  });
  return {
    x_mm: candX.length ? candX.reduce((a, c) => (Math.abs(c - x) < Math.abs(a - x) ? c : a)) : x,
    y_mm: candY.length ? candY.reduce((a, c) => (Math.abs(c - y) < Math.abs(a - y) ? c : a)) : y,
  };
}
