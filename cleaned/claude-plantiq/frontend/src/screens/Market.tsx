import { useCallback, useEffect, useMemo, useState } from "react";
import { Flag, MapPin, Package, Plus, RefreshCw, RotateCcw, Search, SlidersHorizontal, Store, Trash2 } from "lucide-react";
import { AppBar } from "../components/AppBar";
import { BottomNav } from "../components/BottomNav";
import { Sheet } from "../components/Sheet";
import { ListingCard } from "../components/ListingCard";
import { ListingForm } from "../components/ListingForm";
import { EmptyState, OfflineBanner, Spinner, useErrorText } from "../components/common";
import { useI18n } from "../lib/i18n";
import { useLocation2 } from "../lib/location";
import { API, api } from "../lib/api";
import { useToast } from "../lib/toast";
import { inr, num } from "../lib/format";
import type { Listing } from "../lib/types";
import type { TKey } from "../lib/i18n/en";

type Sort = "distance" | "newest" | "price_asc" | "price_desc" | "qty_desc";
type Filters = { distance: number | null; variety: string; minQty: number; minPrice: number; maxPrice: number; photosOnly: boolean };
export const DEFAULT_FILTERS: Filters = { distance: null, variety: "all", minQty: 0, minPrice: 0, maxPrice: 1000, photosOnly: false };
const SORTS: [Sort, TKey][] = [["distance", "sortNearest"], ["newest", "sortNewest"], ["price_asc", "sortPriceAsc"], ["price_desc", "sortPriceDesc"], ["qty_desc", "sortQty"]];

export function filtersToQuery(f: Filters, q: string, sort: Sort, lat: number | null, lng: number | null) {
  return {
    q: q.trim() || undefined,
    sort_by: sort,
    variety: f.variety !== "all" ? f.variety : undefined,
    min_qty: f.minQty || undefined,
    min_price: f.minPrice > 0 ? f.minPrice : undefined,
    max_price: f.maxPrice < 1000 ? f.maxPrice : undefined,
    has_photos: f.photosOnly || undefined,
    latitude: lat ?? undefined,
    longitude: lng ?? undefined,
    max_distance_km: f.distance && lat != null ? f.distance : undefined,
  };
}

export function activeFilterCount(f: Filters) {
  return [f.distance !== null, f.variety !== "all", f.minQty > 0, f.minPrice > 0 || f.maxPrice < 1000, f.photosOnly].filter(Boolean).length;
}

