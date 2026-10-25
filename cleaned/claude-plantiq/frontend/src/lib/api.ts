/**
 * API client.
 *  - Backend URL is chosen at runtime (server settings screen) and stored locally, so the APK can talk to a
 *    laptop on the LAN, a tunnel or a cloud server without rebuilding.
 *  - Access token in memory + storage, refresh token in storage; one transparent refresh on 401.
 */
import { isNative } from "./native";

const KEY_URL = "plantiq.server_url";
const KEY_ACCESS = "plantiq.access";
const KEY_REFRESH = "plantiq.refresh";
const KEY_USER = "plantiq.user";
export const DEFAULT_PORT = 8000;

export type User = {
  id: number;
  username: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  preferred_language: "en" | "kn";
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
};

export class ApiError extends Error {
  status: number;
  code?: string;
  fieldErrors: { field: string; message: string }[];
  retryAfter?: number;
  constructor(status: number, message: string, code?: string, fieldErrors: { field: string; message: string }[] = [], retryAfter?: number) {
    super(message);
    this.status = status;
    this.code = code;
    this.fieldErrors = fieldErrors;
    this.retryAfter = retryAfter;
  }
}

const store = {
  get(k: string): string | null {
    try {
      return localStorage.getItem(k);
    } catch {
      return null;
    }
  },
  set(k: string, v: string | null) {
    try {
      if (v === null) localStorage.removeItem(k);
      else localStorage.setItem(k, v);
    } catch {
      /* storage unavailable (private mode) — app still works for this session */
    }
  },
};

