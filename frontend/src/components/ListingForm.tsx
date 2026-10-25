import { useEffect, useRef, useState } from "react";
import { ClipboardX, Crosshair, ImagePlus, MapPin, PackagePlus, Pencil, Send, Trash2 } from "lucide-react";
import { Sheet } from "./Sheet";
import { Spinner, useErrorText } from "./common";
import { useI18n } from "../lib/i18n";
import { API, ApiError, api, resolveUrl } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useLocation2 } from "../lib/location";
import { useToast } from "../lib/toast";
import { inr, num } from "../lib/format";
import {
  effectivePriceUnit, effectiveQtyUnit, normalizePhone, priceToPerKg, quantityToKg, validCoords, validateListing,
  type Issue, type ListingDraft,
} from "../lib/validation";
import type { Listing } from "../lib/types";
import type { TKey } from "../lib/i18n/en";

const QTY_UNITS: [string, TKey][] = [["kg", "unitKg"], ["ton", "unitTon"], ["quintal", "unitQuintal"], ["bag (50kg)", "unitBag50"], ["bag (60kg)", "unitBag60"], ["custom", "unitCustom"]];
const PRICE_UNITS: [string, TKey][] = [["per kg", "pricePerKg"], ["per ton", "pricePerTon"], ["per quintal", "pricePerQuintal"], ["per 50kg bag", "pricePer50"], ["per 60kg bag", "pricePer60"], ["custom", "unitCustom"]];
const VARIETIES = ["Arabica", "Robusta", "Liberica"];
const MAX_PHOTOS = 8;

type PhotoDraft = { key: string; preview: string; mediaId?: string; file?: File; caption: string };

function draftFrom(l: Listing | null, name: string, phone: string): ListingDraft {
  const qu = QTY_UNITS.some(([v]) => v === l?.quantity_unit) ? l!.quantity_unit : l ? "custom" : "kg";
  const pu = PRICE_UNITS.some(([v]) => v === l?.price_unit) ? l!.price_unit : l ? "custom" : "per kg";
  return {
    title: l?.title ?? "", variety: l?.variety ?? "", quantity: l ? String(l.quantity) : "", quantityUnit: qu,
    customQtyUnit: qu === "custom" ? l?.quantity_unit ?? "" : "", price: l ? String(l.price) : "", priceUnit: pu,
    customPriceUnit: pu === "custom" ? l?.price_unit ?? "" : "", farmerName: l?.farmer_name ?? name, phone: l?.phone_number ?? phone,
    address: l?.address ?? "",
  };
}

type Props = { open: boolean; onClose: () => void; editing: Listing | null; onSaved: (l: Listing, created: boolean) => void };

