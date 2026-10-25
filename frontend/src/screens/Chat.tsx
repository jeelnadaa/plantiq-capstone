import { useCallback, useEffect, useRef, useState } from "react";
import { Crosshair, ImagePlus, MapPin, MessageSquareText, PanelLeft, Paperclip, Pencil, SendHorizontal, Sprout, SquarePen, Trash2, X } from "lucide-react";
import { AppBar } from "../components/AppBar";
import { BottomNav } from "../components/BottomNav";
import { Sheet } from "../components/Sheet";
import { VoiceButton } from "../components/VoiceButton";
import { GmapsGuide } from "../components/modals/GmapsGuide";
import { EmptyState, OfflineBanner, Spinner, useErrorText } from "../components/common";
import { useI18n } from "../lib/i18n";
import { useLocation2 } from "../lib/location";
import { API, api, resolveUrl } from "../lib/api";
import { Markdown } from "../lib/markdown";
import { useToast } from "../lib/toast";
import { diseaseName, num, timeAgo } from "../lib/format";
import { HANDOFF_KEY } from "./Scanner";
import type { ChatResponse, Handoff, Message, Scan, Thread } from "../lib/types";

type Attachment = { name: string; preview: string; file?: File; mediaId?: string; fromHistory?: boolean; disease?: string };

