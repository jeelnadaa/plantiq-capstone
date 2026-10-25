import { useEffect, useRef, useState } from "react";
import { Mic, Square } from "lucide-react";
import { Sheet } from "./Sheet";
import { Spinner } from "./common";
import { useI18n } from "../lib/i18n";
import { API, api } from "../lib/api";
import { useToast } from "../lib/toast";

const MAX_MS = 60_000;

function pickMime(): string {
  const types = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus", "audio/mp4"];
  for (const t of types) if (typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported?.(t)) return t;
  return "";
}

type Props = { onText: (text: string) => void; onBusy?: (busy: boolean) => void; className?: string };

/** Mic button → language sheet (Kannada / English) → record → /voice/transcribe → text. */
export function VoiceButton({ onText, onBusy, className }: Props) {
  const { t } = useI18n();
  const toast = useToast();
  const [chooser, setChooser] = useState(false);
  const [state, setState] = useState<"idle" | "recording" | "sending">("idle");
  const rec = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const stopTimer = useRef<number>();

  useEffect(() => () => {
    window.clearTimeout(stopTimer.current);
    rec.current?.stream.getTracks().forEach((tr) => tr.stop());
  }, []);

  const start = async (lang: "kn" | "en") => {
    setChooser(false);
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      toast.show(t("micDenied"), "error");
      return;
    }
    const mime = pickMime();
    const mr = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
    chunks.current = [];
    mr.ondataavailable = (e) => e.data.size && chunks.current.push(e.data);
    mr.onstop = async () => {
      stream.getTracks().forEach((tr) => tr.stop());
      const type = mr.mimeType || "audio/webm";
      const blob = new Blob(chunks.current, { type });
      const ext = type.includes("ogg") ? "ogg" : type.includes("mp4") ? "m4a" : "webm";
      setState("sending");
      onBusy?.(true);
      try {
        const form = new FormData();
        form.append("file", blob, `voice_note.${ext}`);
        form.append("target_language", lang);
        const res = await api<{ text: string; error?: string }>(`${API}/voice/transcribe`, { form, timeoutMs: 90000 });
        if (res.text) onText(res.text);
        else toast.show(t("voiceFailed"), "error");
      } catch {
        toast.show(t("voiceFailed"), "error");
      } finally {
        setState("idle");
        onBusy?.(false);
      }
    };
    rec.current = mr;
    mr.start();
    setState("recording");
    stopTimer.current = window.setTimeout(() => mr.state === "recording" && mr.stop(), MAX_MS);
  };

  const onClick = () => {
    if (state === "recording") {
      window.clearTimeout(stopTimer.current);
      rec.current?.stop();
      return;
    }
    if (state === "idle") setChooser(true);
  };

  return (
    <>
      <button type="button" className={`icon-btn mic ${state === "recording" ? "recording" : ""} ${className ?? ""}`} onClick={onClick}
        aria-label={state === "recording" ? t("stopRecording") : t("speak")} aria-pressed={state === "recording"} disabled={state === "sending"}
        title={state === "sending" ? t("transcribing") : undefined} data-testid="mic-button">
        {state === "sending" ? <Spinner /> : state === "recording" ? <Square /> : <Mic />}
      </button>
      <Sheet open={chooser} onClose={() => setChooser(false)} testId="voice-sheet">
        <div style={{ textAlign: "center", padding: "10px 0 4px" }}>
          <div className="sheet-ico" style={{ margin: "0 auto 10px", width: 72, height: 72, borderRadius: 24, background: "var(--accent-soft)", color: "var(--accent)" }}>
            <Mic width={34} height={34} />
          </div>
          <div className="h2">{t("voiceTitle")}</div>
          <p className="body-sm">{t("voiceSub")}</p>
        </div>
        <div className="stack-sm">
          <button className="btn btn-primary btn-xl btn-block" onClick={() => start("kn")} data-testid="voice-kn">{t("voiceKn")}</button>
          <button className="btn btn-outline btn-xl btn-block" onClick={() => start("en")} data-testid="voice-en">{t("voiceEn")}</button>
          <button className="btn btn-ghost btn-block" onClick={() => setChooser(false)}>{t("cancel")}</button>
        </div>
      </Sheet>
    </>
  );
}