export function Market() {
  const { t } = useI18n();
  const toast = useToast();
  const errText = useErrorText();
  const { coords, env, hasCoords, requestGps } = useLocation2();
  const [tab, setTab] = useState<"all" | "mine">("all");
  const [q, setQ] = useState("");
  const [debouncedQ, setDebouncedQ] = useState("");
  const [sort, setSort] = useState<Sort>("newest");
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [items, setItems] = useState<Listing[] | null>(null);
  const [mine, setMine] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Listing | null>(null);
  const [deleting, setDeleting] = useState<Listing | null>(null);
  const [reporting, setReporting] = useState<Listing | null>(null);

  useEffect(() => {
    const id = window.setTimeout(() => setDebouncedQ(q), 350);
    return () => window.clearTimeout(id);
  }, [q]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [all, my] = await Promise.all([
        api<Listing[]>(`${API}/marketplace/listings`, { query: filtersToQuery(filters, debouncedQ, sort, coords.lat, coords.lng) }),
        api<Listing[]>(`${API}/marketplace/my-listings`, { query: hasCoords ? { latitude: coords.lat!, longitude: coords.lng! } : undefined }),
      ]);
      setItems(all);
      setMine(my);
    } catch (e) {
      toast.show(errText(e), "error");
      setItems((x) => x ?? []);
    } finally {
      setLoading(false);
    }
  }, [filters, debouncedQ, sort, coords.lat, coords.lng, hasCoords, toast, errText]);

  useEffect(() => { load(); }, [load]);

  const remove = async () => {
    if (!deleting) return;
    try {
      await api(`${API}/marketplace/listings/${deleting.id}`, { method: "DELETE" });
      toast.show(t("listingDeleted"));
      setDeleting(null);
      load();
    } catch (e) {
      toast.show(errText(e), "error");
    }
  };

  const list = tab === "all" ? items : mine;
  const place = env?.region_name ?? (hasCoords ? `${num(coords.lat, 3)}, ${num(coords.lng, 3)}` : t("noLocation"));
  const nFilters = activeFilterCount(filters);

  return (
    <div className="screen" data-testid="market">
      <AppBar title={t("marketTitle")} icon={<Store />} />
      <main className="screen-body">
        <OfflineBanner />
        <div className="segmented" role="tablist">
          <button role="tab" aria-selected={tab === "all"} className={tab === "all" ? "active" : ""} onClick={() => setTab("all")} data-testid="tab-all"><Store />{t("allLots")}</button>
          <button role="tab" aria-selected={tab === "mine"} className={tab === "mine" ? "active" : ""} onClick={() => setTab("mine")} data-testid="tab-mine"><Package />{t("myLots", { n: mine.length })}</button>
        </div>
        {tab === "all" && (
          <>
            <div className="row">
              <div className="search grow">
                <Search />
                <input className="input" type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder={t("searchPlaceholder")} aria-label={t("searchPlaceholder")} data-testid="market-search" />
              </div>
              <button className="icon-btn" style={{ width: 54, height: 54, borderRadius: 18 }} onClick={() => setFiltersOpen(true)} aria-label={t("filters")} data-testid="open-filters">
                <SlidersHorizontal />{nFilters > 0 && <span className="status-dot ok" style={{ top: 8, right: 8 }} />}
              </button>
            </div>
            <div className="chips" role="radiogroup" aria-label="Sort">
              {SORTS.map(([s, k]) => (
                <button key={s} role="radio" aria-checked={sort === s} className={`chip ${sort === s ? "active" : ""}`}
                  onClick={() => { setSort(s); if (s === "distance" && !hasCoords) requestGps(); }} data-testid={`sort-${s}`}>{t(k)}</button>
              ))}
            </div>
            <div className="row-between">
              <span className="caption"><MapPin width={14} height={14} style={{ verticalAlign: -2 }} /> {t("fromPlace", { place, n: items?.length ?? 0 })}</span>
              <button className="btn btn-sm btn-ghost" onClick={requestGps}>{coords.status === "locating" ? <Spinner size={16} /> : <RefreshCw />}GPS</button>
            </div>
          </>
        )}
        {list === null || (loading && list.length === 0) ? (
          <div className="stack">{[0, 1].map((i) => <div key={i} className="skeleton" style={{ height: 220 }} />)}</div>
        ) : list.length === 0 ? (
          <EmptyState icon={tab === "all" ? <Store /> : <Package />} title={tab === "all" ? t("noLots") : t("noMyLots")}
            action={tab === "mine" ? <button className="btn btn-primary" onClick={() => { setEditing(null); setFormOpen(true); }}><Plus />{t("sellCrop")}</button> : undefined} />
        ) : (
          <div className="stack" data-testid="listing-list">
            {list.map((l) => (
              <ListingCard key={l.id} item={l} onEdit={(x) => { setEditing(x); setFormOpen(true); }} onDelete={setDeleting} onReport={setReporting} />
            ))}
          </div>
        )}
      </main>
      <button className="fab" onClick={() => { setEditing(null); setFormOpen(true); }} data-testid="sell-fab"><Plus />{t("sellCrop")}</button>
      <BottomNav />

      <FiltersSheet open={filtersOpen} onClose={() => setFiltersOpen(false)} value={filters} onApply={(f) => { setFilters(f); setFiltersOpen(false); }}
        countFor={async (f) => (await api<Listing[]>(`${API}/marketplace/listings`, { query: filtersToQuery(f, debouncedQ, sort, coords.lat, coords.lng) })).length}
        hasCoords={hasCoords} />
      <ListingForm open={formOpen} onClose={() => setFormOpen(false)} editing={editing} onSaved={(_, created) => { if (created) setTab("mine"); load(); }} />
      <Sheet open={!!deleting} onClose={() => setDeleting(null)} center icon={<Trash2 />} iconTone="danger" testId="delete-sheet"
        title={<span>{t("deleteTitle")}<div className="caption" style={{ fontWeight: 600 }}>{t("deleteSub")}</div></span>}>
        <p className="body-sm" style={{ marginTop: 0 }}>{t("deleteBody")}</p>
        {deleting && <div className="card tonal" style={{ padding: 12 }}><b>{deleting.title}</b><div className="caption">₹{inr(deleting.price)} {deleting.price_unit} · {deleting.quantity} {deleting.quantity_unit}</div></div>}
        <div className="grid-2" style={{ marginTop: 14 }}>
          <button className="btn btn-outline" onClick={() => setDeleting(null)}>{t("keep")}</button>
          <button className="btn btn-danger" onClick={remove} data-testid="confirm-delete">{t("confirmDelete")}</button>
        </div>
      </Sheet>
      <ReportSheet listing={reporting} onClose={() => setReporting(null)} onDone={load} />
    </div>
  );
}

