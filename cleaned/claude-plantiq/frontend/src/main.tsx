import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@fontsource/noto-sans-kannada/400.css";
import "@fontsource/noto-sans-kannada/700.css";
import "./styles/tokens.css";
import "./styles/components.css";
import "./styles/app.css";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
