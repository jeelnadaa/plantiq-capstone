import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { apiBase, getServerUrl, needsServerSetup, pingServer } from "./api";

export type Status = "unknown" | "ok" | "warn" | "down";
type Ctx = { status: Status; latency: number | null; check: () => Promise<void>; url: string };
const StatusCtx = createContext<Ctx | null>(null);

export function ServerStatusProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<Status>("unknown");
  const [latency, setLatency] = useState<number | null>(null);
  const [url, setUrl] = useState(getServerUrl());

  const check = useCallback(async () => {
    if (needsServerSetup()) {
      setStatus("down");
      return;
    }
    const base = apiBase() || window.location.origin;
    const res = await pingServer(base, 4000);
    setLatency(res.ok ? res.ms : null);
    setStatus(res.ok ? "ok" : res.status ? "warn" : "down");
  }, []);

  useEffect(() => {
    check();
    const id = window.setInterval(check, 30000);
    const onChange = () => {
      setUrl(getServerUrl());
      check();
    };
    window.addEventListener("plantiq:server-changed", onChange);
    window.addEventListener("online", check);
    return () => {
      window.clearInterval(id);
      window.removeEventListener("plantiq:server-changed", onChange);
      window.removeEventListener("online", check);
    };
  }, [check]);

  return <StatusCtx.Provider value={{ status, latency, check, url }}>{children}</StatusCtx.Provider>;
}

export function useServerStatus() {
  const ctx = useContext(StatusCtx);
  if (!ctx) throw new Error("useServerStatus outside provider");
  return ctx;
}
