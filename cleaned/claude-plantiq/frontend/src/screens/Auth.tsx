import { useEffect, useRef, useState, type FormEvent } from "react";
import { AtSign, Check, Languages, Lock, LogIn, Mail, Phone, Server, ShieldAlert, ShieldCheck, Sprout, UserRound, X } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useI18n, type Lang } from "../lib/i18n";
import { useAuth } from "../lib/auth";
import { API, ApiError, api, getServerUrl } from "../lib/api";
import { Field, FieldError, PasswordInput, PasswordStrength, Spinner, useErrorText } from "../components/common";
import { ServerSettings } from "../components/modals/ServerSettings";
import { formatCountdown } from "../lib/format";
import { isEmail, normalizePhone, passwordOk, USERNAME_RE } from "../lib/validation";

export function LeafArt() {
  return (
    <svg className="hero-leaf" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2" aria-hidden>
      <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
      <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
    </svg>
  );
}

export function AuthScreen({ mode }: { mode: "signin" | "signup" }) {
  const { t, toggle } = useI18n();
  const nav = useNavigate();
  const [serverOpen, setServerOpen] = useState(false);
  const server = getServerUrl() || window.location.host;
  return (
    <div className="screen" data-testid={`auth-${mode}`}>
      <div className="auth-hero">
        <LeafArt />
        <div className="row-between">
          <div className="row"><div className="brand-mark" style={{ background: "rgba(255,255,255,.18)" }}><Sprout /></div><b style={{ fontSize: "1.25rem" }}>PlantIQ</b></div>
          <button className="lang-pill" style={{ background: "rgba(255,255,255,.16)", borderColor: "rgba(255,255,255,.3)", color: "inherit" }} onClick={toggle} data-testid="lang-toggle">
            <Languages />{t("langToggle")}
          </button>
        </div>
        <h1 className="h1" style={{ marginTop: 22 }}>{mode === "signin" ? t("welcomeBack") : t("createAccountTitle")}</h1>
        <p>{mode === "signin" ? t("signInSub") : t("createAccountSub")}</p>
      </div>
      <div className="card auth-card stack">
        <div className="segmented" role="tablist">
          <button role="tab" aria-selected={mode === "signin"} className={mode === "signin" ? "active" : ""} onClick={() => nav("/signin", { replace: true })} data-testid="tab-signin">{t("tabSignIn")}</button>
          <button role="tab" aria-selected={mode === "signup"} className={mode === "signup" ? "active" : ""} onClick={() => nav("/signup", { replace: true })} data-testid="tab-signup">{t("tabCreate")}</button>
        </div>
        {mode === "signin" ? <SignInForm /> : <SignUpForm />}
      </div>
      <div className="screen-body no-nav">
        <button className="btn btn-ghost" onClick={() => setServerOpen(true)}><Server />{t("serverButton", { url: server })}</button>
      </div>
      <ServerSettings open={serverOpen} onClose={() => setServerOpen(false)} />
    </div>
  );
}

function useAfterAuth() {
  const nav = useNavigate();
  const loc = useLocation();
  const { setLang } = useI18n();
  return (lang?: Lang) => {
    if (lang) setLang(lang);
    const from = (loc.state as { from?: string } | null)?.from;
    nav(from && !from.startsWith("/sign") ? from : "/", { replace: true });
  };
}

