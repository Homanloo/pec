import { useEffect, useState, type FormEvent } from "react";
import { api, type Phase } from "../api";
import { CompositionTable, DataTable, EosSelect, Errors, PUnitSelect, Quantity, TUnitSelect } from "../components/inputs";
import { hasState, readState, useCalc, writeState } from "../state";
import { fmt, fromKelvin, fromPascal, T_LABEL, type PUnit, type TUnit } from "../units";
import { mixture, NATURAL_GAS } from "./shared";

interface PointResult {
  kind: "bubble" | "dew";
  T: number;
  P: number;
  feed: Phase;
  incipient: Phase;
  K: number[];
}

const DEFAULTS = {
  eos: "PR",
  rows: NATURAL_GAS,
  kind: "bubble" as "bubble" | "dew",
  given: "T" as "T" | "P",
  T: "300",
  Tu: "K" as TUnit,
  P: "30",
  Pu: "bar" as PUnit,
};

export default function Saturation() {
  const [s, setS] = useState(() => readState(DEFAULTS));
  const set = (patch: Partial<typeof DEFAULTS>) => setS({ ...s, ...patch });
  const calc = useCalc<{ r: PointResult; names: string[] }>();

  function submit(e?: FormEvent) {
    e?.preventDefault();
    writeState(s);
    const given = s.given === "T" ? { T: { value: Number(s.T), unit: s.Tu } } : { P: { value: Number(s.P), unit: s.Pu } };
    const body = { ...mixture(s.eos, s.rows), kind: s.kind, ...given };
    calc.run(async () => ({ r: await api<PointResult>("saturation-point/", body), names: body.components }));
  }
  useEffect(() => {
    if (hasState()) submit();
  }, []); // run once when opened from a shared link

  const out = calc.result;
  return (
    <>
      <h1>Saturation points</h1>
      <p className="lead">
        Bubble point: the T or P at which a liquid of this composition forms its first bubble of vapour. Dew point:
        where a vapour forms its first drop of liquid. Give T to find P, or P to find T.
      </p>
      <form className="calc" onSubmit={submit}>
        <EosSelect value={s.eos} onChange={(eos) => set({ eos })} />
        <CompositionTable rows={s.rows} onChange={(rows) => set({ rows })} />
        <div className="row">
          <div className="radio" role="radiogroup" aria-label="point">
            {(["bubble", "dew"] as const).map((k) => (
              <label key={k}>
                <input type="radio" checked={s.kind === k} onChange={() => set({ kind: k })} /> {k === "bubble" ? "Bubble point" : "Dew point"}
              </label>
            ))}
          </div>
          <label>
            Given
            <select value={s.given} onChange={(e) => set({ given: e.target.value as "T" | "P" })}>
              <option value="T">temperature (find P)</option>
              <option value="P">pressure (find T)</option>
            </select>
          </label>
          {s.given === "T" ? (
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
          <button className="primary" disabled={calc.busy}>
            {calc.busy ? "Calculating…" : "Calculate"}
          </button>
        </div>
      </form>
      <Errors messages={calc.error} />
      {out && (
        <section className="result">
          <div className="summary">
            <strong>{out.r.kind === "bubble" ? "Bubble" : "Dew"} point</strong> at{" "}
            <strong>
              {fmt(fromKelvin(out.r.T, s.Tu))} {T_LABEL[s.Tu]}
            </strong>{" "}
            and{" "}
            <strong>
              {fmt(fromPascal(out.r.P, s.Pu))} {s.Pu}
            </strong>
            ; the incipient {out.r.incipient.name} has the composition below.
          </div>
          <DataTable
            name={`${out.r.kind}-point`}
            header={["Component", `Feed (${out.r.feed.name})`, `Incipient ${out.r.incipient.name}`, "K = y/x"]}
            rows={out.names.map((n, i) => [n, fmt(out.r.feed.composition[i]), fmt(out.r.incipient.composition[i]), fmt(out.r.K[i])])}
            json={out.r}
          />
        </section>
      )}
    </>
  );
}
