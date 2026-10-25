import { Moon, Palette as PaletteIcon, Smartphone, Sun } from "lucide-react";
import { Sheet } from "../Sheet";
import { useI18n } from "../../lib/i18n";
import { PALETTES, useTheme, type Mode } from "../../lib/theme";
import type { TKey } from "../../lib/i18n/en";

const NAMES: Record<string, [TKey, TKey]> = {
  estate: ["paletteEstate", "paletteEstateSub"],
  monsoon: ["paletteMonsoon", "paletteMonsoonSub"],
  harvest: ["paletteHarvest", "paletteHarvestSub"],
  cherry: ["paletteCherry", "paletteCherrySub"],
  sunlight: ["paletteSunlight", "paletteSunlightSub"],
};

export function PalettePicker({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { t } = useI18n();
  const { palette, setPalette, mode, setMode } = useTheme();
  const modes: [Mode, TKey, typeof Sun][] = [["light", "modeLight", Sun], ["dark", "modeDark", Moon], ["auto", "modeAuto", Smartphone]];
  return (
    <Sheet open={open} onClose={onClose} title={t("paletteTitle")} icon={<PaletteIcon />} testId="palette-sheet">
      <div className="stack-sm" role="radiogroup" aria-label={t("paletteTitle")}>
        {PALETTES.map((p) => {
          const [name, sub] = NAMES[p.id];
          const active = p.id === palette;
          return (
            <button key={p.id} className={`palette-opt${active ? " active" : ""}`} role="radio" aria-checked={active}
              onClick={() => setPalette(p.id)} data-testid={`palette-${p.id}`}>
              <span className="swatches" aria-hidden><i style={{ background: p.swatch[0] }} /><i style={{ background: p.swatch[1] }} /></span>
              <div className="grow"><b>{t(name)}</b><div className="caption">{t(sub)}</div></div>
              {active && <span className="badge badge-primary">{t("active")}</span>}
            </button>
          );
        })}
        <div className="segmented" style={{ marginTop: 6 }} role="radiogroup" aria-label={t("darkMode")}>
          {modes.map(([m, key, Icon]) => (
            <button key={m} className={mode === m ? "active" : ""} role="radio" aria-checked={mode === m} onClick={() => setMode(m)} data-testid={`mode-${m}`}>
              <Icon />{t(key)}
            </button>
          ))}
        </div>
      </div>
    </Sheet>
  );
}
