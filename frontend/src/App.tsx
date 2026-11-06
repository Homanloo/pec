import { lazy, Suspense, useEffect, useState, type ComponentType } from "react";
import Binary from "./pages/Binary";
import Components from "./pages/Components";
import Developers from "./pages/Developers";
import Envelope from "./pages/Envelope";
import Flash from "./pages/Flash";
import Home from "./pages/Home";
import Pure from "./pages/Pure";
import Saturation from "./pages/Saturation";
import { Link, ThemeContext, usePath } from "./router";

// KaTeX is only needed on the Theory page: load it with that page
const Theory = lazy(() => import("./pages/Theory"));

const PAGES: [string, string, ComponentType][] = [
  ["/flash", "Flash", Flash],
  ["/saturation", "Saturation", Saturation],
  ["/binary", "Binary", Binary],
  ["/envelope", "Envelope", Envelope],
  ["/pure", "Pure", Pure],
  ["/components", "Components", Components],
  ["/theory", "Theory", Theory],
  ["/developers", "API", Developers],
];

function useTheme() {
  const [theme, setTheme] = useState<"light" | "dark">(
    document.documentElement.dataset.theme === "dark" ? "dark" : "light",
  );
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);
  function toggle() {
    const next = theme === "dark" ? "light" : "dark";
    try {
      localStorage.setItem("theme", next);
    } catch {
      // private mode: the choice lasts for this page only
    }
    setTheme(next);
  }
  return [theme, toggle] as const;
}

export default function App() {
  const path = usePath();
  const [theme, toggleTheme] = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);
  const page = PAGES.find(([p]) => p === path);
  const Page = path === "/" ? Home : page?.[2];

  useEffect(() => {
    document.title = page ? `${page[1]} · Phase Equilibrium Calculator` : "Phase Equilibrium Calculator";
    setMenuOpen(false);
  }, [path]); // the title follows the page

  return (
    <ThemeContext.Provider value={theme}>
      <header>
        <nav className="nav" aria-label="main">
          <Link to="/" className="nav-name">
            Phase Equilibrium Calculator
          </Link>
          <button type="button" className="icon-button menu-button" aria-expanded={menuOpen} onClick={() => setMenuOpen(!menuOpen)}>
            Menu
          </button>
          <ul className={menuOpen ? "nav-links open" : "nav-links"}>
            {PAGES.map(([to, title]) => (
              <li key={to}>
                <Link to={to} className={to === path ? "active" : undefined}>
                  {title}
                </Link>
              </li>
            ))}
            <li>
              <button type="button" className="icon-button" onClick={toggleTheme} aria-label="switch light or dark mode" title="Light or dark mode">
                {theme === "dark" ? "☀" : "☾"}
              </button>
            </li>
          </ul>
        </nav>
      </header>
      <main>
        <Suspense fallback={<p className="note">Loading…</p>}>
          {Page ? <Page /> : <NotFound />}
        </Suspense>
      </main>
      <footer>
        <p>
          <strong>Phase Equilibrium Calculator</strong>: phase equilibrium of multi-component mixtures with cubic
          equations of state.
        </p>
        <p>
          Developed and designed by <strong>Mohammad Homanloo</strong>, 2023–2026.
        </p>
        <p>
          <a href="https://www.linkedin.com/in/homanloo/" target="_blank" rel="noreferrer">
            LinkedIn
          </a>
          <a href="https://github.com/Homanloo" target="_blank" rel="noreferrer">
            GitHub
          </a>
          <a href="https://Homanloo.github.io" target="_blank" rel="noreferrer">
            Website
          </a>
        </p>
      </footer>
    </ThemeContext.Provider>
  );
}

function NotFound() {
  return (
    <>
      <h1>Page not found</h1>
      <p>
        There is no page at this address. <Link to="/">Go to the home page.</Link>
      </p>
    </>
  );
}
