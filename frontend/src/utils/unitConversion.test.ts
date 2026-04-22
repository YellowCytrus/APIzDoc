import { describe, expect, it } from 'vitest';
import { convert, fromMm, toMm } from './unitConversion';

describe('unitConversion', () => {
  it('converts between mm, cm and in through mm', () => {
    expect(toMm(1, 'cm')).toBe(10);
    expect(toMm(1, 'in')).toBe(25.4);
    expect(fromMm(25.4, 'in')).toBe(1);
  });

  it('converts em with context and rejects missing context', () => {
    expect(toMm(2, 'em', { fontSizeMm: 3 })).toBe(6);
    expect(fromMm(6, 'em', { fontSizeMm: 3 })).toBe(2);
    expect(() => toMm(1, 'em')).toThrow();
  });

  it('is stable across repeated mm-centered switching', () => {
    const startMm = 37.777;
    const inInches = convert(startMm, 'mm', 'in');
    const inCm = convert(inInches, 'in', 'cm');
    const roundTripMm = convert(inCm, 'cm', 'mm');
    expect(roundTripMm).toBeCloseTo(startMm, 12);
  });
});
