// Calls to the PEC API (/api/v1/). Errors carry the API's messages, one per line.

export class ApiError extends Error {
  constructor(public messages: string[]) {
    super(messages.join("; "));
  }
}

// DRF errors: {"detail": "..."} or {field: ["..."]} or nested {field: {index: ["..."]}}
function messagesOf(data: unknown, prefix = ""): string[] {
  if (typeof data === "string") return [prefix ? `${prefix}: ${data}` : data];
  if (Array.isArray(data)) return data.flatMap((d) => messagesOf(d, prefix));
  if (data && typeof data === "object") {
    return Object.entries(data).flatMap(([k, v]) =>
      messagesOf(v, k === "detail" || k === "non_field_errors" ? prefix : prefix ? `${prefix}.${k}` : k),
    );
  }
  return [];
}

export async function api<T>(path: string, body?: unknown): Promise<T> {
  const init: RequestInit =
    body === undefined
      ? {}
      : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  let response: Response;
  try {
    response = await fetch(`/api/v1/${path}`, init);
  } catch {
    throw new ApiError(["The server could not be reached."]);
  }
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const messages = messagesOf(data);
    throw new ApiError(messages.length ? messages : [`Request failed (HTTP ${response.status}).`]);
  }
  return data as T;
}

export interface Component {
  name: string;
  cas: string;
  formula: string;
  molar_mass: number;
  Tc: number;
  Pc: number;
  omega: number;
  source: string;
}

export interface Phase {
  name: "liquid" | "vapour";
  fraction: number;
  composition: number[];
  Z: number;
  V: number;
}

// The component list is the same for every page: fetch it once
let components: Promise<Component[]> | null = null;
export function loadComponents(): Promise<Component[]> {
  components ??= api<Component[]>("components/");
  return components;
}

export const MODELS = [
  ["PR", "Peng–Robinson (1976)"],
  ["SRK", "Soave–Redlich–Kwong (1972)"],
  ["RK", "Redlich–Kwong (1949)"],
  ["vdW", "van der Waals (1873)"],
] as const;
