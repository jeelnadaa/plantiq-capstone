/// <reference types="vitest" />
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

// Production builds get a strict CSP meta tag (the APK has no server to send headers).
// Dev mode skips it because the React refresh preamble is an inline script.
const cspMeta = (): Plugin => ({
  name: "plantiq-csp",
  apply: "build",
  transformIndexHtml(html) {
    const csp = [
      "default-src 'self'",
      "script-src 'self'",
      "style-src 'self' 'unsafe-inline'",
      "font-src 'self' data:",
      "img-src 'self' data: blob: http: https:",
      "media-src 'self' blob:",
      "connect-src 'self' http: https:",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join("; ");
    return html.replace("<head>", `<head>\n    <meta http-equiv="Content-Security-Policy" content="${csp}">`);
  },
});

const backend = process.env.PLANTIQ_BACKEND ?? "http://127.0.0.1:8000";

export default defineConfig({
  base: "./", // relative asset paths → works from file:// / Capacitor and from the backend at /
  plugins: [react(), cspMeta()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      "/api": backend,
      "/media": backend,
      "/health": backend,
    },
  },
  build: {
    target: "es2019",
    sourcemap: false,
    chunkSizeWarningLimit: 900,
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    include: ["tests/unit/**/*.test.{ts,tsx}"],
    css: false,
  },
});
