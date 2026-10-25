import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

export type Mode = "light" | "dark" | "auto";
export type Palette = "estate" | "monsoon" | "harvest" | "cherry" | "sunlight";
export const PALETTES: { id: Palette; swatch: [string, string] }[] = [
  { id: "estate", swatch: ["#1E6B45", "#B4452A"] },
  { id: "monsoon", swatch: ["#1D5F7E", "#C98A0B"] },
  { id: "harvest", swatch: ["#8A5300", "#2F6B45"] },
  { id: "cherry", swatch: ["#9B2C2C", "#2F6B45"] },
  { id: "sunlight", swatch: ["#000000", "#0A5A1E"] },
];

const read = (k: string, d: string) => {
  try {
    return localStorage.getItem(k) || d;
  } catch {
    return d;
  }
};
const write = (k: string, v: string) => {
  try {
    localStorage.setItem(k, v);
  } catch {
    /* ignore */
  }
};

type Ctx = { mode: Mode; palette: Palette; dark: boolean; setMode: (m: Mode) => void; setPalette: (p: Palette) => void; toggleDark: () => void };
const ThemeCtx = createContext<Ctx | null>(null);

function systemDark() {
  return typeof window !== "undefined" && window.matchMedia?.("(prefers-color-scheme: dark)").matches;
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<Mode>(() => read("plantiq.mode", "light") as Mode);
  const [palette, setPaletteState] = useState<Palette>(() => read("plantiq.palette", "estate") as Palette);
  const [sys, setSys] = useState(systemDark());

  useEffect(() => {
    const mq = window.matchMedia?.("(prefers-color-scheme: dark)");
    const on = () => setSys(mq.matches);
    mq?.addEventListener?.("change", on);
    return () => mq?.removeEventListener?.("change", on);
  }, []);

  const dark = mode === "dark" || (mode === "auto" && sys);
  useEffect(() => {
    const root = document.documentElement;
    root.dataset.theme = dark ? "dark" : "light";
    root.dataset.palette = palette;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", getComputedStyle(root).getPropertyValue("--primary").trim() || "#1E6B45");
  }, [dark, palette]);

  const value = useMemo<Ctx>(() => ({
    mode, palette, dark,
    setMode: (m) => { setModeState(m); write("plantiq.mode", m); },
    setPalette: (p) => { setPaletteState(p); write("plantiq.palette", p); },
    toggleDark: () => { const m = dark ? "light" : "dark"; setModeState(m); write("plantiq.mode", m); },
  }), [mode, palette, dark]);
  return <ThemeCtx.Provider value={value}>{children}</ThemeCtx.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeCtx);
  if (!ctx) throw new Error("useTheme outside provider");
  return ctx;
}
