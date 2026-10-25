import { Languages } from "lucide-react";
import { useI18n } from "../lib/i18n";

export function LangSwitch({ onClick, compact }: { onClick: () => void; compact?: boolean }) {
  const { t } = useI18n();
  return (
    <button className={`lang-pill${compact ? " compact" : ""}`} onClick={onClick} aria-label={`${t("language")}: ${t("langToggle")}`}
      title={t("language")} data-testid="lang-toggle">
      <Languages /> {t("langToggle")}
    </button>
  );
}
