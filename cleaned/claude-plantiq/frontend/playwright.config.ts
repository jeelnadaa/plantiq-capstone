import { defineConfig, devices } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// E2E runs the real backend (fake ML, throw-away SQLite) serving the built web UI.
const backend = path.resolve(__dirname, "../backend");
const python = process.platform === "win32" ? path.join(backend, ".venv/Scripts/python.exe") : path.join(backend, ".venv/bin/python");
const PORT = 8200;

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    ...devices["Pixel 7"],
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "pixel7", use: { ...devices["Pixel 7"] } }],
  webServer: {
    command: `"${python}" -c "import shutil,os; shutil.rmtree('var-e2e', ignore_errors=True)" && "${python}" run.py --port ${PORT}`,
    cwd: backend,
    url: `http://127.0.0.1:${PORT}/health`,
    reuseExistingServer: false,
    timeout: 120_000,
    env: {
      PLANTIQ_FAKE_ML: "1",
      VAR_DIR: "var-e2e",
      DATABASE_URL: "sqlite:///./var-e2e/e2e.db",
      RATE_LIMIT_ENABLED: "false",
      GEMINI_API_KEY: "",
      GROQ_API_KEY: "",
      OPEN_METEO_URL: "http://127.0.0.1:9/unreachable",
    },
  },
});
