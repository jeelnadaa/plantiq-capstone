# PlantIQ papers

Two versions of the PlantIQ paper, each in a two-column IEEE conference layout and a one-column layout. Every number
comes from the running system or from the comparison study in [`../compare/`](../compare/README.md).

| Paper | Text (edit this) | Two-column | One-column | Font | Pages |
|---|---|---|---|---|---|
| Full | `paper_content.tex` | `main.tex` → `main.pdf` | `main_onecol.tex` → `main_onecol.pdf` | 10 pt | 12 / 14 |
| Short | `short_content.tex` | `short.tex` → `short.pdf` | `short_onecol.tex` → `short_onecol.pdf` | 12 pt | 6 / 7 |

The full paper has every method detail (equations, algorithms, implementation, test matrix, ablations). The short paper
keeps the abstract, method, evaluation setup, the three comparisons, limitations and conclusion.

## Build

From this folder (Tectonic is bundled in `tools/`):

```bash
tools/tectonic.exe main.tex
tools/tectonic.exe main_onecol.tex
tools/tectonic.exe short.tex
tools/tectonic.exe short_onecol.tex
```

Figures are generated from `scripts/mock_data.json` (real results; the file name is historical) with
`python scripts/make_figures.py`. The two-column wrappers define `\plantiqbalancerefs`, which balances the reference
columns on the last page; re-tune its number when the text length changes.

## Writing rules used

- The text was edited with the `humanizer` skill: no em dashes as connectors, no bold labels in prose, no stock phrases.
- Sources are plain ASCII. Equations avoid constructs whose copied text contains private-use or combining characters
  (large braces, `\hat`, `\neq`), so text copied from the PDFs has no hidden Unicode.