function FiltersSheet({ open, onClose, value, onApply, countFor, hasCoords }: {
  open: boolean; onClose: () => void; value: Filters; onApply: (f: Filters) => void; countFor: (f: Filters) => Promise<number>; hasCoords: boolean;
}) {
  const { t } = useI18n();
  const [f, setF] = useState<Filters>(value);
  const [count, setCount] = useState<number | null>(null);

  useEffect(() => { if (open) setF(value); }, [open, value]);
  useEffect(() => {
    if (!open) return;
    let alive = true;
    const id = window.setTimeout(() => countFor(f).then((n) => alive && setCount(n)).catch(() => alive && setCount(null)), 300);
    return () => { alive = false; window.clearTimeout(id); };
  }, [f, open]); // eslint-disable-line react-hooks/exhaustive-deps

  const set = <K extends keyof Filters>(k: K, v: Filters[K]) => setF((s) => ({ ...s, [k]: v }));
  const left = useMemo(() => (Math.min(f.minPrice, f.maxPrice) / 1000) * 100, [f.minPrice, f.maxPrice]);
  const right = useMemo(() => 100 - (Math.max(f.minPrice, f.maxPrice) / 1000) * 100, [f.minPrice, f.maxPrice]);

  return (
    <Sheet open={open} onClose={onClose} title={t("filters")} testId="filters-sheet"
      headerExtra={<button className="btn btn-sm btn-ghost" onClick={() => setF(DEFAULT_FILTERS)} data-testid="reset-filters"><RotateCcw />{t("resetFilters")}</button>}>
      <div className="stack">
        <div className="field">
          <span className="label">{t("distance")}</span>
          <div className="chips">
            {[null, 15, 30, 60, 120].map((d) => (
              <button key={String(d)} className={`chip ${f.distance === d ? "active" : ""}`} onClick={() => set("distance", d)} disabled={d !== null && !hasCoords}>
                {d === null ? t("anyDistance") : t("withinKm", { n: d })}
              </button>
            ))}
          </div>
        </div>
        <div className="field">
          <span className="label">{t("variety")}</span>
          <div className="chips">
            {["all", "Arabica", "Robusta", "Liberica"].map((v) => (
              <button key={v} className={`chip ${f.variety === v ? "active" : ""}`} onClick={() => set("variety", v)} data-testid={`variety-${v}`}>{v === "all" ? t("allVarieties") : v}</button>
            ))}
          </div>
        </div>
        <div className="field">
          <span className="label">{t("minLot")}</span>
          <div className="chips">
            {[0, 50, 200, 1000].map((v) => (
              <button key={v} className={`chip ${f.minQty === v ? "active" : ""}`} onClick={() => set("minQty", v)}>{v === 0 ? t("anyQty") : v >= 1000 ? "≥ 1 ton" : `≥ ${v} kg`}</button>
            ))}
          </div>
        </div>
        <div className="field">
          <div className="row-between"><span className="label">{t("priceRange")}</span><b className="num">₹{f.minPrice} – ₹{f.maxPrice}{f.maxPrice >= 1000 ? "+" : ""}</b></div>
          <div className="range">
            <div className="track"><i style={{ left: `${left}%`, right: `${right}%` }} /></div>
            <input type="range" min={0} max={1000} step={10} value={f.minPrice} aria-label="Min price"
              onChange={(e) => set("minPrice", Math.min(Number(e.target.value), f.maxPrice))} />
            <input type="range" min={0} max={1000} step={10} value={f.maxPrice} aria-label="Max price"
              onChange={(e) => set("maxPrice", Math.max(Number(e.target.value), f.minPrice))} />
          </div>
          <div className="grid-2">
            <input className="input" inputMode="numeric" value={f.minPrice} aria-label="Min ₹" onChange={(e) => set("minPrice", Math.max(0, Math.min(1000, Number(e.target.value) || 0)))} />
            <input className="input" inputMode="numeric" value={f.maxPrice} aria-label="Max ₹" onChange={(e) => set("maxPrice", Math.max(0, Math.min(1000, Number(e.target.value) || 0)))} />
          </div>
        </div>
        <label className="check"><input type="checkbox" checked={f.photosOnly} onChange={(e) => set("photosOnly", e.target.checked)} />{t("photosOnly")}</label>
        <button className="btn btn-primary btn-block" onClick={() => onApply({ ...f, minPrice: Math.min(f.minPrice, f.maxPrice), maxPrice: Math.max(f.minPrice, f.maxPrice) })} data-testid="apply-filters">
          {count === null ? t("filters") : t("showLots", { n: count })}
        </button>
      </div>
    </Sheet>
  );
}

