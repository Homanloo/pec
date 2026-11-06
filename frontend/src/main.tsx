import "@fontsource/signika-negative/300.css";
import "@fontsource/signika-negative/500.css";
import "@fontsource/signika-negative/600.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
