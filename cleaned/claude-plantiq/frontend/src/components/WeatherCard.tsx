import { useState } from "react";
import { CircleHelp, CloudRain, Crosshair, Droplets, MapPin, Mountain, Pencil, RefreshCw, ShieldCheck, SprayCan, Thermometer, TriangleAlert, Umbrella } from "lucide-react";
import { useI18n } from "../lib/i18n";
import { useLocation2, type EnvData } from "../lib/location";
import { num } from "../lib/format";
import { GmapsGuide } from "./modals/GmapsGuide";
import { Spinner } from "./common";
import type { TKey } from "../lib/i18n/en";

export function RiskBanner({ env }: { env: EnvData | null }) {
  const { t } = useI18n();
  const level = env?.available ? env.risk_level ?? "none" : "none";
  const map: Record<string, [TKey, TKey]> = {
    high: ["riskHigh", "riskHighBody"], moderate: ["riskModerate", "riskModerateBody"], low: ["riskLow", "riskLowBody"], none: ["riskNone", "riskNoneBody"],
  };
  const [title, body] = map[level];
  const Icon = level === "low" ? ShieldCheck : level === "none" ? CircleHelp : TriangleAlert;
  return (
    <div className={`risk ${level}`} role="status" data-testid="risk-banner" data-level={level}>
      <div className="risk-ico"><Icon /></div>
      <div className="grow">
        <b>{t(title)}</b>
        <div className="caption" style={{ color: "var(--ink-2)" }}>{t(body)}</div>
        {level !== "none" && <div className="risk-meter" aria-hidden><span /><span /><span /></div>}
      </div>
    </div>
  );
}

function humidityWord(h?: number | null): TKey | null {
  if (h == null) return null;
  return h >= 80 ? "veryHumid" : h >= 60 ? "humid" : "dry";
}
function rainWord(r?: number | null): TKey | null {
  if (r == null) return null;
  return r <= 0 ? "noRain" : r < 7.5 ? "lightRain" : "heavyRain";
}

export function WeatherGrid({ env }: { env: EnvData }) {
  const { t } = useI18n();
  const hw = humidityWord(env.humidity);
  const rw = rainWord(env.rainfall);
  return (
    <div className="weather-grid" data-testid="weather-grid">
      <div className="metric"><span className="m-label"><Thermometer />{t("temperature")}</span>
        <span className="m-value">{num(env.temperature)}<small>°C</small></span>
        <span className="m-sub">{env.feels_like != null ? t("feelsLike", { v: num(env.feels_like, 0) }) : "—"}</span></div>
      <div className="metric"><span className="m-label"><Droplets />{t("humidity")}</span>
        <span className="m-value">{num(env.humidity, 0)}<small>%</small></span><span className="m-sub">{hw ? t(hw) : "—"}</span></div>
      <div className="metric"><span className="m-label"><CloudRain />{t("rain24")}</span>
        <span className="m-value">{num(env.rainfall)}<small> mm</small></span><span className="m-sub">{rw ? t(rw) : "—"}</span></div>
      <div className="metric"><span className="m-label"><Mountain />{t("elevation")}</span>
        <span className="m-value">{num(env.elevation, 0)}<small> m</small></span>
        <span className="m-sub">{env.soil_ph != null ? t("soilPh", { v: env.soil_ph }) : "—"}</span></div>
    </div>
  );
}

export function SprayAndForecast({ env }: { env: EnvData }) {
  const { t, lang } = useI18n();
  const days = env.forecast ?? [];
  return (
    <>
      {env.spray_window && (
        <div className="notice info" data-testid="spray-window">
          <SprayCan />
          <div><strong>{t("sprayWindow")}</strong>{lang === "kn" ? env.spray_window.advice_kn : env.spray_window.advice_en}</div>
        </div>
      )}
      {days.length > 0 && (
        <div>
          <div className="eyebrow" style={{ marginBottom: 6 }}>{t("forecast3")}</div>
          <div className="forecast">
            {days.slice(0, 3).map((d, i) => (
              <div className="day" key={d.date}>
                <span>{i === 0 ? t("today") : (lang === "kn" ? d.weekday_kn : d.weekday_en.slice(0, 3))}</span>
                {(d.rain_probability ?? 0) >= 40 ? <Umbrella /> : <CloudRain style={{ opacity: 0.35 }} />}
                <strong>{d.rain_probability != null ? `${num(d.rain_probability, 0)}%` : "—"}</strong>
                <span className="caption">{num(d.t_min, 0)}–{num(d.t_max, 0)}°C</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

/** Estate weather card: location mode, risk banner, metrics, spray window, manual entry + GMaps guide. */
export function WeatherCard({ compact = false }: { compact?: boolean }) {
  const { t } = useI18n();
  const { coords, env, envLoading, requestGps, setManual, refreshEnv, hasCoords } = useLocation2();
  const [guide, setGuide] = useState(false);
  const place = env?.region_name ?? (hasCoords ? `${num(coords.lat, 4)}, ${num(coords.lng, 4)}` : t("noLocation"));

  return (
    <section className="card stack" aria-labelledby="weather-title" data-testid="weather-card">
      <div className="row-between">
        <h2 className="card-title" id="weather-title" style={{ margin: 0 }}><MapPin />{t("estateWeather")}</h2>
        <button className="btn btn-sm btn-ghost" onClick={refreshEnv} disabled={envLoading || !hasCoords} aria-label={t("refresh")}>
          {envLoading ? <Spinner size={18} /> : <RefreshCw />}{t("refresh")}
        </button>
      </div>
      <div className="row wrap">
        <span className="badge badge-primary">{coords.mode === "gps" ? <Crosshair /> : <Pencil />}{coords.mode === "gps" ? t("autoGps") : t("manualEntry")}</span>
        <span className="caption" data-testid="place-label">{coords.status === "locating" ? t("acquiringGps") : place}{hasCoords && env?.region_name ? ` · ${num(coords.lat, 4)}, ${num(coords.lng, 4)}` : ""}</span>
      </div>
      {coords.status === "denied" && <div className="caption" role="status">{t("gpsDenied")}</div>}
      <RiskBanner env={env} />
      {envLoading && !env?.available && <div className="row caption"><Spinner size={16} />{t("weatherLoading")}</div>}
      {env?.available ? (
        <>
          <WeatherGrid env={env} />
          {!compact && <SprayAndForecast env={env} />}
        </>
      ) : (!envLoading && hasCoords && <div className="caption">{t("weatherUnavailable")}</div>)}
      <div className="grid-2">
        {coords.mode === "gps"
          ? <button className="btn btn-sm btn-tonal" onClick={() => setGuide(true)} data-testid="manual-entry"><Pencil />{t("manualEntry")}</button>
          : <button className="btn btn-sm btn-tonal" onClick={requestGps} data-testid="auto-gps"><Crosshair />{t("autoGps")}</button>}
        <button className="btn btn-sm btn-outline" onClick={() => setGuide(true)}><CircleHelp />{t("findOnMaps")}</button>
      </div>
      <GmapsGuide open={guide} onClose={() => setGuide(false)} onApply={(a, b) => setManual(a, b)} initial={coords} />
    </section>
  );
}
