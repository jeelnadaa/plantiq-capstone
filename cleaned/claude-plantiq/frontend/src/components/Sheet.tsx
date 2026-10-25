import { useEffect, useId, useRef, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import { pushBackHandler } from "../lib/native";
import { useI18n } from "../lib/i18n";

type Props = {
  open: boolean;
  onClose: () => void;
  title?: ReactNode;
  icon?: ReactNode;
  iconTone?: "default" | "danger" | "warn";
  center?: boolean;
  children: ReactNode;
  headerExtra?: ReactNode;
  testId?: string;
  dismissable?: boolean;
};

/** Bottom sheet (or centred dialog) with backdrop, Esc, Android back and focus handling. */
export function Sheet({ open, onClose, title, icon, iconTone = "default", center, children, headerExtra, testId, dismissable = true }: Props) {
  const { t } = useI18n();
  const ref = useRef<HTMLDivElement>(null);
  const titleId = useId();
  const closeRef = useRef(onClose);
  closeRef.current = onClose;

  useEffect(() => {
    if (!open) return;
    const prev = document.activeElement as HTMLElement | null;
    const offBack = pushBackHandler(() => {
      if (dismissable) closeRef.current();
      return true;
    });
    document.body.style.overflow = "hidden";
    const focusTimer = window.setTimeout(() => {
      const first = ref.current?.querySelector<HTMLElement>("input, textarea, select, button:not([data-close])");
      (first ?? ref.current)?.focus();
    }, 50);
    return () => {
      offBack();
      document.body.style.overflow = "";
      window.clearTimeout(focusTimer);
      prev?.focus?.();
    };
  }, [open, dismissable]);

  if (!open) return null;
  return createPortal(
    <div
      className="sheet-backdrop"
      style={center ? { alignItems: "center" } : undefined}
      onMouseDown={(e) => {
        if (e.target === e.currentTarget && dismissable) onClose();
      }}
    >
      <div
        ref={ref}
        className={`sheet${center ? " center-sheet" : ""}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? titleId : undefined}
        tabIndex={-1}
        data-testid={testId}
      >
        {!center && <div className="sheet-grip" aria-hidden />}
        {(title || icon) && (
          <div className="sheet-head">
            {icon && <div className={`sheet-ico ${iconTone !== "default" ? iconTone : ""}`}>{icon}</div>}
            <div className="h2" id={titleId}>{title}</div>
            {headerExtra}
            {dismissable && (
              <button className="icon-btn" onClick={onClose} aria-label={t("close")} data-close>
                <X />
              </button>
            )}
          </div>
        )}
        {children}
      </div>
    </div>,
    document.body,
  );
}
