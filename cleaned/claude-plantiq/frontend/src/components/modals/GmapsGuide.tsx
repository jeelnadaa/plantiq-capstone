import { useEffect, useState } from "react";
import { Check, MapPinned } from "lucide-react";
import { Sheet } from "../Sheet";
import { FieldError } from "../common";
import { translate, useI18n, type Lang } from "../../lib/i18n";
import { validCoords } from "../../lib/validation";

type Props = { open: boolean; onClose: () => void; onApply?: (lat: number, lng: number) => void; initial?: { lat: number | null; lng: number | null } };

/** Google Maps coordinates guide (steps in English and Kannada) + manual lat/lng entry. */
export function GmapsGuide({ open, onClose, onApply, initial }: Props) {
  const { t, lang } = useI18n();
  const [guideLang, setGuideLang] = useState<Lang>(lang);
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (open) {
      setGuideLang(lang);
      setLat(initial?.lat != null ? String(initial.lat) : "");
      setLng(initial?.lng != null ? String(initial.lng) : "");
      setError("");
    }
  }, [open, lang, initial?.lat, initial?.lng]);

  const apply = () => {
    // Accept a pasted "13.3161, 75.7720" in the latitude box too.
    let la = lat, ln = lng;
    const pair = /(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)/.exec(lat);
    if (pair && !lng) [la, ln] = [pair[1], pair[2]];
    const a = parseFloat(la), b = parseFloat(ln);
    if (!validCoords(a, b)) {
      setError(t("coordsInvalid"));
      return;
    }
    onApply?.(a, b);
    onClose();
  };

  return (
    <Sheet open={open} onClose={onClose} title={t("gmapsTitle")} icon={<MapPinned />} testId="gmaps-sheet">
      <div className="segmented" style={{ marginBottom: 12 }}>
        <button className={guideLang === "en" ? "active" : ""} onClick={() => setGuideLang("en")}>English</button>
        <button className={guideLang === "kn" ? "active" : ""} onClick={() => setGuideLang("kn")}>ಕನ್ನಡ</button>
      </div>
      <ol className="guide-steps">
        {(["gmaps1", "gmaps2", "gmaps3", "gmaps4"] as const).map((k) => <li key={k}>{translate(guideLang, k)}</li>)}
      </ol>
      {onApply && (
        <>
          <div className="grid-2" style={{ marginTop: 14 }}>
            <div className="field">
              <label className="label" htmlFor="g-lat">{t("latLabel")}</label>
              <input id="g-lat" className={`input ${error ? "invalid" : ""}`} inputMode="decimal" placeholder="13.3161" value={lat} onChange={(e) => setLat(e.target.value)} />
            </div>
            <div className="field">
              <label className="label" htmlFor="g-lng">{t("lngLabel")}</label>
              <input id="g-lng" className={`input ${error ? "invalid" : ""}`} inputMode="decimal" placeholder="75.7720" value={lng} onChange={(e) => setLng(e.target.value)} />
            </div>
          </div>
          <FieldError>{error}</FieldError>
          <button className="btn btn-primary btn-block" style={{ marginTop: 12 }} onClick={apply} data-testid="apply-coords"><Check />{t("applyCoords")}</button>
        </>
      )}
    </Sheet>
  );
}
