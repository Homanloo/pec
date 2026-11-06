const EXAMPLE = `curl -X POST https://<this site>/api/v1/flash/ \\
  -H "Content-Type: application/json" \\
  -d '{"eos": "PR",
       "components": ["Methane", "Ethane", "n-Propane", "n-Butane", "n-Pentane"],
       "z": [0.4, 0.2, 0.15, 0.15, 0.1],
       "T": {"value": 26.85, "unit": "degC"},
       "P": {"value": 30, "unit": "bar"}}'`;

const ENDPOINTS: [string, string, string][] = [
  ["GET", "components/", "All components; components/<name>/ for one"],
  ["GET", "models/", "Equations of state"],
  ["POST", "flash/", "TP flash: one or two phases"],
  ["POST", "saturation-point/", "Bubble or dew point, in T or P"],
  ["POST", "binary/", "P-x-y or T-x-y diagram of a binary"],
  ["POST", "envelope/", "P-T phase envelope (bubble and dew curves)"],
  ["POST", "pure/curve/", "Vapour pressure and saturated volumes"],
  ["POST", "pure/isotherms/", "P-V isotherms"],
  ["GET", "health/", "Service status and version"],
];

export default function Developers() {
  return (
    <>
      <h1>API</h1>
      <p className="lead">
        Everything this site calculates is available as a JSON API under <code>/api/v1/</code>, open and free. The
        interactive documentation has the full schema and a working example for every endpoint.
      </p>
      <p>
        <a href="/api/docs/">Open the interactive API documentation →</a>
      </p>
      <h2>Conventions</h2>
      <ul>
        <li>
          Temperatures and pressures: a number in SI (K, Pa) or <code>{'{"value": 25, "unit": "degC"}'}</code>. Units: K,
          degC, degF, degR; Pa, kPa, MPa, bar, atm, psi, mmHg, torr.
        </li>
        <li>Results are in SI: K, Pa, m³/mol. Mole fractions are normalised for you; each must be positive.</li>
        <li>
          <code>eos</code>: PR (default), SRK, RK or vdW. <code>kij</code>: optional symmetric matrix of binary
          interaction parameters.
        </li>
        <li>
          Errors: <b>400</b> invalid input (a message per field), <b>404</b> unknown component, <b>422</b> no solution
          or no convergence (the message says why).
        </li>
        <li>Limits: up to 10 components and 200 points per request; sweeps stop after 10 s.</li>
      </ul>
      <h2>Endpoints</h2>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Method</th>
              <th style={{ textAlign: "left" }}>Path</th>
              <th style={{ textAlign: "left" }}>What</th>
            </tr>
          </thead>
          <tbody>
            {ENDPOINTS.map(([m, path, what]) => (
              <tr key={path}>
                <td>{m}</td>
                <td style={{ textAlign: "left" }}>
                  <code>/api/v1/{path}</code>
                </td>
                <td style={{ textAlign: "left" }}>{what}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h2>Example</h2>
      <pre>{EXAMPLE}</pre>
      <p>
        The science core is also a Python library, <code>pec</code> (numpy and scipy only), for use in your own scripts.
      </p>
    </>
  );
}
