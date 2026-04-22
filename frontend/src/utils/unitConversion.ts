export type Unit = 'mm' | 'cm' | 'in' | 'em' | 'pt';

export type Context = {
  fontSizeMm: number;
};

/**
 * Length constants reference:
 * - 1 mm = 1 mm
 * - 1 cm = 10 mm
 * - 1 in = 25.4 mm (international inch definition)
 * - 1 pt = 1/72 in = 25.4/72 mm
 */
const MM_PER_UNIT = {
  mm: 1,
  cm: 10,
  in: 25.4,
  pt: 25.4 / 72,
} as const;

function requireContext(unit: Unit, ctx?: Context): Context {
  if (unit !== 'em') return { fontSizeMm: 0 };
  if (!ctx || !Number.isFinite(ctx.fontSizeMm) || ctx.fontSizeMm <= 0) {
    throw new Error('Unit conversion for em requires valid context.fontSizeMm');
  }
  return ctx;
}

export function toMm(value: number, unit: Unit, ctx?: Context): number {
  if (unit === 'em') {
    const safeCtx = requireContext(unit, ctx);
    return value * safeCtx.fontSizeMm;
  }
  return value * MM_PER_UNIT[unit];
}

export function fromMm(valueMm: number, unit: Unit, ctx?: Context): number {
  if (unit === 'em') {
    const safeCtx = requireContext(unit, ctx);
    return valueMm / safeCtx.fontSizeMm;
  }
  return valueMm / MM_PER_UNIT[unit];
}

export function convert(value: number, from: Unit, to: Unit, ctx?: Context): number {
  const valueMm = toMm(value, from, ctx);
  return fromMm(valueMm, to, ctx);
}

/**
 * Derived conversion used for font-size context only.
 * 1 pt = 1/72 in = 25.4/72 mm
 */
export function ptToMm(valuePt: number): number {
  return valuePt * MM_PER_UNIT.pt;
}
