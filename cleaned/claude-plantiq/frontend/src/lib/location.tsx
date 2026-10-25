/** Estate location (auto GPS or manual) + live microclimate, shared by Scanner, Chat and Market. */
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { API, api } from "./api";
import { validCoords } from "./validation";

export const DEFAULT_COORDS = { lat: 13.3161, lng: 75.772 }; // Chikkamagaluru, same default as the original
const KEY = "plantiq.coords";

export type Coords = { lat: number | null; lng: number | null; mode: "gps" | "manual"; status: "idle" | "locating" | "ok" | "denied" | "fallback" };

export type Forecast = { date: string; weekday_en: string; weekday_kn: string; rain_mm: number | null; rain_probability: number | null; t_max: number | null; t_min: number | null };
export type EnvData = {
  available: boolean;
  note?: string;
  region_name?: string | null;
  coordinates?: string | null;
  temperature?: number | null;
  feels_like?: number | null;
  humidity?: number | null;
  rainfall?: number | null;
  wind_speed?: number | null;
  elevation?: number | null;
  soil_ph?: number | null;
  incubation_risk?: string | null;
  risk_level?: "high" | "moderate" | "low" | "none";
  forecast?: Forecast[];
  spray_window?: { day_index: number | null; status: string; advice_en: string; advice_kn: string } | null;
};

type Ctx = {
  coords: Coords;
  env: EnvData | null;
  envLoading: boolean;
  requestGps: () => void;
  setManual: (lat: number, lng: number) => boolean;
  clearLocation: () => void;
  refreshEnv: () => void;
  hasCoords: boolean;
};

const LocationCtx = createContext<Ctx | null>(null);

function load(): Coords {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const c = JSON.parse(raw);
      if (c && (c.lat === null || typeof c.lat === "number")) return { ...c, status: c.lat === null ? "idle" : "ok" };
    }
  } catch {
    /* ignore */
  }
  return { lat: null, lng: null, mode: "gps", status: "idle" };
}

export function LocationProvider({ children, autoStart = true }: { children: ReactNode; autoStart?: boolean }) {
  const [coords, setCoords] = useState<Coords>(load);
  const [env, setEnv] = useState<EnvData | null>(null);
  const [envLoading, setEnvLoading] = useState(false);
  const reqId = useRef(0);

  const persist = (c: Coords) => {
    setCoords(c);
    try {
      localStorage.setItem(KEY, JSON.stringify({ lat: c.lat, lng: c.lng, mode: c.mode }));
    } catch {
      /* ignore */
    }
  };

  const fetchEnv = useCallback(async (lat: number | null, lng: number | null) => {
    const id = ++reqId.current;
    if (lat === null || lng === null) {
      setEnv({ available: false });
      return;
    }
    setEnvLoading(true);
    try {
      const data = await api<EnvData>(`${API}/environment/live`, { query: { latitude: lat, longitude: lng }, auth: false, timeoutMs: 12000 });
      if (id === reqId.current) setEnv(data);
    } catch {
      if (id === reqId.current) setEnv({ available: false });
    } finally {
      if (id === reqId.current) setEnvLoading(false);
    }
  }, []);

  const requestGps = useCallback(() => {
    if (!("geolocation" in navigator)) {
      const c: Coords = { ...DEFAULT_COORDS, mode: "gps", status: "fallback" };
      persist(c);
      fetchEnv(c.lat, c.lng);
      return;
    }
    setCoords((c) => ({ ...c, mode: "gps", status: "locating" }));
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const c: Coords = { lat: +pos.coords.latitude.toFixed(5), lng: +pos.coords.longitude.toFixed(5), mode: "gps", status: "ok" };
        persist(c);
        fetchEnv(c.lat, c.lng);
      },
      () => {
        const c: Coords = { ...DEFAULT_COORDS, mode: "gps", status: "denied" };
        persist(c);
        fetchEnv(c.lat, c.lng);
      },
      { timeout: 8000, maximumAge: 5 * 60 * 1000, enableHighAccuracy: false },
    );
  }, [fetchEnv]);

  const setManual = useCallback((lat: number, lng: number) => {
    if (!validCoords(lat, lng)) return false;
    const c: Coords = { lat, lng, mode: "manual", status: "ok" };
    persist(c);
    fetchEnv(lat, lng);
    return true;
  }, [fetchEnv]);

  const clearLocation = useCallback(() => {
    persist({ lat: null, lng: null, mode: "manual", status: "idle" });
    setEnv({ available: false });
  }, []);

  useEffect(() => {
    if (!autoStart) return;
    if (coords.mode === "gps") requestGps();
    else fetchEnv(coords.lat, coords.lng);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const on = () => fetchEnv(coords.lat, coords.lng);
    window.addEventListener("plantiq:server-changed", on);
    return () => window.removeEventListener("plantiq:server-changed", on);
  }, [coords.lat, coords.lng, fetchEnv]);

  const value = useMemo<Ctx>(() => ({
    coords, env, envLoading, requestGps, setManual, clearLocation,
    refreshEnv: () => fetchEnv(coords.lat, coords.lng),
    hasCoords: coords.lat !== null && coords.lng !== null,
  }), [coords, env, envLoading, requestGps, setManual, clearLocation, fetchEnv]);
  return <LocationCtx.Provider value={value}>{children}</LocationCtx.Provider>;
}

export function useLocation2() {
  const ctx = useContext(LocationCtx);
  if (!ctx) throw new Error("useLocation2 outside provider");
  return ctx;
}
