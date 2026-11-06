import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Built files are served by Django under /static/ (WhiteNoise); in `vite dev` the app is at /
// and API calls go to Django on :8000.
export default defineConfig(({ command }) => ({
  base: command === "build" ? "/static/" : "/",
  plugins: [react()],
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
  // Plotly (~1.2 MB) is a chunk of its own, loaded only by pages with charts
  build: { chunkSizeWarningLimit: 1300 },
}));