function ReportSheet({ listing, onClose, onDone }: { listing: Listing | null; onClose: () => void; onDone: () => void }) {
  const { t } = useI18n();
  const toast = useToast();
  const errText = useErrorText();
  const reasons: TKey[] = ["reportReasonFake", "reportReasonPrice", "reportReasonSpam", "reportReasonOther"];
  const [reason, setReason] = useState<TKey>("reportReasonFake");
  const [details, setDetails] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => { if (listing) { setReason("reportReasonFake"); setDetails(""); } }, [listing]);

  const send = async () => {
    if (!listing) return;
    setBusy(true);
    try {
      const text = `${t(reason)}${details.trim() ? ` — ${details.trim()}` : ""}`.slice(0, 500);
      await api(`${API}/marketplace/listings/${listing.id}/report`, { body: { reason: text } });
      toast.show(t("reportSent"));
      onClose();
      onDone();
    } catch (e) {
      toast.show(errText(e), "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Sheet open={!!listing} onClose={onClose} title={t("reportTitle")} icon={<Flag />} iconTone="warn" testId="report-sheet">
      <div className="stack">
        <p className="body-sm" style={{ margin: 0 }}>{t("reportBody")}</p>
        <div className="stack-sm" role="radiogroup">
          {reasons.map((r) => (
            <label key={r} className="check" style={{ padding: "10px 12px", border: "1px solid var(--line)", borderRadius: 14 }}>
              <input type="radio" name="reason" checked={reason === r} onChange={() => setReason(r)} />{t(r)}
            </label>
          ))}
        </div>
        <div className="field">
          <label className="label" htmlFor="rep-details">{t("reportDetails")} <span className="caption">({t("optional")})</span></label>
          <textarea id="rep-details" className="textarea" maxLength={300} value={details} onChange={(e) => setDetails(e.target.value)} />
        </div>
        <button className="btn btn-primary btn-block" onClick={send} disabled={busy} data-testid="send-report">{busy ? <Spinner /> : <Flag />}{t("sendReport")}</button>
      </div>
    </Sheet>
  );
}
