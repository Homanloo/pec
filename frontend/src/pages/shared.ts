import type { Row } from "../components/inputs";

// A C1–C5 natural-gas liquid: two phases at room temperature and 30 bar
export const NATURAL_GAS: Row[] = [
  { name: "Methane", z: "0.4" },
  { name: "Ethane", z: "0.2" },
  { name: "n-Propane", z: "0.15" },
  { name: "n-Butane", z: "0.15" },
  { name: "n-Pentane", z: "0.1" },
];

export function mixture(eos: string, rows: Row[]) {
  return { eos, components: rows.map((r) => r.name.trim()), z: rows.map((r) => Number(r.z)) };
}

export const cm3 = (V: number) => V * 1e6; // m³/mol → cm³/mol for display
