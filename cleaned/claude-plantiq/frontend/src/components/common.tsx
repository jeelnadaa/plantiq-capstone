import { useCallback, useState, type InputHTMLAttributes, type ReactNode } from "react";
import { AlertCircle, Check, Circle, Eye, EyeOff, Loader2, WifiOff } from "lucide-react";
import { useI18n } from "../lib/i18n";
import { useServerStatus } from "../lib/server-status";
import { passwordRules, passwordScore } from "../lib/validation";
import { ApiError } from "../lib/api";
import type { TKey } from "../lib/i18n/en";

export function Spinner({ size = 20 }: { size?: number }) {
  return <Loader2 className="spin" width={size} height={size} aria-hidden />;
}

export function FieldError({ children, id }: { children?: ReactNode; id?: string }) {
  if (!children) return null;
  return (
    <span className="error-text" role="alert" id={id}>
      <AlertCircle /> {children}
    </span>
  );
}

type FieldProps = { label: ReactNode; error?: string; help?: ReactNode; required?: boolean; children: ReactNode; htmlFor?: string };
export function Field({ label, error, help, required, children, htmlFor }: FieldProps) {
  return (
    <div className="field">
      <label className="label" htmlFor={htmlFor}>
        {label} {required && <span className="req" aria-hidden>*</span>}
      </label>
      {children}
      {error ? <FieldError>{error}</FieldError> : help ? <span className="help">{help}</span> : null}
    </div>
  );
}

export function PasswordInput(props: InputHTMLAttributes<HTMLInputElement> & { invalid?: boolean; icon?: ReactNode }) {
  const { t } = useI18n();
  const [show, setShow] = useState(false);
  const { invalid, icon, className, ...rest } = props;
  return (
    <div className="input-wrap">
      {icon}
      <input {...rest} type={show ? "text" : "password"} className={`input has-trail ${invalid ? "invalid" : ""} ${className ?? ""}`} aria-invalid={invalid || undefined} />
      <button type="button" className="trail" onClick={() => setShow((s) => !s)} aria-label={show ? t("hidePassword") : t("showPassword")} aria-pressed={show}>
        {show ? <EyeOff /> : <Eye />}
      </button>
    </div>
  );
}

export function PasswordStrength({ password, username }: { password: string; username?: string }) {
  const { t } = useI18n();
  const score = password ? passwordScore(password, username) : 0;
  const rules = passwordRules(password, username);
  const items: [boolean, TKey][] = [[rules.length, "ruleLength"], [rules.mix, "ruleMix"], [rules.common, "ruleCommon"]];
  if (username) items.push([rules.username, "ruleUsername"]);
  return (
    <div className="stack-sm" aria-live="polite">
      <div className="row-between">
        <div className="strength grow" data-score={score} aria-hidden>
          <span /><span /><span /><span />
        </div>
        <span className="caption" style={{ minWidth: 70, textAlign: "right" }}>{password ? t(`strength${score}` as TKey) : ""}</span>
      </div>
      <ul className="rules">
        {items.map(([ok, key]) => (
          <li key={key} className={ok ? "ok" : ""}>{ok ? <Check /> : <Circle />}{t(key)}</li>
        ))}
      </ul>
    </div>
  );
}

export function OfflineBanner({ onOpenServer }: { onOpenServer?: () => void }) {
  const { t } = useI18n();
  const { status, check } = useServerStatus();
  if (status !== "down") return null;
  return (
    <div className="banner" role="alert" data-testid="offline-banner">
      <WifiOff />
      <span className="grow">{t("offlineBanner")}</span>
      <button className="btn btn-sm btn-outline" onClick={onOpenServer ?? check}>{onOpenServer ? t("offlineAction") : t("retry")}</button>
    </div>
  );
}

export function EmptyState({ icon, title, body, action }: { icon: ReactNode; title: string; body?: string; action?: ReactNode }) {
  return (
    <div className="empty card flat">
      <div className="empty-ico">{icon}</div>
      <div className="h3">{title}</div>
      {body && <p className="body-sm">{body}</p>}
      {action}
    </div>
  );
}

/** Turn an ApiError into farmer-friendly text. */
export function useErrorText() {
  const { t } = useI18n();
  return useCallback((e: unknown) => {
    if (e instanceof ApiError) {
      if (e.code === "network") return t("networkError");
      if (e.code === "timeout") return t("timeoutError");
      return e.message || t("genericError");
    }
    return t("genericError");
  }, [t]);
}
