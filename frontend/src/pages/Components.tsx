import { useState } from "react";
import { DataTable, useComponents } from "../components/inputs";
import { fmt } from "../units";

export default function Components() {
  const all = useComponents();
  const [q, setQ] = useState("");
  const query = q.trim().toLowerCase();
  const shown = all.filter((c) => !query || [c.name, c.formula, c.cas].some((v) => v.toLowerCase().includes(query)));
  return (
    <>
      <h1>Components</h1>
      <p className="lead">
        {all.length} pure components. Critical constants from each fluid's reference equation of state (collected in
        CoolProp); ω by Pitzer's definition from the same equation; every entry confirmed against independent tables.
      </p>
      <input className="search" type="search" placeholder="Search name, formula or CAS number" value={q} onChange={(e) => setQ(e.target.value)} aria-label="search components" />
      <DataTable
        name="components"
        header={["Name", "Formula", "CAS", "M (g/mol)", "Tc (K)", "Pc (bar)", "ω", "Equation of state"]}
        rows={shown.map((c) => [c.name, c.formula, c.cas, fmt(c.molar_mass * 1000), fmt(c.Tc), fmt(c.Pc / 1e5), fmt(c.omega, 4), c.source])}
        json={shown}
      />
    </>
  );
}
