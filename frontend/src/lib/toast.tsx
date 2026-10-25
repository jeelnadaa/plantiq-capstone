/** Toasts, including the 3-second undo toast used by History (same behaviour as the original). */
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { CheckCircle2, CircleAlert, Trash2 } from "lucide-react";
import { useI18n } from "./i18n";

type Toast = { id: number; text: string; kind: "ok" | "error" | "undo"; seconds: number; onUndo?: () => void; onCommit?: () => void };
type Ctx = {
  show: (text: string, kind?: "ok" | "error") => void;
  undo: (text: string, onUndo: () => void, onCommit?: () => void, seconds?: number) => void;
};
const ToastCtx = createContext<Ctx | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const { t } = useI18n();
  const [toast, setToast] = useState<Toast | null>(null);
  const [left, setLeft] = useState(0);
  const timer = useRef<number>();
  const tick = useRef<number>();
  const current = useRef<Toast | null>(null);

  const finish = useCallback((commit: boolean) => {
    window.clearTimeout(timer.current);
    window.clearInterval(tick.current);
    const cur = current.current;
    current.current = null;
    setToast(null);
    if (commit && cur?.onCommit) cur.onCommit();
  }, []);

  const open = useCallback((tst: Toast) => {
    if (current.current) finish(true); // a new action commits the pending one
    current.current = tst;
    setToast(tst);
    setLeft(tst.seconds);
    timer.current = window.setTimeout(() => finish(true), tst.seconds * 1000);
    tick.current = window.setInterval(() => setLeft((s) => Math.max(0, s - 1)), 1000);
  }, [finish]);

  useEffect(() => () => {
    window.clearTimeout(timer.current);
    window.clearInterval(tick.current);
  }, []);

  const value = useMemo<Ctx>(() => ({
    show: (text, kind = "ok") => open({ id: Date.now(), text, kind, seconds: 3 }),
    undo: (text, onUndo, onCommit, seconds = 3) => open({ id: Date.now(), text, kind: "undo", seconds, onUndo, onCommit }),
  }), [open]);

  return (
    <ToastCtx.Provider value={value}>
      {children}
      {toast && (
        <div className="toast" role="status" aria-live="polite" key={toast.id}>
          {toast.kind === "undo" ? <Trash2 /> : toast.kind === "error" ? <CircleAlert /> : <CheckCircle2 />}
          <span className="grow">{toast.text}</span>
          {toast.kind === "undo" && (
            <button className="btn btn-sm" onClick={() => { toast.onUndo?.(); finish(false); }}>
              {t("undo")} ({left}s)
            </button>
          )}
          <span className="timer" style={{ animationDuration: `${toast.seconds}s` }} />
        </div>
      )}
    </ToastCtx.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastCtx);
  if (!ctx) throw new Error("useToast outside provider");
  return ctx;
}
