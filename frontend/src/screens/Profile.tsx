import { useEffect, useState } from "react";
import { ChevronRight, Info, KeyRound, Languages, LogOut, Moon, Palette, Pencil, Server, Smartphone, UserRound, UserX } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { AppBar } from "../components/AppBar";
import { BottomNav } from "../components/BottomNav";
import { Sheet } from "../components/Sheet";
import { ServerSettings } from "../components/modals/ServerSettings";
import { PalettePicker } from "../components/modals/PalettePicker";
import { Field, FieldError, PasswordInput, PasswordStrength, Spinner, useErrorText } from "../components/common";
import { useI18n } from "../lib/i18n";
import { useAuth } from "../lib/auth";
import { useTheme } from "../lib/theme";
import { API, api, getServerUrl, saveSession, type TokenResponse, type User } from "../lib/api";
import { useToast } from "../lib/toast";
import { timeAgo } from "../lib/format";
import { isEmail, normalizePhone, passwordOk } from "../lib/validation";
import type { Session, Stats } from "../lib/types";
import type { TKey } from "../lib/i18n/en";

export const APP_VERSION = "3.0.0";

export function Profile() {
  const { t, lang, setLang } = useI18n();
  const { user, signOut } = useAuth();
  const { dark, toggleDark, palette } = useTheme();
  const nav = useNavigate();
  const [stats, setStats] = useState<Stats | null>(null);
  const [sheet, setSheet] = useState<"" | "edit" | "password" | "devices" | "delete" | "server" | "palette" | "about">("");

  useEffect(() => {
    api<Stats>(`${API}/users/me/stats`).then(setStats).catch(() => undefined);
  }, []);

  const initials = (user?.full_name || user?.username || "?").split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase();
  const paletteName = t(`palette${palette.charAt(0).toUpperCase()}${palette.slice(1)}` as TKey);
  const changeLang = async () => {
    const next = lang === "en" ? "kn" : "en";
    setLang(next);
    api(`${API}/users/me`, { method: "PATCH", body: { preferred_language: next } }).catch(() => undefined);
  };

  return (
    <div className="screen" data-testid="profile">
      <AppBar title={t("profileTitle")} icon={<UserRound />} minimal />
      <main className="screen-body">
        <section className="card stack">
          <div className="profile-hero">
            <div className="avatar-lg" aria-hidden>{initials}</div>
            <div className="grow" style={{ minWidth: 0 }}>
              <div className="h3" data-testid="profile-name">{user?.full_name}</div>
              <div className="caption">@{user?.username}{user?.phone ? ` · ${user.phone.replace(/(\d{5})(\d{5})/, "$1 $2")}` : ""}</div>
              {user?.email && <div className="caption">{user.email}</div>}
            </div>
            <button className="icon-btn" onClick={() => setSheet("edit")} aria-label={t("editProfile")} data-testid="edit-profile"><Pencil /></button>
          </div>
          <div className="stats" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
            <div className="stat"><b data-testid="stat-scans">{stats?.scans ?? "–"}</b><span>{t("scansStat")}</span></div>
            <div className="stat"><b data-testid="stat-lots">{stats?.listings ?? "–"}</b><span>{t("lotsStat")}</span></div>
            <div className="stat"><b>{stats?.chats ?? "–"}</b><span>{t("chatsStat")}</span></div>
          </div>
        </section>

        <div className="eyebrow">{t("sectionApp")}</div>
        <div className="menu">
          <button className="menu-item" onClick={changeLang} data-testid="menu-language"><span className="mi-ico"><Languages /></span>{t("language")}<span className="mi-val">{lang === "en" ? "English" : "ಕನ್ನಡ"}</span></button>
          <button className="menu-item" onClick={toggleDark} role="switch" aria-checked={dark} data-testid="menu-dark"><span className="mi-ico"><Moon /></span>{t("darkMode")}<span className="mi-val">{dark ? t("on") : t("off")}</span></button>
          <button className="menu-item" onClick={() => setSheet("palette")}><span className="mi-ico"><Palette /></span>{t("colourTheme")}<span className="mi-val">{paletteName}</span></button>
          <button className="menu-item" onClick={() => setSheet("server")}><span className="mi-ico"><Server /></span>{t("server")}<span className="mi-val" style={{ maxWidth: 150, overflow: "hidden", textOverflow: "ellipsis" }}>{(getServerUrl() || window.location.host).replace(/^https?:\/\//, "")}</span></button>
        </div>

        <div className="eyebrow">{t("sectionSecurity")}</div>
        <div className="menu">
          <button className="menu-item" onClick={() => setSheet("password")} data-testid="menu-password"><span className="mi-ico"><KeyRound /></span>{t("changePassword")}<ChevronRight className="chev" /></button>
          <button className="menu-item" onClick={() => setSheet("devices")} data-testid="menu-devices"><span className="mi-ico"><Smartphone /></span>{t("devices")}<ChevronRight className="chev" /></button>
          <button className="menu-item" onClick={async () => { await signOut(); nav("/signin", { replace: true }); }} data-testid="sign-out"><span className="mi-ico"><LogOut /></span>{t("signOut")}</button>
          <button className="menu-item danger" onClick={() => setSheet("delete")} data-testid="menu-delete"><span className="mi-ico"><UserX /></span>{t("deleteAccount")}</button>
        </div>
        <button className="btn btn-ghost" onClick={() => setSheet("about")}><Info />{t("aboutTitle")} · {t("version", { v: APP_VERSION })}</button>
      </main>
      <BottomNav />

      <EditProfileSheet open={sheet === "edit"} onClose={() => setSheet("")} user={user} />
      <ChangePasswordSheet open={sheet === "password"} onClose={() => setSheet("")} username={user?.username ?? ""} />
      <DevicesSheet open={sheet === "devices"} onClose={() => setSheet("")} />
      <DeleteAccountSheet open={sheet === "delete"} onClose={() => setSheet("")} />
      <ServerSettings open={sheet === "server"} onClose={() => setSheet("")} />
      <PalettePicker open={sheet === "palette"} onClose={() => setSheet("")} />
      <Sheet open={sheet === "about"} onClose={() => setSheet("")} title={t("aboutTitle")} icon={<Info />}>
        <p className="body-sm">{t("aboutBody")}</p>
        <p className="caption">{t("version", { v: APP_VERSION })}</p>
      </Sheet>
    </div>
  );
}

function EditProfileSheet({ open, onClose, user }: { open: boolean; onClose: () => void; user: User | null }) {
  const { t } = useI18n();
  const { setUser } = useAuth();
  const toast = useToast();
  const errText = useErrorText();
  const [f, setF] = useState({ full_name: "", phone: "", email: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    if (open && user) { setF({ full_name: user.full_name, phone: user.phone ?? "", email: user.email ?? "" }); setError(""); }
  }, [open, user]);

  const save = async () => {
    if (f.full_name.trim().length < 2) return setError(t("errNameShort"));
    if (f.phone.trim() && !normalizePhone(f.phone)) return setError(t("errPhone"));
    if (f.email.trim() && !isEmail(f.email)) return setError(t("errEmail"));
    if (!f.phone.trim() && !f.email.trim()) return setError(t("errContact"));
    setBusy(true);
    try {
      const u = await api<User>(`${API}/users/me`, { method: "PATCH", body: { full_name: f.full_name.trim(), phone: f.phone.trim(), email: f.email.trim() } });
      setUser(u);
      toast.show(t("profileSaved"));
      onClose();
    } catch (e) {
      setError(errText(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Sheet open={open} onClose={onClose} title={t("editProfile")} icon={<Pencil />} testId="edit-profile-sheet">
      <div className="stack">
        <Field label={t("fullNameLabel")} htmlFor="ep-name"><input id="ep-name" className="input" value={f.full_name} onChange={(e) => setF({ ...f, full_name: e.target.value })} /></Field>
        <Field label={t("phoneLabel")} htmlFor="ep-phone"><input id="ep-phone" className="input" inputMode="tel" value={f.phone} onChange={(e) => setF({ ...f, phone: e.target.value })} /></Field>
        <Field label={t("emailLabel")} htmlFor="ep-email"><input id="ep-email" className="input" inputMode="email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></Field>
        <FieldError>{error}</FieldError>
        <button className="btn btn-primary btn-block" onClick={save} disabled={busy}>{busy ? <Spinner /> : null}{t("save")}</button>
      </div>
    </Sheet>
  );
}

function ChangePasswordSheet({ open, onClose, username }: { open: boolean; onClose: () => void; username: string }) {
  const { t } = useI18n();
  const { acceptSession } = useAuth();
  const toast = useToast();
  const errText = useErrorText();
  const [f, setF] = useState({ current: "", next: "", confirm: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => { if (open) { setF({ current: "", next: "", confirm: "" }); setError(""); } }, [open]);

  const save = async () => {
    if (!f.current) return setError(t("errFillLogin"));
    if (!passwordOk(f.next, username)) return setError(t("errPasswordWeak"));
    if (f.next !== f.confirm) return setError(t("errPasswordMatch"));
    setBusy(true);
    try {
      const tok = await api<TokenResponse>(`${API}/users/me/password`, { body: { current_password: f.current, new_password: f.next, confirm_password: f.confirm } });
      saveSession(tok);
      acceptSession(tok);
      toast.show(t("passwordChanged"));
      onClose();
    } catch (e) {
      setError(errText(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Sheet open={open} onClose={onClose} title={t("changePassword")} icon={<KeyRound />} testId="password-sheet">
      <div className="stack">
        <Field label={t("currentPassword")} htmlFor="cp-cur"><PasswordInput id="cp-cur" value={f.current} onChange={(e) => setF({ ...f, current: e.target.value })} autoComplete="current-password" /></Field>
        <div className="field">
          <label className="label" htmlFor="cp-new">{t("newPassword")}</label>
          <PasswordInput id="cp-new" value={f.next} onChange={(e) => setF({ ...f, next: e.target.value })} autoComplete="new-password" />
          <PasswordStrength password={f.next} username={username} />
        </div>
        <Field label={t("confirmPasswordLabel")} htmlFor="cp-conf"><PasswordInput id="cp-conf" value={f.confirm} onChange={(e) => setF({ ...f, confirm: e.target.value })} autoComplete="new-password" /></Field>
        <FieldError>{error}</FieldError>
        <button className="btn btn-primary btn-block" onClick={save} disabled={busy}>{busy ? <Spinner /> : null}{t("save")}</button>
      </div>
    </Sheet>
  );
}

function DevicesSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { t, lang } = useI18n();
  const { signOut } = useAuth();
  const nav = useNavigate();
  const toast = useToast();
  const errText = useErrorText();
  const [sessions, setSessions] = useState<Session[] | null>(null);
  const load = () => api<Session[]>(`${API}/auth/sessions`).then(setSessions).catch(() => setSessions([]));
  useEffect(() => { if (open) { setSessions(null); load(); } }, [open]);

  const revoke = async (s: Session) => {
    try {
      await api(`${API}/auth/sessions/${s.id}`, { method: "DELETE" });
      toast.show(t("deviceSignedOut"));
      if (s.current) { await signOut(); nav("/signin", { replace: true }); return; }
      load();
    } catch (e) {
      toast.show(errText(e), "error");
    }
  };

  return (
    <Sheet open={open} onClose={onClose} title={t("devices")} icon={<Smartphone />} testId="devices-sheet">
      <div className="stack">
        {sessions === null ? <Spinner /> : (
          <div className="menu">
            {sessions.map((s) => (
              <div className="menu-item" key={s.id} style={{ paddingTop: 8, paddingBottom: 8 }}>
                <span className="mi-ico"><Smartphone /></span>
                <div className="grow" style={{ minWidth: 0 }}>
                  <div>{s.device}{s.current && <span className="badge badge-primary" style={{ marginLeft: 6 }}>{t("thisDevice")}</span>}</div>
                  <div className="caption">{t("lastActive", { when: timeAgo(lang, s.last_used_at) })}{s.ip ? ` · ${s.ip}` : ""}</div>
                </div>
                <button className="btn btn-sm btn-outline" onClick={() => revoke(s)}>{t("signOutDevice")}</button>
              </div>
            ))}
          </div>
        )}
        <button className="btn btn-danger-outline btn-block" onClick={async () => { await signOut(true); nav("/signin", { replace: true }); }} data-testid="sign-out-all">
          <LogOut />{t("signOutAll")}
        </button>
      </div>
    </Sheet>
  );
}

function DeleteAccountSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { t } = useI18n();
  const { signOut } = useAuth();
  const nav = useNavigate();
  const toast = useToast();
  const errText = useErrorText();
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => { if (open) { setPassword(""); setError(""); } }, [open]);

  const confirm = async () => {
    if (!password) return setError(t("errFillLogin"));
    setBusy(true);
    try {
      await api(`${API}/users/me`, { method: "DELETE", body: { password } });
      toast.show(t("accountDeleted"));
      await signOut();
      nav("/signup", { replace: true });
    } catch (e) {
      setError(errText(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Sheet open={open} onClose={onClose} title={t("deleteAccountTitle")} icon={<UserX />} iconTone="danger" center testId="delete-account-sheet">
      <div className="stack">
        <p className="body-sm" style={{ margin: 0 }}>{t("deleteAccountBody")}</p>
        <PasswordInput value={password} onChange={(e) => setPassword(e.target.value)} placeholder={t("passwordLabel")} aria-label={t("passwordLabel")} autoComplete="current-password" />
        <FieldError>{error}</FieldError>
        <div className="grid-2">
          <button className="btn btn-outline" onClick={onClose}>{t("cancel")}</button>
          <button className="btn btn-danger" onClick={confirm} disabled={busy} data-testid="confirm-delete-account">{busy ? <Spinner /> : null}{t("deleteAccountConfirm")}</button>
        </div>
      </div>
    </Sheet>
  );
}
