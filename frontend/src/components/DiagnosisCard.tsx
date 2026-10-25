import { BarChart3, BookOpen, Bug, ClipboardList, FileText, Leaf, ShieldAlert, ShieldCheck, TriangleAlert, WifiOff } from "lucide-react";
import { useI18n } from "../lib/i18n";
import { diseaseName, num } from "../lib/format";
import { resolveUrl } from "../lib/api";
import { Markdown } from "../lib/markdown";
import type { Citation, SafetyAudit } from "../lib/types";
import type { EnvData } from "../lib/location";
import { WeatherGrid } from "./WeatherCard";

type Props = {
  disease: string;
  confidence: number;
  isHealthy: boolean;
  isBlended: boolean;
  distribution: Record<string, number>;
  advisory: string;
  citations?: Citation[] | null;
  safety?: SafetyAudit | null;
  imageUrl?: string | null;
  latin?: string | null;
  provider?: string | null;
  cacheHit?: boolean;
  env?: EnvData | null;
  question?: string | null;
  riskLevel?: string;
};

export function ConfidenceRing({ value, tone }: { value: number; tone: "ok" | "bad" | "warn" }) {
  const color = tone === "ok" ? "var(--success)" : tone === "warn" ? "var(--warning)" : "var(--danger)";
  return (
    <div className="conf-ring" style={{ ["--v" as string]: Math.min(100, value), ["--ring" as string]: color }} role="img" aria-label={`${num(value)}%`}>
      <div>{num(value, 0)}%</div>
    </div>
  );
}

export function DiagnosisSummary({ disease, confidence, isHealthy, isBlended, imageUrl, latin }: Pick<Props, "disease" | "confidence" | "isHealthy" | "isBlended" | "imageUrl" | "latin">) {
  const { t, lang } = useI18n();
  const pest = disease === "Miner";
  return (
    <div className="diag-head">
      {imageUrl && <img className="diag-thumb" src={resolveUrl(imageUrl)} alt="" />}
      <div className="grow">
        <span className={`badge ${isHealthy ? "badge-healthy" : "badge-disease"}`}>
          {isHealthy ? <Leaf /> : <Bug />}{isHealthy ? t("healthyFound") : pest ? t("pestFound") : t("diseaseFound")}
        </span>
        <div className="h2" style={{ marginTop: 6 }} data-testid="diagnosis-name">{diseaseName(lang, disease)}</div>
        {latin && <div className="caption"><i>{latin}</i></div>}
      </div>
      <ConfidenceRing value={confidence} tone={isHealthy ? "ok" : isBlended ? "warn" : "bad"} />
    </div>
  );
}

export function Probabilities({ distribution }: { distribution: Record<string, number> }) {
  const { t, lang } = useI18n();
  const entries = Object.entries(distribution).sort((a, b) => b[1] - a[1]);
  const top = entries[0]?.[0];
  return (
    <section className="card" aria-labelledby="probs">
      <h3 className="card-title" id="probs"><BarChart3 />{t("howSure")}</h3>
      <div className="prob-list">
        {entries.map(([k, v]) => (
          <div className={`prob ${k === top ? "top" : ""}`} key={k}>
            <span>{diseaseName(lang, k, true)}</span>
            <span className="num">{num(v)}%</span>
            <div className="bar" aria-hidden><i style={{ width: `${Math.max(0.5, Math.min(100, v))}%` }} /></div>
          </div>
        ))}
      </div>
    </section>
  );
}

export function Sources({ citations }: { citations: Citation[] }) {
  const { t } = useI18n();
  if (!citations.length) return null;
  return (
    <section className="card" aria-labelledby="sources">
      <h3 className="card-title" id="sources"><BookOpen />{t("sourcesTitle")}</h3>
      <div className="sources">
        {citations.map((c, i) => (
          <div className="source" key={`${c.source}-${i}`}>
            <FileText />
            <div className="grow"><b>{c.title || c.source}</b>{c.page ? ` · ${t("page", { n: c.page })}` : ""}</div>
            {c.score != null && <span className="badge badge-primary">{num(c.score, 2)}</span>}
          </div>
        ))}
      </div>
    </section>
  );
}

export function DiagnosisDetails(p: Props) {
  const { t } = useI18n();
  const urgent = !p.isHealthy && !p.isBlended && (p.riskLevel === "high" || p.riskLevel === "moderate");
  return (
    <div className="stack" data-testid="diagnosis">
      <section className="card stack">
        <DiagnosisSummary {...p} />
        {p.cacheHit && <div className="caption">{t("cachedNote")}</div>}
        {p.isBlended && (
          <div className="notice warn" data-testid="blended-notice"><TriangleAlert /><div><strong>{t("lowCertainty")}</strong>{t("lowCertaintyBody")}</div></div>
        )}
        {urgent && <div className="notice danger"><TriangleAlert /><div><strong>{t("actSoon")}</strong>{t("actSoonBody")}</div></div>}
        {p.question && <div className="caption"><b>{t("questionAsked")}:</b> {p.question}</div>}
      </section>
      <section className="card" aria-labelledby="todo">
        <h3 className="card-title" id="todo"><ClipboardList />{t("whatToDo")}</h3>
        {p.provider === "offline" && <span className="badge badge-neutral" style={{ marginBottom: 8 }}><WifiOff />{t("offlineAdvice")}</span>}
        <Markdown text={p.advisory} />
        {p.safety && (
          p.safety.verified
            ? <div className="notice ok" style={{ marginTop: 10 }}><ShieldCheck /><div><strong>{t("dosesChecked")}</strong>{p.safety.safety_note}</div></div>
            : <div className="notice warn" style={{ marginTop: 10 }} data-testid="dose-warning"><ShieldAlert /><div><strong>{t("dosesUnverified")}</strong>{p.safety.safety_note}</div></div>
        )}
      </section>
      <Probabilities distribution={p.distribution} />
      {p.env?.available && (
        <section className="card stack">
          <h3 className="card-title" style={{ margin: 0 }}>{t("weatherAtScan")}</h3>
          <WeatherGrid env={p.env} />
        </section>
      )}
      <Sources citations={p.citations ?? []} />
    </div>
  );
}
