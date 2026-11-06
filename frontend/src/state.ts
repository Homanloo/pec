import { useState } from "react";
import { ApiError } from "./api";

// Page inputs live in the URL (?s=<json>), so a link reproduces a calculation.
export function readState<T extends object>(defaults: T): T {
  const s = new URLSearchParams(window.location.search).get("s");
  if (!s) return defaults;
  try {
    return { ...defaults, ...JSON.parse(s) };
  } catch {
    return defaults;
  }
}

export function writeState(state: object) {
  const url = `${window.location.pathname}?s=${encodeURIComponent(JSON.stringify(state))}`;
  window.history.replaceState(null, "", url);
}

export const hasState = () => new URLSearchParams(window.location.search).has("s");

// One calculation at a time: its result, its error messages and whether it is running
export function useCalc<T>() {
  const [result, setResult] = useState<T | null>(null);
  const [error, setError] = useState<string[] | null>(null);
  const [busy, setBusy] = useState(false);
  async function run(task: () => Promise<T>) {
    setBusy(true);
    setError(null);
    try {
      setResult(await task());
    } catch (e) {
      setResult(null);
      setError(e instanceof ApiError ? e.messages : [String(e)]);
    } finally {
      setBusy(false);
    }
  }
  return { result, error, busy, run };
}

// Downloads for the result tables
export function download(filename: string, text: string, type: string) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function toCsv(header: string[], rows: (string | number)[][]): string {
  const cell = (v: string | number) => (typeof v === "string" && /[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : String(v));
  return [header, ...rows].map((r) => r.map(cell).join(",")).join("\n") + "\n";
}