export function Chat() {
  const { t, lang } = useI18n();
  const toast = useToast();
  const errText = useErrorText();
  const { coords, env, hasCoords, requestGps, setManual } = useLocation2();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const [attachment, setAttachment] = useState<Attachment | null>(null);
  const [scanMeta, setScanMeta] = useState<Handoff | null>(null);
  const [threadsOpen, setThreadsOpen] = useState(false);
  const [pickerOpen, setPickerOpen] = useState(false);
  const [guideOpen, setGuideOpen] = useState(false);
  const listEnd = useRef<HTMLDivElement>(null);
  const handoffDone = useRef(false);

  const loadThreads = useCallback(async () => {
    try {
      setThreads(await api<Thread[]>(`${API}/chat/threads`));
    } catch {
      /* offline: keep current list */
    }
  }, []);

  useEffect(() => { loadThreads(); }, [loadThreads]);
  useEffect(() => { listEnd.current?.scrollIntoView({ behavior: "smooth", block: "end" }); }, [messages, sending]);

  const openThread = async (id: string) => {
    setThreadsOpen(false);
    try {
      const msgs = await api<Message[]>(`${API}/chat/threads/${id}/messages`);
      setSessionId(id);
      setMessages(msgs);
      setAttachment(null);
      setScanMeta(null);
    } catch (e) {
      toast.show(errText(e), "error");
    }
  };

  const newChat = () => {
    setSessionId(null);
    setMessages([]);
    setAttachment(null);
    setScanMeta(null);
    setThreadsOpen(false);
  };

  const send = useCallback(async (raw?: string, override?: { attachment?: Attachment | null; meta?: Handoff | null }) => {
    const message = (raw ?? text).trim();
    if (!message || sending) return;
    const att = override?.attachment !== undefined ? override.attachment : attachment;
    const meta = override?.meta !== undefined ? override.meta : scanMeta;
    const form = new FormData();
    form.append("user_message", message);
    form.append("language", lang);
    if (sessionId) form.append("session_id", sessionId);
    if (hasCoords) {
      form.append("latitude", String(coords.lat));
      form.append("longitude", String(coords.lng));
    }
    if (att?.file) form.append("image_file", att.file, att.file.name);
    else if (att?.mediaId) form.append("media_id", att.mediaId);
    if (att) form.append("attached_image_name", att.name.slice(0, 150));
    if (att?.disease) form.append("disease_context", att.disease);
    if (meta) form.append("scan_metadata_json", JSON.stringify({ disease: meta.disease, confidence: meta.confidence, advisory: meta.advisory, env_data: meta.env }));

    const localId = `local-${Date.now()}`;
    setMessages((m) => [...m, { id: localId, role: "user", content: message, image_url: att?.preview ?? null, pending: true }]);
    setText("");
    setAttachment(null);
    setScanMeta(null);
    setSending(true);
    try {
      const res = await api<ChatResponse>(`${API}/chat/message`, { form, timeoutMs: 120000 });
      setSessionId(res.session_id);
      setMessages((m) => [
        ...m.map((x) => (x.id === localId ? { ...x, pending: false, image_url: res.image_url ?? x.image_url } : x)),
        { id: `a-${Date.now()}`, role: "assistant", content: res.reply, disease: res.disease ?? null },
      ]);
      loadThreads();
    } catch (e) {
      setMessages((m) => m.filter((x) => x.id !== localId));
      setText(message);
      if (att) setAttachment(att);
      if (meta) setScanMeta(meta);
      toast.show(errText(e), "error");
    } finally {
      setSending(false);
    }
  }, [text, sending, attachment, scanMeta, lang, sessionId, hasCoords, coords.lat, coords.lng, loadThreads, toast, errText]);

  // Hand-off from Scanner / History: attach the scan photo + metadata and ask the first question automatically.
  useEffect(() => {
    if (handoffDone.current) return;
    handoffDone.current = true;
    const raw = sessionStorage.getItem(HANDOFF_KEY);
    if (!raw) return;
    sessionStorage.removeItem(HANDOFF_KEY);
    try {
      const h = JSON.parse(raw) as Handoff;
      const att: Attachment | null = h.imageUrl ? { name: diseaseName(lang, h.disease), preview: resolveUrl(h.imageUrl), mediaId: h.mediaId ?? undefined, fromHistory: true } : null;
      const q = t("handoffQuestion", { disease: diseaseName(lang, h.disease), conf: num(h.confidence) });
      window.setTimeout(() => send(q, { attachment: att, meta: h }), 200);
    } catch {
      /* ignore broken hand-off */
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const current = threads.find((x) => x.id === sessionId);
  const place = env?.region_name ?? (hasCoords ? `${num(coords.lat, 3)}, ${num(coords.lng, 3)}` : t("noLocation"));

  return (
    <div className="screen" data-testid="chat">
      <AppBar
        minimal
        left={<button className="icon-btn" onClick={() => setThreadsOpen(true)} aria-label={t("conversations")} data-testid="open-threads"><PanelLeft /></button>}
        title={<span className="stack" style={{ gap: 0 }}><span style={{ fontSize: "1.05rem" }}>{current?.title ?? t("chatTitle")}</span>
          {current && <span className="caption" style={{ fontWeight: 600 }}>{t("messagesCount", { n: current.message_count })}</span>}</span>}
        right={<>
          <button className="icon-btn" onClick={newChat} aria-label={t("newChat")} data-testid="new-chat"><SquarePen /></button>
        </>}
      />
      <main className="screen-body" style={{ paddingBottom: 250 }}>
        <OfflineBanner />
        <div className="row wrap">
          <span className="badge badge-primary" data-testid="chat-location">{coords.mode === "gps" ? <Crosshair /> : <MapPin />}{place}</span>
          <button className="chip" onClick={() => setGuideOpen(true)}><Pencil />{t("change")}</button>
          {coords.mode === "manual" && <button className="chip" onClick={requestGps}><Crosshair />{t("autoGps")}</button>}
        </div>
        <div className="chat-wrap" aria-live="polite">
          <div className="msg bot"><div className="avatar"><Sprout /></div><div className="bubble">{t("chatWelcome")}</div></div>
          {messages.map((m) => (
            <div key={m.id} className={`msg ${m.role === "user" ? "me" : "bot"}`} data-testid={`msg-${m.role}`}>
              {m.role === "assistant" && <div className="avatar"><Sprout /></div>}
              <div className="bubble" style={m.pending ? { opacity: 0.8 } : undefined}>
                {m.image_url && <img src={resolveUrl(m.image_url)} alt={m.attached_image_name ?? ""} />}
                {m.role === "assistant" ? <Markdown text={m.content} className="advice" /> : m.content}
              </div>
            </div>
          ))}
          {sending && (
            <div className="msg bot" aria-label={t("thinking")}><div className="avatar"><Sprout /></div><div className="bubble"><span className="typing"><i /><i /><i /></span></div></div>
          )}
          <div ref={listEnd} />
        </div>
      </main>
      <div className="composer">
        {messages.length === 0 && !attachment && (
          <div className="suggestions" style={{ marginBottom: 8 }}>
            {(["suggestWeather", "suggestFertilizer", "suggestShade"] as const).map((k) => (
              <button key={k} className="chip" onClick={() => send(t(k))} disabled={sending}>{t(k)}</button>
            ))}
          </div>
        )}
        {attachment && (
          <div className="attach-strip" data-testid="attach-strip">
            <img src={attachment.preview} alt="" />
            <div className="grow"><b style={{ fontSize: ".9rem" }}>{attachment.name}</b><div className="caption">{attachment.fromHistory ? t("fromHistory") : t("attached")}</div></div>
            <button className="btn btn-sm btn-ghost" onClick={() => setAttachment(null)}>{t("remove")}</button>
          </div>
        )}
        <div className="composer-inner">
          <button className="icon-btn" onClick={() => setPickerOpen(true)} aria-label={t("attach")} data-testid="attach"><Paperclip /></button>
          <textarea rows={1} value={text} placeholder={t("chatPlaceholder")} aria-label={t("chatPlaceholder")} maxLength={2000}
            onChange={(e) => { setText(e.target.value); e.target.style.height = "auto"; e.target.style.height = `${Math.min(120, e.target.scrollHeight)}px`; }}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }} data-testid="chat-input" />
          <VoiceButton onText={(v) => setText((s) => (s ? `${s} ${v}` : v))} />
          <button className="icon-btn send" onClick={() => send()} disabled={sending || !text.trim()} aria-label={t("send")} data-testid="send">
            {sending ? <Spinner /> : <SendHorizontal />}
          </button>
        </div>
      </div>
      <BottomNav />

      <ThreadsSheet open={threadsOpen} onClose={() => setThreadsOpen(false)} threads={threads} current={sessionId} onOpen={openThread}
        onNew={newChat} onChanged={loadThreads} onDeleted={(id) => { if (id === sessionId) newChat(); }} />
      <ImagePicker open={pickerOpen} onClose={() => setPickerOpen(false)} onPick={(a) => { setAttachment(a); setPickerOpen(false); }} onClear={() => { setAttachment(null); setPickerOpen(false); }} />
      <GmapsGuide open={guideOpen} onClose={() => setGuideOpen(false)} onApply={(a, b) => setManual(a, b)} initial={coords} />
    </div>
  );
}

function ThreadsSheet({ open, onClose, threads, current, onOpen, onNew, onChanged, onDeleted }: {
  open: boolean; onClose: () => void; threads: Thread[]; current: string | null; onOpen: (id: string) => void; onNew: () => void;
  onChanged: () => void; onDeleted: (id: string) => void;
}) {
  const { t, lang } = useI18n();
  const toast = useToast();
  const errText = useErrorText();
  const [renaming, setRenaming] = useState<Thread | null>(null);
  const [title, setTitle] = useState("");
  const [confirm, setConfirm] = useState<Thread | null>(null);

  const rename = async () => {
    if (!renaming || !title.trim()) return;
    try {
      await api(`${API}/chat/threads/${renaming.id}`, { method: "PATCH", body: { title: title.trim() } });
      setRenaming(null);
      onChanged();
    } catch (e) {
      toast.show(errText(e), "error");
    }
  };
  const remove = async () => {
    if (!confirm) return;
    try {
      await api(`${API}/chat/threads/${confirm.id}`, { method: "DELETE" });
      onDeleted(confirm.id);
      setConfirm(null);
      onChanged();
      toast.show(t("chatDeleted"));
    } catch (e) {
      toast.show(errText(e), "error");
    }
  };

  return (
    <>
      <Sheet open={open} onClose={onClose} title={t("conversations")} icon={<MessageSquareText />} testId="threads-sheet">
        <div className="stack-sm">
          <button className="btn btn-primary btn-block" onClick={onNew}><SquarePen />{t("newChat")}</button>
          {threads.length === 0 && <p className="body-sm" style={{ textAlign: "center" }}>{t("noConversations")}</p>}
          <div className="menu">
            {threads.map((th) => (
              <div key={th.id} className="menu-item" style={{ paddingRight: 6, background: th.id === current ? "var(--primary-soft)" : undefined }}>
                <button className="grow" style={{ background: "none", border: 0, textAlign: "left", padding: "10px 0", cursor: "pointer", color: "inherit", minWidth: 0 }}
                  onClick={() => onOpen(th.id)} data-testid="thread-item">
                  <div style={{ fontWeight: 700, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{th.title}</div>
                  <div className="caption">{t("messagesCount", { n: th.message_count })} · {timeAgo(lang, th.updated_at ?? th.created_at)}</div>
                </button>
                <button className="icon-btn" style={{ border: 0, width: 42, height: 42 }} aria-label={t("renameChat")} onClick={() => { setRenaming(th); setTitle(th.title); }}><Pencil width={18} /></button>
                <button className="icon-btn" style={{ border: 0, width: 42, height: 42, color: "var(--danger)" }} aria-label={t("deleteChat")} onClick={() => setConfirm(th)}><Trash2 width={18} /></button>
              </div>
            ))}
          </div>
        </div>
      </Sheet>
      <Sheet open={!!renaming} onClose={() => setRenaming(null)} title={t("renameChat")} icon={<Pencil />} center>
        <div className="stack">
          <label className="label" htmlFor="th-title">{t("chatTitleLabel")}</label>
          <input id="th-title" className="input" value={title} maxLength={120} onChange={(e) => setTitle(e.target.value)} onKeyDown={(e) => e.key === "Enter" && rename()} />
          <button className="btn btn-primary btn-block" onClick={rename}>{t("save")}</button>
        </div>
      </Sheet>
      <Sheet open={!!confirm} onClose={() => setConfirm(null)} title={t("deleteChat")} icon={<Trash2 />} iconTone="danger" center>
        <p className="body-sm" style={{ marginTop: 0 }}>{t("deleteChatConfirm")}</p>
        <div className="grid-2"><button className="btn btn-outline" onClick={() => setConfirm(null)}>{t("cancel")}</button>
          <button className="btn btn-danger" onClick={remove} data-testid="confirm-delete-thread">{t("delete")}</button></div>
      </Sheet>
    </>
  );
}

function ImagePicker({ open, onClose, onPick, onClear }: { open: boolean; onClose: () => void; onPick: (a: Attachment) => void; onClear: () => void }) {
  const { t, lang } = useI18n();
  const fileRef = useRef<HTMLInputElement>(null);
  const [scans, setScans] = useState<Scan[] | null>(null);

  useEffect(() => {
    if (!open) return;
    api<Scan[]>(`${API}/scans`, { query: { limit: 30 } }).then(setScans).catch(() => setScans([]));
  }, [open]);

  return (
    <Sheet open={open} onClose={onClose} title={t("pickerTitle")} icon={<ImagePlus />} testId="image-picker">
      <div className="stack">
        <button className="btn btn-outline btn-block" style={{ height: 64, justifyContent: "flex-start" }} onClick={() => fileRef.current?.click()} data-testid="picker-upload">
          <ImagePlus /><span style={{ textAlign: "left" }}><b>{t("pickerUpload")}</b><br /><span className="caption">{t("pickerUploadSub")}</span></span>
        </button>
        <input ref={fileRef} type="file" accept="image/*" hidden data-testid="picker-file"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) onPick({ name: f.name, preview: URL.createObjectURL(f), file: f }); e.target.value = ""; }} />
        <div className="eyebrow">{t("pickerHistory")}</div>
        {scans === null ? <Spinner /> : scans.length === 0 ? <p className="body-sm">{t("pickerNone")}</p> : (
          <div className="grid-2">
            {scans.filter((s) => s.image_url).map((s) => (
              <button key={s.id} className="scan-item" style={{ flexDirection: "column", alignItems: "stretch", padding: 8 }} data-testid="picker-scan"
                onClick={() => onPick({ name: diseaseName(lang, s.disease), preview: resolveUrl(s.image_url), mediaId: s.image_url!.split("/").pop()!.replace(/\.jpg$/, ""), fromHistory: true, disease: s.disease })}>
                <img src={resolveUrl(s.image_url)} alt="" style={{ width: "100%", height: 100 }} />
                <span className="caption" style={{ fontWeight: 700, color: "var(--ink)" }}>{diseaseName(lang, s.disease, true)} · {num(s.confidence, 0)}%</span>
              </button>
            ))}
          </div>
        )}
        <button className="btn btn-ghost" onClick={onClear}><X />{t("pickerClear")}</button>
      </div>
    </Sheet>
  );
}

export function NoChatsHint() {
  const { t } = useI18n();
  return <EmptyState icon={<MessageSquareText />} title={t("noConversations")} />;
}
