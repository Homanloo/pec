import { Link } from "../router";

const LINKS: [string, string, string][] = [
  ["/flash", "Flash", "One phase or two at given T and P"],
  ["/saturation", "Saturation points", "Bubble and dew points in T or P"],
  ["/binary", "Binary diagrams", "P-x-y and T-x-y"],
  ["/envelope", "Phase envelope", "P-T bubble and dew curves"],
  ["/pure", "Pure component", "Vapour pressure and P-V isotherms"],
  ["/components", "Components", "The data behind every calculation"],
  ["/theory", "Theory", "Equations, methods and references"],
  ["/developers", "API", "The same calculations as JSON"],
];

export default function Home() {
  return (
    <div className="home">
      <nav className="home-hub" aria-label="calculators">
        <h3>Links</h3>
        <ul>
          {LINKS.map(([to, title, what]) => (
            <li key={to}>
              <Link to={to}>{title}</Link>
              <small>{what}</small>
            </li>
          ))}
        </ul>
      </nav>
      <div className="home-text">
        <h1>Phase Equilibrium Calculator</h1>
        <p>
          PEC calculates the vapour–liquid equilibrium of multi-component mixtures with cubic equations of state:
          Peng–Robinson, Soave–Redlich–Kwong, Redlich–Kwong and van der Waals. Flash a mixture at given temperature and
          pressure, find its bubble and dew points, draw binary and P-T phase diagrams, or look at a pure component's
          vapour pressure and isotherms.
        </p>
        <p>
          Every method is checked against independent references: published data, the reference equations of state
          and an independent implementation. The <Link to="/theory">Theory</Link> page has the equations and sources;
          the <Link to="/developers">API</Link> gives the same calculations as JSON for your own programs.
        </p>
        <p>
          PEC is open source. Suggestions and contributions are welcome: see the GitHub link below.
        </p>
      </div>
    </div>
  );
}