export function ListingForm({ open, onClose, editing, onSaved }: Props) {
  const { t } = useI18n();
  const { user } = useAuth();
  const toast = useToast();
  const errText = useErrorText();
  const { coords } = useLocation2();
  const [d, setD] = useState<ListingDraft>(() => draftFrom(null, "", ""));
  const [photos, setPhotos] = useState<PhotoDraft[]>([]);
  const [locMode, setLocMode] = useState<"gps" | "manual">("gps");
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");
  const [gpsBusy, setGpsBusy] = useState(false);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [showIssues, setShowIssues] = useState(false);
  const [invalid, setInvalid] = useState<Set<string>>(new Set());
  const [busy, setBusy] = useState<"" | "upload" | "save">("");
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    setD(draftFrom(editing, user?.full_name ?? "", user?.phone ?? ""));
    setPhotos((editing?.photos ?? []).map((p) => ({ key: p.media_id, preview: resolveUrl(p.url), mediaId: p.media_id, caption: p.caption })));
    const la = editing?.latitude ?? coords.lat;
    const ln = editing?.longitude ?? coords.lng;
    setLat(la != null ? String(la) : "");
    setLng(ln != null ? String(ln) : "");
    setLocMode(editing && editing.latitude != null ? "manual" : "gps");
    setInvalid(new Set());
    setIssues([]);
  }, [open, editing]); // eslint-disable-line react-hooks/exhaustive-deps

  const set = <K extends keyof ListingDraft>(k: K, v: ListingDraft[K]) => {
    setD((s) => ({ ...s, [k]: v }));
    setInvalid((s) => { const n = new Set(s); n.delete(k); return n; });
  };

  const useGps = () => {
    setLocMode("gps");
    if (!("geolocation" in navigator)) return;
    setGpsBusy(true);
    navigator.geolocation.getCurrentPosition(
      (p) => { setLat(p.coords.latitude.toFixed(5)); setLng(p.coords.longitude.toFixed(5)); setGpsBusy(false); },
      () => { if (coords.lat != null) { setLat(String(coords.lat)); setLng(String(coords.lng)); } setGpsBusy(false); },
      { timeout: 8000 },
    );
  };

  const addFiles = (files: FileList | null) => {
    if (!files) return;
    const room = MAX_PHOTOS - photos.length;
    if (files.length > room) toast.show(t("maxPhotos", { n: MAX_PHOTOS }), "error");
    const added = Array.from(files).slice(0, Math.max(0, room)).map((f) => ({ key: `${f.name}-${f.size}-${Math.random()}`, preview: URL.createObjectURL(f), file: f, caption: "" }));
    setPhotos((p) => [...p, ...added]);
  };

  const focusField = (field: string) => {
    setShowIssues(false);
    window.setTimeout(() => {
      const el = document.getElementById(`lf-${field}`);
      el?.scrollIntoView({ behavior: "smooth", block: "center" });
      (el as HTMLInputElement | null)?.focus();
    }, 120);
  };

  const submit = async () => {
    const found = validateListing(d);
    if (found.length) {
      setIssues(found);
      setInvalid(new Set(found.map((i) => i.field)));
      setShowIssues(true);
      return;
    }
    try {
      setBusy("upload");
      const uploaded: { media_id: string; caption: string }[] = [];
      for (const p of photos) {
        if (p.mediaId) { uploaded.push({ media_id: p.mediaId, caption: p.caption.trim() }); continue; }
        const form = new FormData();
        form.append("file", p.file!, p.file!.name);
        form.append("kind", "listing");
        const m = await api<{ id: string }>(`${API}/media`, { form, timeoutMs: 60000 });
        p.mediaId = m.id;
        uploaded.push({ media_id: m.id, caption: p.caption.trim() });
      }
      setBusy("save");
      const la = parseFloat(lat), ln = parseFloat(lng);
      const body = {
        title: d.title.trim(), variety: d.variety.trim(), quantity: parseFloat(d.quantity), quantity_unit: effectiveQtyUnit(d),
        price: parseFloat(d.price), price_unit: effectivePriceUnit(d), farmer_name: d.farmerName.trim(), phone_number: normalizePhone(d.phone),
        address: d.address.trim(), latitude: validCoords(la, ln) ? la : null, longitude: validCoords(la, ln) ? ln : null, photos: uploaded,
      };
      const saved = editing
        ? await api<Listing>(`${API}/marketplace/listings/${editing.id}`, { method: "PUT", body })
        : await api<Listing>(`${API}/marketplace/listings`, { method: "POST", body });
      toast.show(editing ? t("listingUpdated") : t("listingPublished"));
      onSaved(saved, !editing);
      onClose();
    } catch (e) {
      if (e instanceof ApiError && e.status === 429) toast.show(e.message || t("quotaReached"), "error");
      else toast.show(errText(e), "error");
    } finally {
      setBusy("");
    }
  };

  const qtyKg = quantityToKg(parseFloat(d.quantity), effectiveQtyUnit(d));
  const perKg = priceToPerKg(parseFloat(d.price), effectivePriceUnit(d));
  const cls = (k: string) => `input ${invalid.has(k) ? "invalid" : ""}`;

  return (
    <>
      <Sheet open={open} onClose={onClose} title={editing ? t("editTitle") : t("sellTitle")} icon={<PackagePlus />} testId="listing-form">
        <form className="stack" onSubmit={(e) => { e.preventDefault(); submit(); }} noValidate>
          <div className="field">
            <label className="label" htmlFor="lf-title">{t("cropTitleLabel")} <span className="req">*</span></label>
            <input id="lf-title" className={cls("title")} value={d.title} maxLength={150} onChange={(e) => set("title", e.target.value)} placeholder={t("cropTitlePlaceholder")} />
          </div>
          <div className="field">
            <label className="label" htmlFor="lf-variety">{t("varietyLabel")} <span className="req">*</span></label>
            <div className="chips">
              {VARIETIES.map((v) => (
                <button type="button" key={v} className={`chip ${d.variety.toLowerCase().startsWith(v.toLowerCase()) ? "active" : ""}`} onClick={() => set("variety", v)}>{v}</button>
              ))}
            </div>
            <input id="lf-variety" className={cls("variety")} value={d.variety} maxLength={100} onChange={(e) => set("variety", e.target.value)} placeholder={t("varietyPlaceholder")} />
          </div>
          <div className="field">
            <label className="label" htmlFor="lf-quantity">{t("quantityLabel")} <span className="req">*</span></label>
            <div className="input-group">
              <input id="lf-quantity" className={cls("quantity")} inputMode="decimal" value={d.quantity} onChange={(e) => set("quantity", e.target.value)} placeholder="500" />
              <select className="select" value={d.quantityUnit} onChange={(e) => set("quantityUnit", e.target.value)} aria-label={t("quantityLabel")}>
                {QTY_UNITS.map(([v, k]) => <option key={v} value={v}>{t(k)}</option>)}
              </select>
            </div>
            {d.quantityUnit === "custom" && <input id="lf-customQtyUnit" className={cls("customQtyUnit")} value={d.customQtyUnit} maxLength={50} onChange={(e) => set("customQtyUnit", e.target.value)} placeholder={t("customUnitPlaceholder")} />}
            {qtyKg > 0 && <span className="help">{t("equalsKg", { v: inr(qtyKg) })}</span>}
          </div>
          <div className="field">
            <label className="label" htmlFor="lf-price">{t("priceLabel")} (₹) <span className="req">*</span></label>
            <div className="input-group">
              <input id="lf-price" className={cls("price")} inputMode="decimal" value={d.price} onChange={(e) => set("price", e.target.value)} placeholder="420" />
              <select className="select" value={d.priceUnit} onChange={(e) => set("priceUnit", e.target.value)} aria-label={t("priceLabel")}>
                {PRICE_UNITS.map(([v, k]) => <option key={v} value={v}>{t(k)}</option>)}
              </select>
            </div>
            {d.priceUnit === "custom" && <input id="lf-customPriceUnit" className={cls("customPriceUnit")} value={d.customPriceUnit} maxLength={80} onChange={(e) => set("customPriceUnit", e.target.value)} placeholder={t("customPricePlaceholder")} />}
            {perKg > 0 && d.priceUnit !== "per kg" && <span className="help">{t("equalsPerKg", { v: inr(perKg) })}</span>}
          </div>
          <div className="field">
            <label className="label" htmlFor="lf-farmerName">{t("farmerNameLabel")} <span className="req">*</span></label>
            <input id="lf-farmerName" className={cls("farmerName")} value={d.farmerName} maxLength={120} onChange={(e) => set("farmerName", e.target.value)} />
          </div>
          <div className="field">
            <label className="label" htmlFor="lf-phone">{t("phoneWaLabel")} <span className="req">*</span></label>
            <input id="lf-phone" className={cls("phone")} inputMode="tel" value={d.phone} onChange={(e) => set("phone", e.target.value)} placeholder={t("phonePlaceholder")} />
          </div>
          <div className="field">
            <label className="label" htmlFor="lf-address">{t("addressLabel")} <span className="req">*</span></label>
            <input id="lf-address" className={cls("address")} value={d.address} maxLength={300} onChange={(e) => set("address", e.target.value)} placeholder={t("addressPlaceholder")} />
          </div>
          <div className="card tonal stack-sm">
            <div className="row-between">
              <b className="row" style={{ gap: 6 }}><MapPin width={18} color="var(--primary)" />{t("estateLocation")}</b>
              <span className="caption">{lat && lng ? `${num(parseFloat(lat), 4)}, ${num(parseFloat(lng), 4)}` : t("noLocation")}</span>
            </div>
            <div className="segmented">
              <button type="button" className={locMode === "gps" ? "active" : ""} onClick={useGps}>{gpsBusy ? <Spinner size={16} /> : <Crosshair />}{t("useGps")}</button>
              <button type="button" className={locMode === "manual" ? "active" : ""} onClick={() => setLocMode("manual")}><Pencil />{t("typeIt")}</button>
            </div>
            {locMode === "manual" && (
              <div className="grid-2">
                <input className="input" inputMode="decimal" value={lat} onChange={(e) => setLat(e.target.value)} placeholder="13.3161" aria-label={t("latLabel")} />
                <input className="input" inputMode="decimal" value={lng} onChange={(e) => setLng(e.target.value)} placeholder="75.7720" aria-label={t("lngLabel")} />
              </div>
            )}
          </div>
          <div className="field">
            <span className="label">{t("photosLabel")}</span>
            <button type="button" className="dropzone" onClick={() => fileRef.current?.click()} disabled={photos.length >= MAX_PHOTOS}>
              <ImagePlus /><b>{t("addPhotos")}</b><div className="caption">{t("addPhotosHint")}</div>
            </button>
            <input ref={fileRef} type="file" accept="image/*" multiple hidden onChange={(e) => { addFiles(e.target.files); e.target.value = ""; }} data-testid="listing-photos" />
            {photos.map((p, i) => (
              <div className="photo-row" key={p.key}>
                <img src={p.preview} alt="" />
                <input className="input grow" style={{ height: 44 }} value={p.caption} maxLength={140} placeholder={t("captionPlaceholder")}
                  onChange={(e) => setPhotos((all) => all.map((x, j) => (j === i ? { ...x, caption: e.target.value } : x)))} aria-label={t("captionPlaceholder")} />
                <button type="button" className="icon-btn" style={{ width: 44, height: 44 }} aria-label={t("remove")} onClick={() => setPhotos((all) => all.filter((_, j) => j !== i))}><Trash2 /></button>
              </div>
            ))}
          </div>
          <button type="submit" className="btn btn-accent btn-block btn-xl" disabled={!!busy} data-testid="publish">
            {busy ? <><Spinner />{busy === "upload" ? t("uploadingPhotos") : t("publishing")}</> : <><Send />{editing ? t("update") : t("publish")}</>}
          </button>
        </form>
      </Sheet>

      <Sheet open={showIssues} onClose={() => setShowIssues(false)} center testId="validation-sheet"
        title={<span>{editing ? t("valEditTitle") : t("valTitle")}<div className="caption" style={{ fontWeight: 600 }}>{t("valCount", { n: issues.length })}</div></span>}
        icon={<ClipboardX />} iconTone="warn">
        <p className="body-sm" style={{ marginTop: 0 }}>{t("valIntro")}</p>
        <div className="stack-sm">
          {issues.map((iss, n) => (
            <button key={`${iss.field}-${n}`} className="issue" onClick={() => focusField(iss.field)} data-testid="validation-issue">
              <span className="n">{n + 1}</span>
              <div><strong>{t(iss.label)}</strong><span className="body-sm">{t(iss.what)}</span><div className="caption">{t("whyLabel", { why: t(iss.why) })}</div></div>
            </button>
          ))}
        </div>
        <div className="stack-sm" style={{ marginTop: 14 }}>
          <button className="btn btn-primary btn-block" onClick={() => issues[0] && focusField(issues[0].field)}><Pencil />{t("valFix")}</button>
          <button className="btn btn-ghost btn-block" onClick={() => setShowIssues(false)}>{t("close")}</button>
        </div>
      </Sheet>
    </>
  );
}
