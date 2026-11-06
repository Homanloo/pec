import { useEffect, useMemo, useState, type FormEvent } from "react";
import { api } from "../api";
import { Chart, type Trace } from "../components/Chart";
import { ComponentInput, ComponentList, DataTable, EosSelect, Errors, PUnitSelect, TUnitSelect } from "../components/inputs";
import { hasState, readState, useCalc, writeState } from "../state";
import { fmt, fromKelvin, fromPascal, T_LABEL, toKelvin, type PUnit, type TUnit } from "../units";
import { cm3 } from "./shared";

interface Curve {
  Tc: number;
  Pc: number;
  Vc: number;
  points: { T: number; P: number; V_liquid: number; V_vapour: number }[];
}
interface Isotherms {
  isotherms: { T: number; V: number[]; P: number[]; saturation?: { P: number; V_liquid: number; V_vapour: number } }[];
}

const DEFAULTS = { eos: "PR", component: "Methane", temps: "", Tu: "K" as TUnit, Pu: "bar" as PUnit, logP: true };
// Isotherms around the critical point when none are given: 0.8, 0.9, 1.0 and 1.1 Tc
const AUTO = [0.8, 0.9, 1.0, 1.1];

export default function Pure() {
  const [s, setS] = useState(() => readState(DEFAULTS));
  const set = (patch: Partial<typeof DEFAULTS>) => setS({ ...s, ...patch });
  const calc = useCalc<{ curve: Curve; iso: Isotherms; s: typeof DEFAULTS }>();

  function submit(e?: FormEvent) {
    e?.preventDefault();
    writeState(s);
    const base = { eos: s.eos, component: s.component.trim() };
    const snapshot = { ...s };
    calc.run(async () => {
      const curve = await api<Curve>("pure/curve/", base);
      const given = s.temps.split(/[,\s]+/).filter(Boolean).map(Number);
      const temperatures = given.length ? given.map((t) => toKelvin(t, s.Tu)) : AUTO.map((f) => f * curve.Tc);
      const iso = await api<Isotherms>("pure/isotherms/", { ...base, temperatures });
      return { curve, iso, s: snapshot };
    });
  }
  useEffect(() => {
    if (hasState()) submit();
  }, []); // run once when opened from a shared link

  return (
    <>
      <h1>Pure component</h1>
      <p className="lead">
        Vapour pressure from the equation of state, from 0.45 Tc up to the critical point, and P-V isotherms with the
        saturation dome.
      </p>
      <form className="calc" onSubmit={submit}>
        <EosSelect value={s.eos} onChange={(eos) => set({ eos })} />
        <ComponentList id="component-names" />
        <div className="row">
          <ComponentInput label="Component" value={s.component} onChange={(component) => set({ component })} />
          <label>
            Isotherms ({T_LABEL[s.Tu]}, comma-separated; empty: 0.8–1.1 Tc)
            <input value={s.temps} onChange={(e) => set({ temps: e.target.value })} placeholder="e.g. 150, 170, 190" />
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
      {calc.result && <PureOutput {...calc.result} logP={s.logP} setLogP={(logP) => set({ logP })} />}
    </>
  );
}

function PureOutput({ curve, iso, s, logP, setLogP }: { curve: Curve; iso: Isotherms; s: typeof DEFAULTS; logP: boolean; setLogP: (v: boolean) => void }) {
  const T = (v: number) => fromKelvin(v, s.Tu);
  const P = (v: number) => fromPascal(v, s.Pu);
  const psat = useMemo<Trace[]>(
    () => [{ name: "Vapour pressure", x: curve.points.map((p) => T(p.T)), y: curve.points.map((p) => P(p.P)), color: "--brand" }],
    [curve, s], // the result and the units it was asked in
  );
  const pv = useMemo<Trace[]>(() => {
    // The dome: saturated liquid volumes up to Vc, then saturated vapour volumes back down
    const dome = [...curve.points, ...curve.points.slice().reverse()];
    const half = curve.points.length;
    const traces: Trace[] = [
      {
        name: "Saturation dome",
        x: dome.map((p, i) => cm3(i < half ? p.V_liquid : p.V_vapour)),
        y: dome.map((p) => P(p.P)),
        color: "--text",
        dash: "dot",
      },
    ];
    iso.isotherms.forEach((it, i) => {
      // Isotherm colours: from the brand blue (coldest) to orange (hottest), readable in both themes
      const shade = `hsl(${202 - (180 * i) / Math.max(1, iso.isotherms.length - 1)}, 85%, 52%)`;
      traces.push({ name: `${fmt(T(it.T), 4)} ${T_LABEL[s.Tu]}`, x: it.V.map(cm3), y: it.P.map(P), color: shade });
    });
    return traces;
  }, [curve, iso, s]);
  const yRange = useMemo<[number, number]>(() => [-0.5 * P(curve.Pc), 2 * P(curve.Pc)], [curve, s]);
  // V axis: the isotherms' own range (the dome's vapour side runs much further at low T)
  const V = iso.isotherms[0].V;
  const xRange = useMemo<[number, number]>(() => [Math.log10(cm3(V[0])), Math.log10(cm3(V[V.length - 1]))], [V]);

  return (
    <section className="result">
      <div className="summary">
        Critical point (input data): Tc = <strong>{fmt(T(curve.Tc))} {T_LABEL[s.Tu]}</strong>, Pc ={" "}
        <strong>
          {fmt(P(curve.Pc))} {s.Pu}
        </strong>
        ; the equation of state gives Vc = <strong>{fmt(cm3(curve.Vc))} cm³/mol</strong>.
      </div>
      <h2>Vapour pressure</h2>
      <label className="check">
        <input type="checkbox" checked={logP} onChange={(e) => setLogP(e.target.checked)} /> logarithmic pressure axis
      </label>
      <Chart traces={psat} xTitle={`T (${T_LABEL[s.Tu]})`} yTitle={`Pˢᵃᵗ (${s.Pu})`} yLog={logP} />
      <h2>P-V isotherms</h2>
      <Chart traces={pv} xTitle="V (cm³/mol)" yTitle={`P (${s.Pu})`} xLog xRange={xRange} yRange={yRange} />
      <p className="note">
        Below Tc each isotherm has the cubic's van der Waals loop inside the dome; the real fluid follows the horizontal
        line at Pˢᵃᵗ between the liquid and vapour volumes.
      </p>
      <h3>Saturation table</h3>
      <DataTable
        name={`saturation-${s.component}`}
        header={[`T (${T_LABEL[s.Tu]})`, `Pˢᵃᵗ (${s.Pu})`, "V liquid (cm³/mol)", "V vapour (cm³/mol)"]}
        rows={curve.points.map((p) => [fmt(T(p.T)), fmt(P(p.P)), fmt(cm3(p.V_liquid)), fmt(cm3(p.V_vapour))])}
        json={curve}
      />
    </section>
  );
}
