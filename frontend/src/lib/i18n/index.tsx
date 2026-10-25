import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import en, { type TKey } from "./en";
import kn from "./kn";

export type Lang = "en" | "kn";
const DICTS = { en, kn };
const KEY = "plantiq.lang";

export function format(template: string, vars?: Record<string, string | number>) {
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (_, k) => (vars[k] !== undefined ? String(vars[k]) : `{${k}}`));
}

export function translate(lang: Lang, key: TKey, vars?: Record<string, string | number>) {
  return format(DICTS[lang][key] ?? en[key] ?? key, vars);
}

type Ctx = { lang: Lang; setLang: (l: Lang) => void; toggle: () => void; t: (k: TKey, v?: Record<string, string | number>) => string };
const I18nCtx = createContext<Ctx | null>(null);

function initialLang(): Lang {
  try {
    const saved = localStorage.getItem(KEY);
    if (saved === "en" || saved === "kn") return saved;
  } catch {
    /* ignore */
  }
  return navigator.language?.toLowerCase().startsWith("kn") ? "kn" : "en";
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(initialLang);
  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    try {
      localStorage.setItem(KEY, l);
    } catch {
      /* ignore */
    }
  }, []);
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);
  const value = useMemo<Ctx>(() => ({
    lang,
    setLang,
    toggle: () => setLang(lang === "en" ? "kn" : "en"),
    t: (k, v) => translate(lang, k, v),
  }), [lang, setLang]);
  return <I18nCtx.Provider value={value}>{children}</I18nCtx.Provider>;
}

export function useI18n() {
  const ctx = useContext(I18nCtx);
  if (!ctx) throw new Error("useI18n outside provider");
  return ctx;
}

export type { TKey };
