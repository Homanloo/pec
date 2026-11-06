import { useEffect, useMemo, useState, type FormEvent } from "react";
import { api } from "../api";
import { Chart } from "../components/Chart";
import { CompositionTable, DataTable, EosSelect, Errors, PUnitSelect, TUnitSelect } from "../components/inputs";
import { hasState, readState, useCalc, writeState } from "../state";
import { fmt, fromKelvin, fromPascal, T_LABEL, type PUnit, type TUnit } from "../units";
import { mixture, NATURAL_GAS } from "./shared";

interface EnvelopeResult {
  bubble: { T: number; P: number }[];
  dew: { T: number; P: number }[];
}

const DEFAULTS = { eos: "PR", rows: NATURAL_GAS, points: "40", Tu: "K" as TUnit, Pu: "bar" as PUnit };

export default function Envelope() {
  const [s, setS] = useState(() => readState(DEFAULTS));
  const set = (patch: Partial<typeof DEFAULTS>) => setS({ ...s, ...patch });
  const calc = useCalc<EnvelopeResult>();

  function submit(e?: FormEvent) {
    e?.preventDefault();
    writeState(s);
    calc.run(() => api<EnvelopeResult>("envelope/", { ...mixture(s.eos, s.rows), points: Number(s.points) }));
  }
  useEffect(() => {
    if (hasState()) submit();
  }, []); // run once when opened from a shared link

  const r = calc.result;
  const traces = useMemo(
    () =>
      r
        ? [
            { name: "Bubble curve", x: r.bubble.map((p) => fromKelvin(p.T, s.Tu)), y: r.bubble.map((p) => fromPascal(p.P, s.Pu)), color: "--brand" },
            { name: "Dew curve", x: r.dew.map((p) => fromKelvin(p.T, s.Tu)), y: r.dew.map((p) => fromPascal(p.P, s.Pu)), color: "--series-2" },
          ]
        : [],
    [r, s.Tu, s.Pu],
  );
  const rows = r
    ? [
        ...r.bubble.map((p) => ["bubble", fmt(fromKelvin(p.T, s.Tu)), fmt(fromPascal(p.P, s.Pu))]),
        ...r.dew.map((p) => ["dew", fmt(fromKelvin(p.T, s.Tu)), fmt(fromPascal(p.P, s.Pu))]),
      ]
    : [];
  return (
    <>
      <h1>Phase envelope</h1>
      <p className="lead">
        The P-T envelope of a mixture: the bubble curve (first vapour) and the dew curve (first liquid). Inside, the
        mixture splits into two phases.
      </p>
      <form className="calc" onSubmit={submit}>
        <EosSelect value={s.eos} onChange={(eos) => set({ eos })} />
        <CompositionTable rows={s.rows} onChange={(rows) => set({ rows })} />
        <div className="row">
          <label>
            Points per curve
            <input type="number" min="5" max="200" step="1" value={s.points} onChange={(e) => set({ points: e.target.value })} />
          </label>
          <label>
            Units
            <span className="quantity">
              <TUnitSelect value={s.Tu} onChange={(Tu) => set({ Tu })} />
              <PUnitSelect value={s.Pu} onChange={(Pu) => set({ Pu })} />
            </span>
          </label>
          <button className="primary" disabled={calc.busy}>
            {calc.busy ? "Calculating…" : "Calculate"}
          </button>
        </div>
      </form>
      <Errors messages={calc.error} />
      {r && (
        <section className="result">
          <Chart traces={traces} xTitle={`T (${T_LABEL[s.Tu]})`} yTitle={`P (${s.Pu})`} />
          <p className="note">
            Version 1: each curve is a sweep of bubble or dew temperatures over pressure, so it stops short of the
            critical point, where the two curves meet. Tracing through the critical point comes in a later version.
          </p>
          <DataTable name="envelope" header={["Curve", `T (${T_LABEL[s.Tu]})`, `P (${s.Pu})`]} rows={rows} json={r} />
        </section>
      )}
    </>
  );
}
