# Design — "Field Notebook"

Open [design/mockups.html](design/mockups.html) through any static server (e.g. `python -m http.server` in
`claude-plantiq/`, then `/design/mockups.html`). The toolbar switches palettes and light/dark; `?theme=dark`
and `?palette=monsoon` work as URL parameters. 16 phone screens are drawn at 393×852 (Pixel 7 / iPhone 15).

## Who we design for
Coffee growers in Chikkamagaluru, Kodagu and Hassan: often outdoors in bright light or under canopy shade,
one hand holding a leaf, mixed literacy, Kannada first, budget Android phones, patchy Wi-Fi.

## Principles
1. **One obvious next step per screen.** Scanner is home; the Scan button is the raised centre of the nav.
2. **Icon + word, never icon alone** — nav, buttons, badges, risk levels.
3. **Big targets.** Buttons 54 px (primary actions 64 px), inputs 54 px, tap targets ≥ 48 px.
4. **Plain language.** "High rust risk today" not "Incubation risk: High". "How sure is PlantIQ?" not "Class distribution".
5. **Colour is never the only signal.** Risk = colour + icon + word + 3-segment meter.
6. **Readable outdoors.** Body text 17 px, Satoshi 700/900 for headings, a *Sunlight* high-contrast palette with 2 px borders.
7. **Kannada as a first-class language.** Satoshi falls back to Noto Sans Kannada for Kannada glyphs; layouts allow
   ~30 % longer strings; language switch is always one tap away in the app bar.
8. **Mobile-native patterns.** Bottom sheets instead of centred pop-ups, undo toasts instead of confirm dialogs for
   reversible actions, confirm sheets for irreversible ones (delete listing, delete account).

## How it differs from the original
| Original (neo-brutalist) | Rebuild (field notebook) |
|---|---|
| Cobalt/coral, hard black borders and offset shadows | Leaf green + coffee-cherry on warm paper, soft elevation |
| Generic sans | Satoshi (bundled offline) + Noto Sans Kannada |
| Centre modals everywhere | Bottom sheets, confirm only for irreversible actions |
| Text-heavy diagnosis card | Confidence ring, "what to do" grouped by Today / Spray / Timing, sources and dose check |
| Raw metric labels | Weather tiles with plain-language sub-labels and a spray-window tip |
| Filters always open on the page | Sort chips + a filters sheet with a result count |

## Tokens (see [design/tokens.css](design/tokens.css))
| Token | Light (Estate) | Dark |
|---|---|---|
| `--bg` paper | `#F6F1E7` | `#101713` |
| `--surface` | `#FFFFFF` | `#18221C` |
| `--ink` | `#1C2620` | `#EDF2EC` |
| `--primary` leaf | `#1E6B45` | `#62C08D` |
| `--accent` cherry | `#B4452A` | `#F08A6C` |
| success / warning / danger / info | `#2E7D32` / `#A86A00` / `#B3261E` / `#2C6690` | lightened equivalents |

Palettes (light + dark each): **Estate Green** (default), **Monsoon Blue**, **Harvest Amber**, **Coffee Cherry**,
**Sunlight** (high contrast). Type scale 13/15/17/20/24/30/36 px. Radii 10/16/22/28 px. 4-px spacing grid,
16-px gutter. Motion 180 ms ease-out; respects `prefers-reduced-motion`.

## Components ([design/components.css](design/components.css))
App bar (brand, server status dot, language pill, theme), bottom nav with raised Scan, cards (default / tonal),
buttons (primary, accent, tonal, outline, ghost, danger, WhatsApp; sm / default / xl), inputs with leading icon and
trailing action, segmented control, password strength meter + rule checklist, chips (filter/sort), badges, notices
(ok / info / warn / danger), risk banner with meter, weather metric tiles, 3-day forecast, confidence ring, probability
bars, advisory typography, sources list, chat bubbles + typing indicator, composer with attachment strip, voice mic
with recording pulse, listing card with gallery + thumbnails, dual-thumb price range, photo row with caption, dropzone,
history item, empty state, profile hero + stats, settings menu, bottom sheet / centre sheet, validation issue item,
palette option, numbered guide steps, undo toast with timer bar, offline banner, skeleton loader.

## Screens
01 first-launch server connect · 02 sign in (lockout state) · 03 create account (strength, availability, mismatch) ·
04 scanner home with weather + risk + spray window · 05 photo ready + question + voice + progress ·
06 diagnosis result · 07 chat with attachment + suggestions · 08 market browse (others' lot + own lot) ·
09 filters sheet · 10 sell sheet · 11 validation "what & why" · 12 history + undo toast · 13 profile & settings ·
14 colour theme sheet · 15 voice language · 16 Google Maps coordinates guide.