function SignInForm() {
  const { t } = useI18n();
  const { signIn } = useAuth();
  const after = useAfterAuth();
  const errText = useErrorText();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [lockLeft, setLockLeft] = useState(0);

  useEffect(() => {
    if (lockLeft <= 0) return;
    const id = window.setInterval(() => setLockLeft((s) => s - 1), 1000);
    return () => window.clearInterval(id);
  }, [lockLeft > 0]); // eslint-disable-line react-hooks/exhaustive-deps

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    if (!identifier.trim() || !password) {
      setError(t("errFillLogin"));
      return;
    }
    setBusy(true);
    try {
      const user = await signIn(identifier.trim(), password, remember);
      after(user.preferred_language);
    } catch (err) {
      if (err instanceof ApiError && err.status === 423) setLockLeft(err.retryAfter ?? 900);
      else if (err instanceof ApiError && err.status === 429) setError(err.message);
      else setError(errText(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="stack" onSubmit={submit} noValidate data-testid="signin-form">
      <Field label={t("identifierLabel")} htmlFor="login-id">
        <div className="input-wrap">
          <UserRound className="lead" />
          <input id="login-id" className="input" value={identifier} onChange={(e) => setIdentifier(e.target.value)} placeholder={t("identifierPlaceholder")}
            autoComplete="username" autoCapitalize="off" autoCorrect="off" spellCheck={false} />
        </div>
      </Field>
      <Field label={t("passwordLabel")} htmlFor="login-pw">
        <PasswordInput id="login-pw" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" icon={<Lock className="lead" />} />
      </Field>
      <label className="check"><input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />{t("keepSignedIn")}</label>
      {lockLeft > 0 && (
        <div className="notice danger" role="alert" data-testid="lock-notice">
          <ShieldAlert /><div><strong>{t("lockedTitle")}</strong>{t("lockedBody", { time: formatCountdown(lockLeft) })}</div>
        </div>
      )}
      <FieldError>{error}</FieldError>
      <button className="btn btn-primary btn-block" type="submit" disabled={busy || lockLeft > 0} data-testid="signin-submit">
        {busy ? <><Spinner />{t("signingIn")}</> : <>{t("btnSignIn")}<LogIn /></>}
      </button>
      <div className="caption" style={{ textAlign: "center" }}><ShieldCheck width={14} height={14} style={{ verticalAlign: -2 }} /> {t("passwordSafe")}</div>
    </form>
  );
}

type Avail = "idle" | "checking" | "ok" | "taken" | "invalid";

function SignUpForm() {
  const { t, lang } = useI18n();
  const { signUp } = useAuth();
  const after = useAfterAuth();
  const errText = useErrorText();
  const [f, setF] = useState({ fullName: "", username: "", phone: "", email: "", password: "", confirm: "", language: lang as Lang, terms: false });
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [busy, setBusy] = useState(false);
  const [serverError, setServerError] = useState("");
  const [avail, setAvail] = useState<Avail>("idle");
  const debounce = useRef<number>();

  const set = <K extends keyof typeof f>(k: K, v: (typeof f)[K]) => setF((s) => ({ ...s, [k]: v }));
  const uname = f.username.trim().toLowerCase();

  useEffect(() => {
    window.clearTimeout(debounce.current);
    if (!uname) return setAvail("idle");
    if (!USERNAME_RE.test(uname)) return setAvail("invalid");
    setAvail("checking");
    debounce.current = window.setTimeout(async () => {
      try {
        const r = await api<{ available: boolean }>(`${API}/auth/availability`, { query: { field: "username", value: uname }, auth: false });
        setAvail(r.available ? "ok" : "taken");
      } catch {
        setAvail("idle");
      }
    }, 450);
  }, [uname]);

  const errors = {
    fullName: f.fullName.trim().length < 2 ? t("errNameShort") : "",
    username: avail === "invalid" || !uname ? t("usernameInvalid") : avail === "taken" ? t("usernameTaken") : "",
    contact: !f.phone.trim() && !f.email.trim() ? t("errContact") : "",
    phone: f.phone.trim() && !normalizePhone(f.phone) ? t("errPhone") : "",
    email: f.email.trim() && !isEmail(f.email) ? t("errEmail") : "",
    password: !passwordOk(f.password, uname) ? t("errPasswordWeak") : "",
    confirm: f.confirm !== f.password ? t("errPasswordMatch") : "",
    terms: !f.terms ? t("errTerms") : "",
  };
  const show = (k: keyof typeof errors) => (touched[k] || touched.submit ? errors[k] : "");

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setTouched((s) => ({ ...s, submit: true }));
    setServerError("");
    if (Object.values(errors).some(Boolean)) return;
    setBusy(true);
    try {
      const user = await signUp({
        full_name: f.fullName.trim(), username: uname, phone: f.phone.trim() || null, email: f.email.trim() || null,
        password: f.password, confirm_password: f.confirm, preferred_language: f.language, accept_terms: f.terms, remember: true,
      });
      after(user.preferred_language);
    } catch (err) {
      setServerError(errText(err));
    } finally {
      setBusy(false);
    }
  };
  const blur = (k: string) => () => setTouched((s) => ({ ...s, [k]: true }));

  return (
    <form className="stack" onSubmit={submit} noValidate data-testid="signup-form">
      <Field label={t("fullNameLabel")} required error={show("fullName")} htmlFor="su-name">
        <input id="su-name" className={`input ${show("fullName") ? "invalid" : ""}`} value={f.fullName} onChange={(e) => set("fullName", e.target.value)}
          onBlur={blur("fullName")} placeholder={t("fullNamePlaceholder")} autoComplete="name" />
      </Field>
      <div className="field">
        <label className="label" htmlFor="su-user">{t("usernameLabel")} <span className="req" aria-hidden>*</span></label>
        <div className="input-wrap">
          <AtSign className="lead" />
          <input id="su-user" className={`input ${show("username") ? "invalid" : ""}`} value={f.username} onChange={(e) => set("username", e.target.value.toLowerCase())}
            onBlur={blur("username")} placeholder={t("usernamePlaceholder")} autoComplete="username" autoCapitalize="off" spellCheck={false} />
        </div>
        {avail === "ok" ? <span className="help" style={{ color: "var(--success)", fontWeight: 700 }} data-testid="username-ok"><Check width={14} height={14} style={{ verticalAlign: -2 }} /> {t("usernameAvailable")}</span>
          : avail === "taken" ? <span className="error-text" data-testid="username-taken"><X />{t("usernameTaken")}</span>
          : show("username") ? <FieldError>{show("username")}</FieldError>
          : <span className="help">{avail === "checking" ? t("loading") : t("usernameHint")}</span>}
      </div>
      <Field label={t("phoneLabel")} error={show("phone") || (touched.submit ? errors.contact : "")} help={t("contactHint")} htmlFor="su-phone">
        <div className="input-wrap">
          <Phone className="lead" />
          <input id="su-phone" className={`input ${show("phone") ? "invalid" : ""}`} value={f.phone} onChange={(e) => set("phone", e.target.value)}
            onBlur={blur("phone")} placeholder={t("phonePlaceholder")} inputMode="tel" autoComplete="tel" />
        </div>
      </Field>
      <Field label={<>{t("emailLabel")} <span className="caption">({t("optional")})</span></>} error={show("email")} htmlFor="su-email">
        <div className="input-wrap">
          <Mail className="lead" />
          <input id="su-email" className={`input ${show("email") ? "invalid" : ""}`} value={f.email} onChange={(e) => set("email", e.target.value)}
            onBlur={blur("email")} placeholder={t("emailPlaceholder")} inputMode="email" autoComplete="email" autoCapitalize="off" />
        </div>
      </Field>
      <div className="field">
        <label className="label" htmlFor="su-pw">{t("passwordLabel")} <span className="req" aria-hidden>*</span></label>
        <PasswordInput id="su-pw" value={f.password} onChange={(e) => set("password", e.target.value)} onBlur={blur("password")}
          autoComplete="new-password" invalid={!!show("password")} icon={<Lock className="lead" />} />
        <PasswordStrength password={f.password} username={uname} />
        <FieldError>{show("password")}</FieldError>
      </div>
      <Field label={t("confirmPasswordLabel")} required error={show("confirm")} htmlFor="su-confirm">
        <PasswordInput id="su-confirm" value={f.confirm} onChange={(e) => set("confirm", e.target.value)} onBlur={blur("confirm")}
          autoComplete="new-password" invalid={!!show("confirm")} />
      </Field>
      <div className="field">
        <span className="label">{t("languageLabel")}</span>
        <div className="segmented">
          <button type="button" className={f.language === "en" ? "active" : ""} onClick={() => set("language", "en")}>English</button>
          <button type="button" className={f.language === "kn" ? "active" : ""} onClick={() => set("language", "kn")}>ಕನ್ನಡ</button>
        </div>
      </div>
      <label className="check"><input type="checkbox" checked={f.terms} onChange={(e) => set("terms", e.target.checked)} data-testid="terms" />{t("termsLabel")}</label>
      <FieldError>{show("terms")}</FieldError>
      <FieldError>{serverError}</FieldError>
      <button className="btn btn-primary btn-block" type="submit" disabled={busy} data-testid="signup-submit">
        {busy ? <><Spinner />{t("creatingAccount")}</> : t("btnCreateAccount")}
      </button>
    </form>
  );
}
