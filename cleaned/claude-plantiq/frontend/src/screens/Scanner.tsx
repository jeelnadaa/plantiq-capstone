import { useEffect, useRef, useState } from "react";
import { Camera, Check, Focus, Image as ImageIcon, MapPin, MessagesSquare, RotateCcw, ScanLine, Sparkles, Sun, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { AppBar } from "../components/AppBar";
import { BottomNav } from "../components/BottomNav";
import { WeatherCard } from "../components/WeatherCard";
import { DiagnosisDetails } from "../components/DiagnosisCard";
import { VoiceButton } from "../components/VoiceButton";
import { OfflineBanner, Spinner, useErrorText } from "../components/common";
import { LeafArt } from "./Auth";
import { useI18n } from "../lib/i18n";
import { useAuth } from "../lib/auth";
import { useLocation2 } from "../lib/location";
import { API, api } from "../lib/api";
import { useToast } from "../lib/toast";
import type { Diagnosis, Handoff } from "../lib/types";

export const HANDOFF_KEY = "plantiq.handoff";

export function setHandoff(h: Handoff) {
  sessionStorage.setItem(HANDOFF_KEY, JSON.stringify(h));
}

export function Scanner() {
  const { t, lang } = useI18n();
  const { user } = useAuth();
  const nav = useNavigate();
  const toast = useToast();
  const errText = useErrorText();
  const { coords, env, hasCoords } = useLocation2();
  const camRef = useRef<HTMLInputElement>(null);
  const galRef = useRef<HTMLInputElement>(null);
  const resultRef = useRef<HTMLDivElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [step, setStep] = useState(0);
  const [result, setResult] = useState<Diagnosis | null>(null);

  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  useEffect(() => {
    if (!busy) return;
    setStep(1);
    const a = window.setTimeout(() => setStep(2), 900);
    const b = window.setTimeout(() => setStep(3), 1900);
    return () => { window.clearTimeout(a); window.clearTimeout(b); };
  }, [busy]);

  const pick = (f: File | undefined) => {
    if (!f) return;
    if (!/^image\//.test(f.type) && !/\.(jpe?g|png|webp)$/i.test(f.name)) {
      toast.show(t("pickPhotoFirst"), "error");
      return;
    }
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
  };

  const clear = () => {
    setFile(null);
    setPreview("");
    setQuestion("");
    setResult(null);
    if (camRef.current) camRef.current.value = "";
    if (galRef.current) galRef.current.value = "";
  };

  const analyze = async () => {
    if (!file) {
      toast.show(t("pickPhotoFirst"), "error");
      return;
    }
    setBusy(true);
    try {
      const form = new FormData();
      form.append("file", file, file.name || "leaf.jpg");
      form.append("language", lang);
      if (question.trim()) form.append("user_question", question.trim());
      if (hasCoords) {
        form.append("latitude", String(coords.lat));
        form.append("longitude", String(coords.lng));
      }
      const d = await api<Diagnosis>(`${API}/predict`, { form, timeoutMs: 120000 });
      setResult(d);
      window.setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
    } catch (e) {
      toast.show(t("scanFailed", { reason: errText(e) }), "error");
    } finally {
      setBusy(false);
      setStep(0);
    }
  };

  const askInChat = () => {
    if (!result) return;
    const mediaId = result.image_url?.split("/").pop()?.replace(/\.jpg$/, "") ?? null;
    setHandoff({ disease: result.disease, confidence: result.confidence, advisory: result.advisory, imageUrl: result.image_url, mediaId, env: result.env_data });
    nav("/chat");
  };

  const firstName = (user?.full_name || user?.username || "").split(" ")[0];

  return (
    <div className="screen" data-testid="scanner">
      <AppBar />
      <main className="screen-body">
        <OfflineBanner />
        {!file && (
          <>
            <div>
              <div className="eyebrow">{t("greeting", { name: firstName })}</div>
              <h1 className="h2">{t("scanQuestion")}</h1>
            </div>
            <section className="hero-scan">
              <LeafArt />
              <h2 className="h1">{t("scanHeroTitle")}</h2>
              <p>{t("scanHeroSub")}</p>
              <div className="hero-actions">
                <button className="btn" onClick={() => camRef.current?.click()} data-testid="btn-camera"><Camera />{t("btnCamera")}</button>
                <button className="btn secondary" onClick={() => galRef.current?.click()} data-testid="btn-gallery"><ImageIcon />{t("btnGallery")}</button>
              </div>
            </section>
            <div className="steps" aria-hidden>
              <div className="step"><div className="step-ico"><Sun /></div>{t("tipLight")}</div>
              <div className="step"><div className="step-ico"><ScanLine /></div>{t("tipOneLeaf")}</div>
              <div className="step"><div className="step-ico"><Focus /></div>{t("tipSteady")}</div>
            </div>
          </>
        )}
        <input ref={camRef} type="file" accept="image/*" capture="environment" hidden onChange={(e) => pick(e.target.files?.[0])} data-testid="camera-input" />
        <input ref={galRef} type="file" accept="image/jpeg,image/png,image/webp" hidden onChange={(e) => pick(e.target.files?.[0])} data-testid="file-input" />

        {file && (
          <>
            <div className="preview">
              <img src={preview} alt={t("photoReady")} />
              <button className="remove" onClick={clear} aria-label={t("removePhoto")} data-testid="remove-photo"><X /></button>
              <span className="tag badge badge-neutral"><ImageIcon />{file.name.slice(0, 28)}</span>
            </div>
            {!result && (
              <>
                <div className="field">
                  <label className="label" htmlFor="scan-q">{t("questionLabel")} <span className="caption">({t("optional")})</span></label>
                  <div className="row">
                    <input id="scan-q" className="input grow" value={question} maxLength={500} onChange={(e) => setQuestion(e.target.value)} placeholder={t("questionPlaceholder")} />
                    <VoiceButton onText={(txt) => setQuestion(txt)} />
                  </div>
                  <div className="chips">
                    {(["quickWhen", "quickOrganic", "quickDose"] as const).map((k) => (
                      <button type="button" key={k} className={`chip ${question === t(k) ? "active" : ""}`} onClick={() => setQuestion(t(k))}>{t(k)}</button>
                    ))}
                  </div>
                </div>
                <div className="row">
                  <span className={`badge ${env?.available ? "badge-primary" : "badge-neutral"}`}><MapPin />{env?.available ? t("usingWeather") : t("noWeatherUsed")}</span>
                  {env?.region_name && <span className="caption">{env.region_name}</span>}
                </div>
                <button className="btn btn-primary btn-xl btn-block" onClick={analyze} disabled={busy} data-testid="analyze">
                  {busy ? <><Spinner />{t("checking")}</> : <><Sparkles />{t("btnCheckLeaf")}</>}
                </button>
                {busy && (
                  <div className="card tonal stack-sm" role="status" aria-live="polite">
                    {(["step1", "step2", "step3"] as const).map((k, i) => (
                      <div key={k} className="row" style={{ opacity: step >= i + 1 ? 1 : 0.45 }}>
                        {step > i + 1 ? <Check width={18} color="var(--success)" /> : step === i + 1 ? <Spinner size={18} /> : <span style={{ width: 18 }} />}
                        <span className="body-sm">{t(k)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </>
        )}

        {result && (
          <div ref={resultRef} className="stack">
            <DiagnosisDetails
              disease={result.disease} confidence={result.confidence} isHealthy={result.is_healthy} isBlended={result.is_blended}
              distribution={result.distribution} advisory={result.advisory} citations={result.citations} safety={result.safety_audit}
              latin={result.latin_name} provider={result.provider} cacheHit={result.cache_hit} env={result.env_data}
              question={question || null} riskLevel={result.env_data?.risk_level}
            />
            <div className="grid-2">
              <button className="btn btn-primary" onClick={askInChat} data-testid="ask-in-chat"><MessagesSquare />{t("btnAskMore")}</button>
              <button className="btn btn-outline" onClick={clear} data-testid="new-scan"><RotateCcw />{t("btnNewScan")}</button>
            </div>
          </div>
        )}

        {!result && <WeatherCard />}
      </main>
      <BottomNav />
    </div>
  );
}
