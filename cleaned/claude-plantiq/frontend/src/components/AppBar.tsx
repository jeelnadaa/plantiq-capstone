import { useState, type ReactNode } from "react";
import { Languages, Palette, Server, Sprout } from "lucide-react";
import { useI18n } from "../lib/i18n";
import { useServerStatus } from "../lib/server-status";
import { ServerSettings } from "./modals/ServerSettings";
import { PalettePicker } from "./modals/PalettePicker";

type Props = { title?: ReactNode; icon?: ReactNode; left?: ReactNode; right?: ReactNode; minimal?: boolean };

export function AppBar({ title, icon, left, right, minimal }: Props) {
  const { t, toggle } = useI18n();
  const { status } = useServerStatus();
  const [serverOpen, setServerOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const statusLabel = status === "ok" ? t("statusOk") : status === "warn" ? t("statusWarn") : t("statusDown");

  return (
    <>
      <header className="appbar">
        {left}
        {title !== undefined ? (
          <div className="brand">
            {icon && <div className="brand-mark">{icon}</div>}
            <span>{title}</span>
          </div>
        ) : (
          <div className="brand">
            <div className="brand-mark"><Sprout /></div>
            <span>{t("appName")}</span>
          </div>
        )}
        {right}
        {!minimal && (
          <>
            <button className="icon-btn" onClick={() => setServerOpen(true)} aria-label={`${t("server")}: ${statusLabel}`} title={statusLabel} data-testid="server-button">
              <Server />
              <span className={`status-dot ${status === "ok" ? "ok" : status === "warn" ? "warn" : status === "down" ? "down" : ""}`} />
            </button>
            <button className="lang-pill" onClick={toggle} aria-label={t("language")} data-testid="lang-toggle">
              <Languages /> {t("langShort")}
            </button>
            <button className="icon-btn" onClick={() => setPaletteOpen(true)} aria-label={t("colourTheme")}>
              <Palette />
            </button>
          </>
        )}
      </header>
      <ServerSettings open={serverOpen} onClose={() => setServerOpen(false)} />
      <PalettePicker open={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </>
  );
}
