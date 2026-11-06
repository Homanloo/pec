import { useContext, useEffect, useRef } from "react";
import { ThemeContext } from "../router";

export interface Trace {
  x: number[];
  y: number[];
  name: string;
  color?: string; // CSS colour or a var(--token) name
  dash?: "solid" | "dash" | "dot";
  markers?: boolean;
}

// Theme colours come from the CSS tokens, so charts follow light and dark mode
function cssVar(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}
const resolve = (c: string) => (c.startsWith("--") ? cssVar(c) : c);

// Plotly (basic bundle: scatter only) is loaded on first use, so pages without charts stay light.
// Ranges are in axis units (for a log axis: log10 of the values, as Plotly takes them)
export function Chart(props: {
  traces: Trace[];
  xTitle: string;
  yTitle: string;
  xLog?: boolean;
  yLog?: boolean;
  xRange?: [number, number];
  yRange?: [number, number];
}) {
  const ref = useRef<HTMLDivElement>(null);
  const theme = useContext(ThemeContext);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let live = true;
    import("plotly.js-basic-dist-min").then(({ default: Plotly }) => {
      if (!live) return;
      const text = cssVar("--text");
      const grid = cssVar("--border");
      const axis = (title: string, log?: boolean, range?: [number, number]) => ({
        title: { text: title },
        type: log ? "log" : "linear",
        gridcolor: grid,
        zerolinecolor: grid,
        linecolor: text,
        ticks: "outside",
        ...(range ? { range } : {}),
      });
      const data = props.traces.map((t) => ({
        type: "scatter",
        mode: t.markers ? "markers" : "lines",
        name: t.name,
        x: t.x,
        y: t.y,
        line: { color: resolve(t.color ?? "--brand"), width: 2, dash: t.dash ?? "solid" },
        marker: { color: resolve(t.color ?? "--brand"), size: 7 },
      }));
      const layout = {
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { family: "Signika Negative, sans-serif", color: text, size: 14 },
        margin: { l: 70, r: 20, t: 20, b: 60 },
        xaxis: axis(props.xTitle, props.xLog, props.xRange),
        yaxis: axis(props.yTitle, props.yLog, props.yRange),
        legend: { orientation: "h", y: -0.2 },
        hovermode: "closest",
      };
      Plotly.react(el, data, layout, { responsive: true, displaylogo: false });
    });
    return () => {
      live = false;
    };
  }, [props.traces, props.xTitle, props.yTitle, props.xLog, props.yLog, props.xRange, props.yRange, theme]);

  useEffect(() => {
    const el = ref.current;
    return () => {
      if (el) import("plotly.js-basic-dist-min").then(({ default: Plotly }) => Plotly.purge(el));
    };
  }, []);

  return <div ref={ref} className="chart" />;
}
