import { useEffect, useState } from "react";
import { Activity, Lightbulb, Save, Server, ShieldAlert, Wifi, WifiOff } from "lucide-react";
import { Sheet } from "../Sheet";
import { Spinner } from "../common";
import { useI18n } from "../../lib/i18n";
import { apiBase, getServerUrl, isPrivateHost, normalizeServerUrl, pingServer, setServerUrl } from "../../lib/api";
import { useToast } from "../../lib/toast";

type Result = { state: "idle" | "testing" | "ok" | "http" | "down" | "empty"; ms?: number; version?: string; status?: number; url?: string };

export function useServerTester() {
  const [result, setResult] = useState<Result>({ state: "idle" });
  const test = async (value: string) => {
    const url = normalizeServerUrl(value);
    if (!url) {
      setResult({ state: "empty" });
      return false;
    }
    setResult({ state: "testing", url });
    const r = await pingServer(url);
    setResult(r.ok ? { state: "ok", ms: r.ms, version: r.version, url } : r.status ? { state: "http", status: r.status, url } : { state: "down", url });
    return r.ok;
  };
  return { result, test, setResult };
}

export function ServerTestResult({ result }: { result: Result }) {
  const { t } = useI18n();
  if (result.state === "idle") return null;
  if (result.state === "testing")
    return <div className="notice info" role="status"><Spinner /><div>{t("testing", { url: result.url ?? "" })}</div></div>;
  if (result.state === "ok")
    return (
      <div className="notice ok" role="status" data-testid="server-ok">
        <Wifi /><div><strong>{t("connectedMs", { ms: result.ms ?? 0 })}</strong>{t("serverOnline", { version: result.version ?? "" })}</div>
      </div>
    );
  if (result.state === "empty") return <div className="notice warn" role="alert"><ShieldAlert /><div>{t("serverEmpty")}</div></div>;
  if (result.state === "http") return <div className="notice warn" role="alert"><ShieldAlert /><div>{t("serverHttp", { status: result.status ?? 0 })}</div></div>;
  return <div className="notice danger" role="alert" data-testid="server-down"><WifiOff /><div>{t("serverUnreachable", { url: result.url ?? "" })}</div></div>;
}

export function InsecureHint({ value }: { value: string }) {
  const { t } = useI18n();
  const url = normalizeServerUrl(value);
  if (!url.startsWith("http://")) return null;
  try {
    if (isPrivateHost(new URL(url).hostname)) return null;
  } catch {
    return null;
  }
  return <div className="notice warn"><ShieldAlert /><div>{t("serverInsecure")}</div></div>;
}

export function ServerSettings({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { t } = useI18n();
  const toast = useToast();
  const [value, setValue] = useState("");
  const { result, test, setResult } = useServerTester();

  useEffect(() => {
    if (open) {
      setValue(getServerUrl() || apiBase() || window.location.origin);
      setResult({ state: "idle" });
    }
  }, [open, setResult]);

  const save = async () => {
    const ok = await test(value);
    if (!normalizeServerUrl(value)) return;
    setServerUrl(value);
    toast.show(t("serverSaved"), ok ? "ok" : "error");
    if (ok) onClose();
  };

  return (
    <Sheet open={open} onClose={onClose} title={t("serverModalTitle")} icon={<Server />} testId="server-sheet">
      <div className="stack">
        <p className="body-sm" style={{ margin: 0 }}>{t("serverModalDesc")}</p>
        <div className="field">
          <label className="label" htmlFor="server-url">{t("serverLabel")}</label>
          <div className="input-wrap">
            <Server className="lead" />
            <input id="server-url" className="input" value={value} onChange={(e) => setValue(e.target.value)} placeholder={t("serverPlaceholder")}
              inputMode="url" autoCapitalize="off" autoCorrect="off" spellCheck={false} onKeyDown={(e) => e.key === "Enter" && save()} />
          </div>
          <span className="help">{t("serverHint")}</span>
        </div>
        <InsecureHint value={value} />
        <ServerTestResult result={result} />
        <div className="grid-2">
          <button className="btn btn-outline" onClick={() => test(value)} disabled={result.state === "testing"}><Activity />{t("btnTest")}</button>
          <button className="btn btn-primary" onClick={save} disabled={result.state === "testing"}><Save />{t("btnSaveConnect")}</button>
        </div>
        <button className="btn btn-ghost" onClick={() => { setServerUrl(""); setValue(window.location.origin); toast.show(t("serverResetDone")); onClose(); }}>
          {t("btnResetDefault")}
        </button>
        <div className="card tonal stack-sm">
          <div className="card-title" style={{ margin: 0 }}><Lightbulb />{t("tipsTitle")}</div>
          <div className="body-sm">• {t("tip1")}<br />• {t("tip2")}<br />• {t("tip3")}</div>
        </div>
      </div>
    </Sheet>
  );
}
