import { useEffect, useMemo, useState, type FormEvent } from "react";
import { api } from "../api";
import { Chart } from "../components/Chart";
import { ComponentInput, ComponentList, DataTable, EosSelect, Errors, PUnitSelect, Quantity, TUnitSelect } from "../components/inputs";
import { hasState, readState, useCalc, writeState } from "../state";
import { fmt, fromKelvin, fromPascal, T_LABEL, type PUnit, type TUnit } from "../units";

interface BinaryResult {
  kind: "Pxy" | "Txy";
  points: { x: number; y: number; T: number; P: number }[];
  failed: number[];
}

const DEFAULTS = {
  eos: "PR",
  c1: "Ethane",
  c2: "n-Propane",
  kind: "Pxy" as "Pxy" | "Txy",
  T: "250",
  Tu: "K" as TUnit,
  P: "1",
  Pu: "bar" as PUnit,
  k12: "0",
  points: "41",
};

export default function Binary() {
  const [s, setS] = useState(() => readState(DEFAULTS));
  const set = (patch: Partial<typeof DEFAULTS>) => setS({ ...s, ...patch });
  const calc = useCalc<{ r: BinaryResult; s: typeof DEFAULTS }>();

  function submit(e?: FormEvent) {
    e?.preventDefault();
    writeState(s);
    const k = Number(s.k12) || 0;
    const fixed = s.kind === "Pxy" ? { T: { value: Number(s.T), unit: s.Tu } } : { P: { value: Number(s.P), unit: s.Pu } };
    const body = {
      eos: s.eos,
      components: [s.c1.trim(), s.c2.trim()],
      kind: s.kind,
      points: Number(s.points),
      ...(k ? { kij: [[0, k], [k, 0]] } : {}),
      ...fixed,
    };
    const snapshot = { ...s };
    calc.run(async () => ({ r: await api<BinaryResult>("binary/", body), s: snapshot }));
  }
  useEffect(() => {
    if (hasState()) submit();
  }, []); // run once when opened from a shared link

  return (
    <>
      <h1>Binary diagrams</h1>
      <p className="lead">
        P-x-y at a fixed temperature or T-x-y at a fixed pressure for a two-component mixture: the bubble curve (liquid
        x₁) and the dew curve (vapour y₁).
      </p>
      <form className="calc" onSubmit={submit}>
        <EosSelect value={s.eos} onChange={(eos) => set({ eos })} />
        <ComponentList id="component-names" />
        <div className="row">
          <ComponentInput label="Component 1 (x₁, y₁)" value={s.c1} onChange={(c1) => set({ c1 })} />
          <ComponentInput label="Component 2" value={s.c2} onChange={(c2) => set({ c2 })} />
          <label>
            k₁₂
            <input type="number" step="any" value={s.k12} onChange={(e) => set({ k12: e.target.value })} />
          </label>
        </div>
        <div className="row">
          <label>
            Diagram
            <select value={s.kind} onChange={(e) => set({ kind: e.target.value as "Pxy" | "Txy" })}>
              <option value="Pxy">P-x-y (fixed T)</option>
              <option value="Txy">T-x-y (fixed P)</option>
            </select>
          </label>
          {s.kind === "Pxy" ? (
            <>
              <Quantity kind="T" label="Temperature" value={s.T} unit={s.Tu} onValue={(T) => set({ T })} onUnit={(Tu) => set({ Tu })} />
              <label>
                Pressure unit
                <PUnitSelect value={s.Pu} onChange={(Pu) => set({ Pu })} />
              </label>
            </>
          ) : (
            <>
              <Quantity kind="P" label="Pressure" value={s.P} unit={s.Pu} onValue={(P) => set({ P })} onUnit={(Pu) => set({ Pu })} />
              <label>
                Temperature unit
                <TUnitSelect value={s.Tu} onChange={(Tu) => set({ Tu })} />
              </label>
            </>
          )}
          <label>
            Points
            <input type="number" min="3" max="200" step="1" value={s.points} onChange={(e) => set({ points: e.target.value })} />
          </label>
          <button className="primary" disabled={calc.busy}>
            {calc.busy ? "Calculating…" : "Calculate"}
          </button>
        </div>
      </form>
      <Errors messages={calc.error} />
      {calc.result && <BinaryOutput {...calc.result} />}
    </>
  );
}

function BinaryOutput({ r, s }: { r: BinaryResult; s: typeof DEFAULTS }) {
  const Pxy = r.kind === "Pxy";
  const value = (p: { T: number; P: number }) => (Pxy ? fromPascal(p.P, s.Pu) : fromKelvin(p.T, s.Tu));
  const unit = Pxy ? s.Pu : T_LABEL[s.Tu];
  const traces = useMemo(
    () => [
      { name: "Bubble curve (liquid x₁)", x: r.points.map((p) => p.x), y: r.points.map(value), color: "--brand" },
      { name: "Dew curve (vapour y₁)", x: r.points.map((p) => p.y), y: r.points.map(value), color: "--series-2" },
    ],
    [r, s], // the result and the units it was asked in
  );
  return (
    <section className="result">
      {r.points.length === 0 ? (
        <div className="error">No point converged: check that the mixture has two phases here.</div>
      ) : (
        <Chart traces={traces} xTitle={`x₁, y₁ (${s.c1})`} yTitle={`${Pxy ? "P" : "T"} (${unit})`} />
      )}
      {r.failed.length > 0 && (
        <p className="note">
          No solution at x₁ = {r.failed.map((x) => fmt(x, 3)).join(", ")} (for example above a component's critical
          temperature, or beyond the mixture critical point).
        </p>
      )}
      <DataTable
        name={`${r.kind}-${s.c1}-${s.c2}`}
        header={["x₁", "y₁", `${Pxy ? "P" : "T"} (${unit})`]}
        rows={r.points.map((p) => [fmt(p.x), fmt(p.y), fmt(value(p))])}
        json={r}
      />
    </section>
  );
}
