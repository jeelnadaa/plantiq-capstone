import { useCallback, useEffect, useMemo, useState } from "react";
import { Bug, ChevronRight, ClipboardList, History as HistoryIcon, Leaf, MessagesSquare, ScanLine, Trash2, TriangleAlert } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { AppBar } from "../components/AppBar";
import { BottomNav } from "../components/BottomNav";
import { Sheet } from "../components/Sheet";
import { DiagnosisDetails } from "../components/DiagnosisCard";
import { EmptyState, OfflineBanner, useErrorText } from "../components/common";
import { useI18n } from "../lib/i18n";
import { API, api, resolveUrl } from "../lib/api";
import { useToast } from "../lib/toast";
import { clock, dayBucket, diseaseName, num, shortDate } from "../lib/format";
import { setHandoff } from "./Scanner";
import type { Scan } from "../lib/types";

type Kind = "all" | "disease" | "healthy";

export function History() {
  const { t, lang } = useI18n();
  const nav = useNavigate();
  const toast = useToast();
  const errText = useErrorText();
  const [scans, setScans] = useState<Scan[] | null>(null);
  const [kind, setKind] = useState<Kind>("all");
  const [open, setOpen] = useState<Scan | null>(null);

  const load = useCallback(async () => {
    try {
      setScans(await api<Scan[]>(`${API}/scans`, { query: { limit: 200 } }));
    } catch (e) {
      toast.show(errText(e), "error");
      setScans((s) => s ?? []);
    }
  }, [toast, errText]);
  useEffect(() => { load(); }, [load]);

  const counts = useMemo(() => ({
    all: scans?.length ?? 0, disease: scans?.filter((s) => !s.is_healthy).length ?? 0, healthy: scans?.filter((s) => s.is_healthy).length ?? 0,
  }), [scans]);
  const visible = (scans ?? []).filter((s) => kind === "all" || (kind === "healthy" ? s.is_healthy : !s.is_healthy));
  const groups = (["today", "yesterday", "earlier"] as const).map((b) => [b, visible.filter((s) => dayBucket(s.created_at) === b)] as const).filter(([, v]) => v.length);

  const deleteOne = async (scan: Scan) => {
    setOpen(null);
    const before = scans ?? [];
    setScans(before.filter((s) => s.id !== scan.id));
    try {
      await api(`${API}/scans/${scan.id}`, { method: "DELETE" });
      toast.undo(t("scanDeleted"), async () => {
        await api(`${API}/scans/${scan.id}/restore`, { method: "POST" }).catch(() => undefined);
        load();
      });
    } catch (e) {
      setScans(before);
      toast.show(errText(e), "error");
    }
  };

  const clearAll = async () => {
    const before = scans ?? [];
    if (!before.length) return;
    setScans([]);
    try {
      const res = await api<{ ids: number[] }>(`${API}/scans`, { method: "DELETE" });
      toast.undo(t("allCleared"), async () => {
        await api(`${API}/scans/restore`, { body: { ids: res.ids } }).catch(() => undefined);
        load();
      });
    } catch (e) {
      setScans(before);
      toast.show(errText(e), "error");
    }
  };

  const askInChat = (s: Scan) => {
    const mediaId = s.image_url?.split("/").pop()?.replace(/\.jpg$/, "") ?? null;
    setHandoff({ disease: s.disease, confidence: s.confidence, advisory: s.advisory, imageUrl: s.image_url, mediaId, env: s.env_data });
    nav("/chat");
  };

  return (
    <div className="screen" data-testid="history">
      <AppBar title={t("historyTitle")} icon={<HistoryIcon />}
        right={counts.all > 0 ? <button className="btn btn-sm btn-danger-outline" onClick={clearAll} data-testid="clear-all"><Trash2 />{t("clearAll")}</button> : undefined} minimal />
      <main className="screen-body">
        <OfflineBanner />
        {scans === null ? (
          <div className="stack">{[0, 1, 2].map((i) => <div key={i} className="skeleton" style={{ height: 92 }} />)}</div>
        ) : scans.length === 0 ? (
          <EmptyState icon={<ScanLine />} title={t("noScans")} body={t("noScansBody")}
            action={<button className="btn btn-primary" onClick={() => nav("/")}><ScanLine />{t("goScan")}</button>} />
        ) : (
          <>
            <div className="chips" role="radiogroup">
              {(["all", "disease", "healthy"] as const).map((k) => (
                <button key={k} role="radio" aria-checked={kind === k} className={`chip ${kind === k ? "active" : ""}`} onClick={() => setKind(k)} data-testid={`filter-${k}`}>
                  {t(k === "all" ? "filterAll" : k === "disease" ? "filterDisease" : "filterHealthy", { n: counts[k] })}
                </button>
              ))}
            </div>
            {groups.map(([bucket, items]) => (
              <div key={bucket} className="stack-sm">
                <div className="date-head">{t(bucket === "today" ? "todayLabel" : bucket === "yesterday" ? "yesterday" : "earlier")}</div>
                {items.map((s) => (
                  <div key={s.id} className="row" style={{ gap: 6 }}>
                    <button className="scan-item grow" onClick={() => setOpen(s)} data-testid="scan-item">
                      {s.image_url ? <img src={resolveUrl(s.image_url)} alt="" loading="lazy" /> : <div style={{ width: 72, height: 72 }} />}
                      <div className="grow" style={{ minWidth: 0 }}>
                        <div className="title">{diseaseName(lang, s.disease)}</div>
                        <div className="caption">
                          {bucket === "earlier" ? shortDate(lang, s.created_at) : clock(lang, s.created_at)} · {num(s.confidence)}% {t("sureLabel")}
                          {s.env_data?.region_name ? ` · ${s.env_data.region_name.split(" ")[0]}` : ""}
                        </div>
                        <span className={`badge ${s.is_blended ? "badge-warn" : s.is_healthy ? "badge-healthy" : "badge-disease"}`} style={{ marginTop: 4 }}>
                          {s.is_blended ? <TriangleAlert /> : s.is_healthy ? <Leaf /> : <Bug />}
                          {s.is_blended ? t("lowCertaintyBadge") : s.is_healthy ? t("dzShort_Healthy") : s.disease === "Miner" ? t("pestFound") : t("diseaseFound")}
                        </span>
                      </div>
                      <ChevronRight color="var(--muted)" />
                    </button>
                    <button className="icon-btn" style={{ color: "var(--danger)" }} onClick={() => deleteOne(s)} aria-label={t("deleteScan")} data-testid="delete-scan"><Trash2 /></button>
                  </div>
                ))}
              </div>
            ))}
          </>
        )}
      </main>
      <BottomNav />
      <Sheet open={!!open} onClose={() => setOpen(null)} title={t("detailsTitle")} icon={<ClipboardList />} testId="scan-details">
        {open && (
          <div className="stack">
            {open.image_url && <img src={resolveUrl(open.image_url)} alt="" style={{ width: "100%", maxHeight: 220, objectFit: "cover", borderRadius: 18 }} />}
            <div className="caption">{shortDate(lang, open.created_at)} · {clock(lang, open.created_at)}</div>
            <DiagnosisDetails disease={open.disease} confidence={open.confidence} isHealthy={open.is_healthy} isBlended={open.is_blended}
              distribution={open.distribution} advisory={open.advisory} citations={open.citations} safety={open.safety_audit}
              env={open.env_data} question={open.question} />
            <div className="grid-2">
              <button className="btn btn-primary" onClick={() => askInChat(open)} data-testid="details-ask"><MessagesSquare />{t("askInChat")}</button>
              <button className="btn btn-danger-outline" onClick={() => deleteOne(open)}><Trash2 />{t("deleteScan")}</button>
            </div>
          </div>
        )}
      </Sheet>
    </div>
  );
}
