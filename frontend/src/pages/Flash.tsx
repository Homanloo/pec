import { useEffect, useState, type FormEvent } from "react";
import { api, type Phase } from "../api";
import { CompositionTable, DataTable, EosSelect, Errors, Quantity } from "../components/inputs";
import { hasState, readState, useCalc, writeState } from "../state";
import { fmt, fromKelvin, fromPascal, T_LABEL, type PUnit, type TUnit } from "../units";
import { cm3, mixture, NATURAL_GAS } from "./shared";

interface FlashResult {
  T: number;
  P: number;
  phases: Phase[];
  K: number[] | null;
}

const DEFAULTS = { eos: "PR", rows: NATURAL_GAS, T: "300", Tu: "K" as TUnit, P: "30", Pu: "bar" as PUnit };

export default function Flash() {
  const [s, setS] = useState(() => readState(DEFAULTS));
  const set = (patch: Partial<typeof DEFAULTS>) => setS({ ...s, ...patch });
  const calc = useCalc<{ r: FlashResult; names: string[]; z: number[] }>();

  function submit(e?: FormEvent) {
    e?.preventDefault();
    writeState(s);
    const body = { ...mixture(s.eos, s.rows), T: { value: Number(s.T), unit: s.Tu }, P: { value: Number(s.P), unit: s.Pu } };
    const sum = body.z.reduce((a, b) => a + b, 0);
    calc.run(async () => ({ r: await api<FlashResult>("flash/", body), names: body.components, z: body.z.map((v) => v / sum) }));
  }
  useEffect(() => {
    if (hasState()) submit();
  }, []); // run once when opened from a shared link

  const out = calc.result;
  return (
    <>
      <h1>Flash</h1>
      <p className="lead">
        Isothermal (TP) flash: is the feed one phase or two at this T and P, and if two, how much of each and of what
        composition. A stability test decides first, then the phase split is solved.
      </p>
      <form className="calc" onSubmit={submit}>
        <EosSelect value={s.eos} onChange={(eos) => set({ eos })} />
        <CompositionTable rows={s.rows} onChange={(rows) => set({ rows })} />
        <div className="row">
          <Quantity kind="T" label="Temperature" value={s.T} unit={s.Tu} onValue={(T) => set({ T })} onUnit={(Tu) => set({ Tu })} />
          <Quantity kind="P" label="Pressure" value={s.P} unit={s.Pu} onValue={(P) => set({ P })} onUnit={(Pu) => set({ Pu })} />
          <button className="primary" disabled={calc.busy}>
            {calc.busy ? "Calculating…" : "Calculate"}
          </button>
        </div>
      </form>
      <Errors messages={calc.error} />
      {out && <FlashOutput {...out} Tu={s.Tu} Pu={s.Pu} />}
    </>
  );
}

function FlashOutput({ r, names, z, Tu, Pu }: { r: FlashResult; names: string[]; z: number[]; Tu: TUnit; Pu: PUnit }) {
  const at = `${fmt(fromKelvin(r.T, Tu))} ${T_LABEL[Tu]} and ${fmt(fromPascal(r.P, Pu))} ${Pu}`;
  const two = r.phases.length === 2;
  const header = two ? ["Component", "Feed z", "Liquid x", "Vapour y", "K = y/x"] : ["Component", "Mole fraction"];
  const rows = names.map((n, i) =>
    two ? [n, fmt(z[i]), fmt(r.phases[0].composition[i]), fmt(r.phases[1].composition[i]), fmt(r.K![i])] : [n, fmt(z[i])],
  );
  return (
    <section className="result">
      <div className="summary">
        {two ? (
          <>
            <strong>Two phases</strong> at {at}: vapour fraction <strong>{fmt(r.phases[1].fraction, 5)}</strong>.
          </>
        ) : (
          <>
            <strong>One phase</strong> ({r.phases[0].name}-like) at {at}: the feed is stable.
          </>
        )}
      </div>
      <DataTable name="flash" header={header} rows={rows} json={r} />
      <h3>Phases</h3>
      <DataTable
        name="flash-phases"
        header={["Phase", "Mole fraction of feed", "Z", "V (cm³/mol)"]}
        rows={r.phases.map((p) => [p.name, fmt(p.fraction), fmt(p.Z), fmt(cm3(p.V))])}
        json={r.phases}
      />
    </section>
  );
}