// ------------------------------------------------------------------ server URL
export function normalizeServerUrl(input: string): string {
  let url = (input || "").trim().replace(/\s+/g, "");
  if (!url) return "";
  url = url.replace(/\/+$/, "");
  if (!/^https?:\/\//i.test(url)) url = `http://${url}`;
  try {
    const u = new URL(url);
    if (!u.port && u.protocol === "http:" && isPrivateHost(u.hostname)) u.port = String(DEFAULT_PORT);
    return `${u.protocol}//${u.host}${u.pathname.replace(/\/+$/, "")}`;
  } catch {
    return "";
  }
}

export function isPrivateHost(host: string): boolean {
  return /^(localhost|127\.|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)/.test(host);
}

export function getServerUrl(): string {
  return store.get(KEY_URL) || "";
}

export function setServerUrl(url: string) {
  const clean = normalizeServerUrl(url);
  store.set(KEY_URL, clean || null);
  window.dispatchEvent(new Event("plantiq:server-changed"));
}

/** Base URL for requests: configured server, or same-origin when the web UI is served by the backend. */
export function apiBase(): string {
  const custom = getServerUrl();
  if (custom) return custom;
  return "";
}

/** True when we have no idea where the backend is (APK on first launch). */
export function needsServerSetup(): boolean {
  return isNative() && !getServerUrl();
}

export function resolveUrl(path: string | null | undefined): string {
  if (!path) return "";
  if (/^(https?:|data:|blob:)/.test(path)) return path;
  return `${apiBase()}${path}`;
}

// ------------------------------------------------------------------ tokens
let accessToken: string | null = store.get(KEY_ACCESS);

export function getAccessToken() {
  return accessToken;
}

export function saveSession(t: TokenResponse) {
  accessToken = t.access_token;
  store.set(KEY_ACCESS, t.access_token);
  store.set(KEY_REFRESH, t.refresh_token);
  store.set(KEY_USER, JSON.stringify(t.user));
}

export function clearSession() {
  accessToken = null;
  store.set(KEY_ACCESS, null);
  store.set(KEY_REFRESH, null);
  store.set(KEY_USER, null);
}

export function cachedUser(): User | null {
  try {
    const raw = store.get(KEY_USER);
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

export function cacheUser(u: User) {
  store.set(KEY_USER, JSON.stringify(u));
}

export function hasRefreshToken() {
  return !!store.get(KEY_REFRESH);
}

// ------------------------------------------------------------------ fetch
type Opts = {
  method?: string;
  body?: unknown;
  form?: FormData;
  auth?: boolean;
  timeoutMs?: number;
  signal?: AbortSignal;
  query?: Record<string, string | number | boolean | null | undefined>;
};

let refreshing: Promise<boolean> | null = null;
const listeners = new Set<() => void>();
export function onSessionExpired(fn: () => void) {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
}

async function tryRefresh(): Promise<boolean> {
  const rt = store.get(KEY_REFRESH);
  if (!rt) return false;
  if (!refreshing) {
    refreshing = (async () => {
      try {
        const res = await rawFetch("/api/v1/auth/refresh", { method: "POST", body: { refresh_token: rt }, auth: false });
        saveSession(res as TokenResponse);
        return true;
      } catch {
        return false;
      } finally {
        setTimeout(() => (refreshing = null), 0);
      }
    })();
  }
  return refreshing;
}

function buildUrl(path: string, query?: Opts["query"]) {
  let url = `${apiBase()}${path}`;
  if (query) {
    const qs = new URLSearchParams();
    Object.entries(query).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
    });
    const s = qs.toString();
    if (s) url += `?${s}`;
  }
  return url;
}

async function rawFetch(path: string, opts: Opts = {}): Promise<unknown> {
  const headers: Record<string, string> = { Accept: "application/json", "Bypass-Tunnel-Reminder": "1" };
  if (opts.auth !== false && accessToken) headers.Authorization = `Bearer ${accessToken}`;
  let body: BodyInit | undefined;
  if (opts.form) body = opts.form;
  else if (opts.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(opts.body);
  }
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), opts.timeoutMs ?? 30000);
  opts.signal?.addEventListener("abort", () => ctrl.abort());
  let res: Response;
  try {
    res = await fetch(buildUrl(path, opts.query), { method: opts.method ?? (body ? "POST" : "GET"), headers, body, signal: ctrl.signal });
  } catch (e) {
    const aborted = (e as Error).name === "AbortError";
    throw new ApiError(0, aborted ? "timeout" : "network", aborted ? "timeout" : "network");
  } finally {
    clearTimeout(timer);
  }
  if (res.status === 204) return null;
  const text = await res.text();
  let data: any = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { detail: text };
  }
  if (!res.ok) {
    const detail = data?.detail;
    const message = typeof detail === "string" ? detail : detail?.message ?? `HTTP ${res.status}`;
    const retry = Number(res.headers.get("retry-after") ?? detail?.retry_after) || undefined;
    throw new ApiError(res.status, message, data?.code, data?.errors ?? [], retry);
  }
  return data;
}

export async function api<T = unknown>(path: string, opts: Opts = {}): Promise<T> {
  try {
    return (await rawFetch(path, opts)) as T;
  } catch (e) {
    if (e instanceof ApiError && e.status === 401 && opts.auth !== false && !path.includes("/auth/")) {
      if (await tryRefresh()) return (await rawFetch(path, opts)) as T;
      clearSession();
      listeners.forEach((fn) => fn());
    }
    throw e;
  }
}

/** Ping /health and measure latency (server settings "Test"). */
export async function pingServer(url: string, timeoutMs = 5000): Promise<{ ok: boolean; ms: number; version?: string; status?: number }> {
  const base = normalizeServerUrl(url);
  const started = performance.now();
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${base}/health`, { signal: ctrl.signal, headers: { "Bypass-Tunnel-Reminder": "1" } });
    const ms = Math.round(performance.now() - started);
    if (!res.ok) return { ok: false, ms, status: res.status };
    const data = await res.json().catch(() => ({}));
    return { ok: data?.status === "ok", ms, version: data?.version };
  } catch {
    return { ok: false, ms: Math.round(performance.now() - started) };
  } finally {
    clearTimeout(timer);
  }
}

export const API = "/api/v1";
