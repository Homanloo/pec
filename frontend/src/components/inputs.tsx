import { useEffect, useState } from "react";
import { loadComponents, MODELS, type Component } from "../api";
import { download, toCsv } from "../state";
import { P_UNITS, T_LABEL, T_UNITS, type PUnit, type TUnit } from "../units";

export function EosSelect({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <label>
      Equation of state
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {MODELS.map(([name, title]) => (
          <option key={name} value={name}>
            {title}
          </option>
        ))}
      </select>
    </label>
  );
}

export function TUnitSelect({ value, onChange }: { value: TUnit; onChange: (u: TUnit) => void }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value as TUnit)} aria-label="temperature unit">
      {(Object.keys(T_UNITS) as TUnit[]).map((u) => (
        <option key={u} value={u}>
          {T_LABEL[u]}
        </option>
      ))}
    </select>
  );
}

export function PUnitSelect({ value, onChange }: { value: PUnit; onChange: (u: PUnit) => void }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value as PUnit)} aria-label="pressure unit">
      {(Object.keys(P_UNITS) as PUnit[]).map((u) => (
        <option key={u} value={u}>
          {u}
        </option>
      ))}
    </select>
  );
}

// A number plus its unit, e.g. temperature 25 °C
export function Quantity<U extends string>(props: {
  label: string;
  value: string;
  unit: U;
  onValue: (v: string) => void;
  onUnit: (u: U) => void;
  kind: "T" | "P";
}) {
  return (
    <label>
      {props.label}
      <span className="quantity">
        <input type="number" step="any" required value={props.value} onChange={(e) => props.onValue(e.target.value)} />
        {props.kind === "T" ? (
          <TUnitSelect value={props.unit as TUnit} onChange={(u) => props.onUnit(u as U)} />
        ) : (
          <PUnitSelect value={props.unit as PUnit} onChange={(u) => props.onUnit(u as U)} />
        )}
      </span>
    </label>
  );
}

// All component names, for the searchable pickers (one <datalist> per page)
export function useComponents(): Component[] {
  const [list, setList] = useState<Component[]>([]);
  useEffect(() => {
    loadComponents().then(setList, () => setList([]));
  }, []);
  return list;
}

export function ComponentList({ id }: { id: string }) {
  const list = useComponents();
  return (
    <datalist id={id}>
      {list.map((c) => (
        <option key={c.name} value={c.name}>
          {c.formula}
        </option>
      ))}
    </datalist>
  );
}

export function ComponentInput(props: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label>
      {props.label}
      <input className="name" list="component-names" required value={props.value} onChange={(e) => props.onChange(e.target.value)} placeholder="e.g. Methane" />
    </label>
  );
}

export interface Row {
  name: string;
  z: string;
}

// Components and mole fractions; the API normalises z, the button does it in place.
export function CompositionTable({ rows, onChange }: { rows: Row[]; onChange: (rows: Row[]) => void }) {
  const sum = rows.reduce((s, r) => s + (Number(r.z) || 0), 0);
  const set = (i: number, patch: Partial<Row>) => onChange(rows.map((r, j) => (j === i ? { ...r, ...patch } : r)));
  const normalise = () =>
    sum > 0 && onChange(rows.map((r) => ({ ...r, z: String(Number(((Number(r.z) || 0) / sum).toPrecision(6))) })));
  return (
    <div>
      <ComponentList id="component-names" />
      <table className="composition">
        <thead>
          <tr>
            <th>Component</th>
            <th>Mole fraction</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              <td>
                <input className="name" list="component-names" required value={r.name} aria-label="component" onChange={(e) => set(i, { name: e.target.value })} />
              </td>
              <td>
                <input type="number" step="any" min="0" required value={r.z} aria-label="mole fraction" onChange={(e) => set(i, { z: e.target.value })} />
              </td>
              <td>
                {rows.length > 1 && (
                  <button type="button" className="link" title="Remove" onClick={() => onChange(rows.filter((_, j) => j !== i))}>
                    ✕
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td>
              <button type="button" className="secondary" onClick={() => onChange([...rows, { name: "", z: "0" }])}>
                + Add component
              </button>
            </td>
            <td>
              <span className={Math.abs(sum - 1) > 1e-9 ? "sum off" : "sum"}>Σ = {Number(sum.toPrecision(6))}</span>{" "}
              <button type="button" className="secondary" onClick={normalise}>
                Normalise
              </button>
            </td>
            <td />
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

export function Errors({ messages }: { messages: string[] | null }) {
  if (!messages) return null;
  return (
    <div className="error" role="alert">
      {messages.length === 1 ? messages[0] : <ul>{messages.map((m, i) => <li key={i}>{m}</li>)}</ul>}
    </div>
  );
}

// A results table with CSV and JSON downloads of exactly what it shows
export function DataTable({ name, header, rows, json }: { name: string; header: string[]; rows: (string | number)[][]; json: unknown }) {
  return (
    <>
      <div className="actions">
        <button type="button" className="secondary" onClick={() => download(`${name}.csv`, toCsv(header, rows), "text/csv")}>
          CSV
        </button>
        <button type="button" className="secondary" onClick={() => download(`${name}.json`, JSON.stringify(json, null, 2), "application/json")}>
          JSON
        </button>
      </div>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              {header.map((h) => (
                <th key={h}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i}>
                {r.map((v, j) => (
                  <td key={j}>{v}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
