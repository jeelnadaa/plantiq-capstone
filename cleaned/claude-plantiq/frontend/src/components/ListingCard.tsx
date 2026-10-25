import { useState } from "react";
import { BadgeCheck, Calendar, Flag, Map, MapPin, MessageCircle, Navigation, Pencil, Phone, Trash2, UserRound } from "lucide-react";
import { useI18n } from "../lib/i18n";
import { resolveUrl } from "../lib/api";
import { openExternal } from "../lib/native";
import { inr, timeAgo } from "../lib/format";
import type { Listing } from "../lib/types";

type Props = { item: Listing; onEdit?: (l: Listing) => void; onDelete?: (l: Listing) => void; onReport?: (l: Listing) => void };

function priceUnitLabel(unit: string) {
  const u = unit.trim();
  return u.startsWith("per ") ? `/${u.slice(4)}` : u.startsWith("/") ? u : `/${u}`;
}

export function ListingCard({ item, onEdit, onDelete, onReport }: Props) {
  const { t, lang } = useI18n();
  const [active, setActive] = useState(0);
  const photo = item.photos[active];
  const perKg = item.price_unit.replace(/\s/g, "").toLowerCase() !== "perkg";
  const wa = item.whatsapp_url ?? `https://wa.me/91${item.phone_number}?text=${encodeURIComponent(t("waMessage", { name: item.farmer_name, title: item.title }))}`;

  return (
    <article className="listing" data-testid="listing-card">
      {item.photos.length > 0 && (
        <>
          <div className="listing-media">
            <img src={resolveUrl(photo.url)} alt={photo.caption || item.title} loading="lazy" />
            {item.distance_km != null && <span className="dist badge badge-neutral"><Navigation />{t("kmAway", { n: item.distance_km })}</span>}
            {photo.caption && <div className="cap">{photo.caption}</div>}
          </div>
          {item.photos.length > 1 && (
            <div className="thumbs" role="tablist">
              {item.photos.map((p, i) => (
                <button key={p.media_id} className={i === active ? "active" : ""} onClick={() => setActive(i)} role="tab" aria-selected={i === active} aria-label={p.caption || `${i + 1}`}>
                  <img src={resolveUrl(p.url)} alt="" loading="lazy" />
                </button>
              ))}
            </div>
          )}
        </>
      )}
      <div className="listing-body">
        <div className="row-between" style={{ alignItems: "flex-start" }}>
          <div style={{ minWidth: 0 }}>
            <b style={{ fontSize: "1.1rem" }} data-testid="listing-title">{item.title}</b>
            <div className="caption">{item.variety} · {item.quantity} {item.quantity_unit}</div>
          </div>
          <div style={{ textAlign: "right", flex: "none" }}>
            <div className="price">₹{inr(item.price)}<small>{priceUnitLabel(item.price_unit)}</small></div>
            {perKg && <div className="caption">{t("approxPerKg", { v: inr(item.price_per_kg) })}</div>}
          </div>
        </div>
        <div className="meta">
          <span><MapPin />{item.address}</span>
          <span><UserRound />{item.is_owner ? t("you") : item.farmer_name}</span>
          <span><Calendar />{timeAgo(lang, item.created_at)}</span>
          {item.photos.length === 0 && item.distance_km != null && <span><Navigation />{t("kmAway", { n: item.distance_km })}</span>}
          {item.distance_km == null && item.latitude != null && <span><MapPin />{t("gpsVerified")}</span>}
        </div>
        {!item.is_owner && (
          <>
            <div className="contact-row">
              <button className="btn btn-sm btn-outline" onClick={() => openExternal(`tel:${item.phone_number}`)}><Phone />{t("call")}</button>
              <button className="btn btn-sm btn-whatsapp" onClick={() => openExternal(wa)}><MessageCircle />{t("whatsapp")}</button>
              <button className="btn btn-sm btn-tonal" onClick={() => item.google_maps_url && openExternal(item.google_maps_url)} disabled={!item.google_maps_url}><Map />{t("route")}</button>
            </div>
            {onReport && (
              <button className="btn btn-sm btn-ghost" style={{ alignSelf: "flex-start", color: "var(--muted)" }} disabled={item.reported_by_me}
                onClick={() => onReport(item)} data-testid="report-btn">
                <Flag />{item.reported_by_me ? t("reported") : t("report")}
              </button>
            )}
          </>
        )}
        {item.is_owner && (
          <div className="owner-row">
            <span className="badge badge-primary"><BadgeCheck />{t("yourLot")}</span>
            <span className="grow" />
            {onEdit && <button className="btn btn-sm btn-outline" onClick={() => onEdit(item)} data-testid="edit-listing"><Pencil />{t("edit")}</button>}
            {onDelete && <button className="btn btn-sm btn-danger-outline" onClick={() => onDelete(item)} aria-label={t("delete")} data-testid="delete-listing"><Trash2 /></button>}
          </div>
        )}
      </div>
    </article>
  );
}
