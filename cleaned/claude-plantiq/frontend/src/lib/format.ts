import type { Lang } from "./i18n";
import { translate } from "./i18n";
import type { TKey } from "./i18n/en";

export const DISEASES = ["Rust", "Cerscospora", "Phoma", "Miner", "Healthy"] as const;
export type Disease = (typeof DISEASES)[number];

export function diseaseName(lang: Lang, cls: string, short = false): string {
  const key = `${short ? "dzShort_" : "dz_"}${cls}` as TKey;
  const v = translate(lang, key);
  return v === key ? cls : v;
}

export function diseaseKind(cls: string): "healthy" | "pest" | "disease" {
  return cls === "Healthy" ? "healthy" : cls === "Miner" ? "pest" : "disease";
}

export function parseDate(s: string | Date): Date {
  if (s instanceof Date) return s;
  return new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(s) ? s : `${s}Z`);
}

export function timeAgo(lang: Lang, s: string | Date, now = Date.now()): string {
  const diff = Math.max(0, now - parseDate(s).getTime()) / 1000;
  if (diff < 60) return translate(lang, "justNow");
  if (diff < 3600) return translate(lang, "minutesAgo", { n: Math.floor(diff / 60) });
  if (diff < 86400) return translate(lang, "hoursAgo", { n: Math.floor(diff / 3600) });
  return translate(lang, "daysAgo", { n: Math.floor(diff / 86400) });
}

export function dayBucket(s: string | Date, now = new Date()): "today" | "yesterday" | "earlier" {
  const d = parseDate(s);
  const start = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  if (d.getTime() >= start) return "today";
  if (d.getTime() >= start - 86400000) return "yesterday";
  return "earlier";
}

export function clock(lang: Lang, s: string | Date) {
  return parseDate(s).toLocaleTimeString(lang === "kn" ? "kn-IN" : "en-IN", { hour: "2-digit", minute: "2-digit" });
}

export function shortDate(lang: Lang, s: string | Date) {
  return parseDate(s).toLocaleDateString(lang === "kn" ? "kn-IN" : "en-IN", { day: "numeric", month: "short" });
}

export function inr(n: number) {
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: n % 1 === 0 ? 0 : 2 }).format(n);
}

export function num(n: number | null | undefined, digits = 1) {
  if (n === null || n === undefined || Number.isNaN(n)) return "--";
  return Number(n).toFixed(digits).replace(/\.0+$/, "");
}

export function formatCountdown(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = Math.max(0, seconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const rad = (d: number) => (d * Math.PI) / 180;
  const a = Math.sin(rad(lat2 - lat1) / 2) ** 2 + Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.sin(rad(lon2 - lon1) / 2) ** 2;
  return Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)) * 10) / 10;
}
