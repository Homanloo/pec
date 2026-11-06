// Unit conversions, the same factors as pec.units (docs/science/units-and-constants.md).
// The API takes {value, unit} and answers in SI; these convert SI results for display.

// T[K] = scale * value + offset
export const T_UNITS = {
  K: [1, 0],
  degC: [1, 273.15],
  degF: [5 / 9, 273.15 - (32 * 5) / 9],
  degR: [5 / 9, 0],
} as const;

// P[Pa] = factor * value
export const P_UNITS = {
  Pa: 1,
  kPa: 1e3,
  MPa: 1e6,
  bar: 1e5,
  atm: 101325,
  psi: (0.45359237 * 9.80665) / 0.0254 ** 2,
  mmHg: 133.322387415,
  torr: 101325 / 760,
} as const;

export type TUnit = keyof typeof T_UNITS;
export type PUnit = keyof typeof P_UNITS;

export const T_LABEL: Record<TUnit, string> = { K: "K", degC: "°C", degF: "°F", degR: "°R" };

export const toKelvin = (v: number, u: TUnit) => T_UNITS[u][0] * v + T_UNITS[u][1];
export const fromKelvin = (v: number, u: TUnit) => (v - T_UNITS[u][1]) / T_UNITS[u][0];
export const toPascal = (v: number, u: PUnit) => P_UNITS[u] * v;
export const fromPascal = (v: number, u: PUnit) => v / P_UNITS[u];

// Numbers for tables: 6 significant digits, no exponent for ordinary magnitudes
export function fmt(v: number | null | undefined, digits = 6): string {
  if (v === null || v === undefined || !Number.isFinite(v)) return "–";
  const a = Math.abs(v);
  if (a !== 0 && (a < 1e-4 || a >= 1e7)) return v.toExponential(digits - 1);
  return Number(v.toPrecision(digits)).toString();
}
