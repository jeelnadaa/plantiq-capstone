import { useState } from "react";
import { Activity, ArrowRight, Languages, Lightbulb, Server, Sprout } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useI18n } from "../lib/i18n";
import { getServerUrl, setServerUrl } from "../lib/api";
import { InsecureHint, ServerTestResult, useServerTester } from "../components/modals/ServerSettings";
import { LeafArt } from "./Auth";

/** First launch in the APK: ask where the PlantIQ backend runs (LAN laptop, tunnel or cloud). */
export function ServerSetup() {
  const { t, toggle } = useI18n();
  const nav = useNavigate();
  const [value, setValue] = useState(getServerUrl());
  const { result, test } = useServerTester();

  const proceed = async () => {
    const ok = await test(value);
    if (ok) {
      setServerUrl(value);
      nav("/signin", { replace: true });
    }
  };

  return (
    <div className="screen" data-testid="server-setup">
      <div className="auth-hero">
        <LeafArt />
        <div className="row-between">
          <div className="row"><div className="brand-mark" style={{ background: "rgba(255,255,255,.18)" }}><Sprout /></div><b style={{ fontSize: "1.25rem" }}>PlantIQ</b></div>
          <button className="lang-pill" style={{ background: "rgba(255,255,255,.16)", borderColor: "rgba(255,255,255,.3)", color: "inherit" }} onClick={toggle}>
            <Languages />{t("langToggle")}
          </button>
        </div>
        <h1 className="h1" style={{ marginTop: 22 }}>{t("serverSetupTitle")}</h1>
        <p>{t("serverSetupSub")}</p>
      </div>
      <div className="screen-body no-nav">
        <div className="card stack">
          <div className="field">
            <label className="label" htmlFor="setup-url">{t("serverLabel")}</label>
            <div className="input-wrap">
              <Server className="lead" />
              <input id="setup-url" className="input" value={value} onChange={(e) => setValue(e.target.value)} placeholder={t("serverPlaceholder")}
                inputMode="url" autoCapitalize="off" autoCorrect="off" spellCheck={false} onKeyDown={(e) => e.key === "Enter" && proceed()} />
            </div>
            <span className="help">{t("serverHint")}</span>
          </div>
          <InsecureHint value={value} />
          <ServerTestResult result={result} />
          <div className="grid-2">
            <button className="btn btn-outline" onClick={() => test(value)} disabled={result.state === "testing"}><Activity />{t("btnTest")}</button>
            <button className="btn btn-primary" onClick={proceed} disabled={result.state === "testing"} data-testid="setup-continue">{t("btnContinue")}<ArrowRight /></button>
          </div>
        </div>
        <div className="card tonal stack-sm">
          <div className="card-title" style={{ margin: 0 }}><Lightbulb />{t("tipsTitle")}</div>
          <div className="body-sm">• {t("tip1")}<br />• {t("tip2")}<br />• {t("tip3")}</div>
        </div>
      </div>
    </div>
  );
}
