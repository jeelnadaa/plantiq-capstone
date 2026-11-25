"""Writes report/Report_Change_Log.md: every paragraph and table row that differs between the original
report (Team_35_report_aligned_v2.pdf/.docx) and the rebuilt v3 content, with word-level marks.

Deleted words are shown as ~~old~~ and inserted words as **new**.
"""
import re
import difflib
import sys
import docx
import pymupdf

ORIG_PDF = "../Team_35_report_aligned_v2.pdf"
ORIG_DOCX = "../Team_35_report_aligned_v2.docx"
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "v3"
OUT = "../Report_Change_Log.md" if VARIANT == "v3" else "../Report_Change_Log_patched.md"
FILES = (("content_1.txt", "content_2.txt", "content_3.txt") if VARIANT == "v3"
         else ("content_old_1.txt", "content_old_2.txt", "content_old_3.txt"))
HEADER = "changelog_header.md" if VARIANT == "v3" else "changelog_header_patched.md"
FIXED = "Team_35_report_v3" if VARIANT == "v3" else "Team_35_report_patched"


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"\s+", " ", s).strip()
    return s


def clean_markup(s):
    return s.replace("**", "").replace("~", "")


# ---------------------------------------------------------------- original body paragraphs (from the PDF)
def orig_paragraphs():
    doc = pymupdf.open(ORIG_PDF)
    out = []  # (kind, text)
    for pno in range(12, len(doc)):
        d = doc[pno].get_text("dict")
        lines = []
        for b in d["blocks"]:
            if b["type"] != 0:
                continue
            for l in b["lines"]:
                sp = [s for s in l["spans"] if s["text"].strip()]
                if not sp:
                    continue
                y = l["bbox"][1]
                if y < 60 or y > 765:
                    continue
                lines.append((round(y), l["bbox"][0], "".join(s["text"] for s in l["spans"]).strip(),
                              "Bold" in sp[0]["font"], sp[0]["size"]))
        lines.sort(key=lambda t: (t[0], t[1]))
        for y, x, t, bold, size in lines:
            out.append((y, x, t, bold, size, pno))
    # merge into paragraphs: a line continues the previous one when it is regular 12 pt text
    paras = []
    prev = None
    for y, x, t, bold, size, pno in out:
        if size < 11.5:  # table cells, captions
            prev = None
            continue
        head = bold and size >= 14
        if head:
            paras.append(["H", t])
            prev = None
            continue
        starts_new = prev is None or re.match(r"^(\d+\.|•|Stage \d|Benefits\.|Drawbacks\.|Step \d)", t) or \
            (prev and prev[3] != pno and False)
        if prev is not None and not starts_new and (y - prev[0] < 26 or prev[3] != pno):
            paras[-1][1] += (" " if not paras[-1][1].endswith("-") else "") + t
        else:
            paras.append(["P", t])
        prev = (y, x, t, pno)
    return [(k, norm(t)) for k, t in paras]


# ---------------------------------------------------------------- new body paragraphs (from the content files)
def new_paragraphs():
    out = []
    for f in FILES:
        for ln in open(f, encoding="utf-8").read().split("\n"):
            ln = ln.rstrip()
            if not ln or ln.startswith(("|", "W: ", "T: ", "F: ", "E: ", "A: ")):
                continue
            if re.match(r"^(INPUT|CREATE|SEARCH|\d+\. |      )", ln) and not ln.startswith(("# ",)):
                continue  # algorithm body lines
            if ln.startswith("= "):
                for part in ln[2:].split("|"):
                    out.append(("H", norm(part)))
            elif ln.startswith(("== ", "=== ")):
                out.append(("H", norm(ln.lstrip("= "))))
            else:
                t = re.sub(r"^(# |- |Q: |R: )", "", ln)
                out.append(("P", norm(clean_markup(t))))
    return out


def word_diff(a, b):
    aw, bw = a.split(" "), b.split(" ")
    sm = difflib.SequenceMatcher(None, aw, bw, autojunk=False)
    res = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            res.append(" ".join(aw[i1:i2]))
        if op in ("delete", "replace"):
            res.append("~~" + " ".join(aw[i1:i2]) + "~~")
        if op in ("insert", "replace"):
            res.append("**" + " ".join(bw[j1:j2]) + "**")
    return " ".join(x for x in res if x)


def section_key(h):
    m = re.match(r"^((\d+|[A-D])(\.\d+)*)\s", h)
    return m.group(1) if m else h.upper()


def group(paras):
    sec, cur = [], ["FRONT", []]
    for k, t in paras:
        if k == "H":
            sec.append(cur)
            cur = [t, []]
        else:
            cur[1].append(t)
    sec.append(cur)
    return sec


def main():
    o = group(orig_paragraphs())
    n = group(new_paragraphs())
    out = ["# Report change log", "",
           "Original: `report/Team_35_report_aligned_v2.docx`. Fixed copy: `report/" + FIXED + ".docx` and `.pdf`.",
           "The original files were not modified.", "",
           "How to read this log: ~~struck-through words~~ were removed, **bold words** were added. "
           "Every body paragraph that changed is listed under its section, with the full new text and the marked "
           "difference. Paragraphs that are not listed were carried over word for word. Section A lists the "
           "formatting changes that apply to the whole document; Sections B to D list the content changes.", ""]
    out += open(HEADER, encoding="utf-8").read().split("\n")
    out += front_matter()
    out += ["", "## E. Paragraph-by-paragraph text changes (Chapters 1 to 9, references, appendices)", ""]
    # align sections by heading
    oh = [section_key(h) for h, _ in o]
    nh = [section_key(h) for h, _ in n]
    sm = difflib.SequenceMatcher(None, oh, nh, autojunk=False)
    count = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        pairs = []
        if op == "equal":
            pairs = list(zip(o[i1:i2], n[j1:j2]))
        elif op == "replace" and (i2 - i1) == (j2 - j1):
            pairs = list(zip(o[i1:i2], n[j1:j2]))
        else:
            for sec in o[i1:i2]:
                pairs.append((sec, None))
            for sec in n[j1:j2]:
                pairs.append((None, sec))
        for a, b in pairs:
            if b is None:
                out += [f"### Removed heading: {a[0]}", "", "This heading no longer exists in this form (renamed or "
                        "renumbered; see the matching new heading).", ""]
                continue
            if a is None:
                out += [f"### New section: {b[0]}", "", "No heading with this number was matched in the original (new section, or a heading whose number or "
                        "title changed). Full text in the fixed copy:", ""]
                out += [f"> {p}" for p in b[1]] + [""]
                count += len(b[1])
                continue
            entries = []
            if a[0] != b[0]:
                entries.append(f"- **Heading:** `{a[0]}` → `{b[0]}`")
            op_ = difflib.SequenceMatcher(None, a[1], b[1], autojunk=False)
            for o2, x1, x2, y1, y2 in op_.get_opcodes():
                if o2 == "equal":
                    continue
                olds, news = a[1][x1:x2], b[1][y1:y2]
                k = max(len(olds), len(news))
                for idx in range(k):
                    ot = olds[idx] if idx < len(olds) else ""
                    nt = news[idx] if idx < len(news) else ""
                    if ot == nt:
                        continue
                    count += 1
                    if not ot:
                        entries.append(f"- **Added paragraph:** {nt}")
                    elif not nt:
                        entries.append(f"- **Removed paragraph:** ~~{ot}~~")
                    else:
                        entries.append(f"- **Changed:** {word_diff(ot, nt)}")
            if entries:
                out += [f"### {b[0]}", ""] + entries + [""]
    out += ["", "## F. Table content changes", ""]
    out += table_changes()
    open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("paragraph changes:", count)


def front_matter():
    src = open("build_report.py", encoding="utf-8").read()
    ns = {}
    exec(src[src.index("ACK = ["):src.index("def list_page")], ns)
    if VARIANT != "v3":
        a = src.index("ABSTRACT_OLD = [")
        exec(src[a:src.index("\n]\n", a) + 3], ns)
        ns["ABSTRACT"] = ns["ABSTRACT_OLD"]
    doc = pymupdf.open(ORIG_PDF)
    res = ["", "## Front matter text changes (Acknowledgement and Abstract)", ""]
    for title, page, new in (("Acknowledgement", 3, ns["ACK"]), ("Abstract", 4, ns["ABSTRACT"])):
        blocks = [norm(b[4]) for b in doc[page].get_text("blocks") if b[6] == 0]
        txt = norm(" ".join(b for b in blocks if b.upper() != title.upper()))
        res += [f"### {title}", "", "- **Changed:** " + word_diff(txt, norm(" ".join(new))), ""]
    return res


# ---------------------------------------------------------------- tables
def orig_tables():
    d = docx.Document(ORIG_DOCX)
    res = []
    for t in d.tables:
        rows = []
        for r in t.rows:
            cells = []
            for c in r.cells:
                if cells and c._tc is cells[-1][0]:
                    continue
                cells.append((c._tc, norm(c.text)))
            rows.append(" | ".join(x[1] for x in cells))
        res.append(rows)
    return res


def new_tables():
    res = []
    for f in FILES:
        lines = open(f, encoding="utf-8").read().split("\n")
        i = 0
        while i < len(lines):
            if lines[i].startswith("T: "):
                cap = lines[i][3:]
                i += 1
                rows = []
                while i < len(lines) and (lines[i].startswith("|") or lines[i].startswith("W: ")):
                    if lines[i].startswith("|"):
                        rows.append(" | ".join(norm(c) for c in lines[i].strip().strip("|").split("|")))
                    i += 1
                res.append((cap, rows))
            i += 1
    return res


def table_changes():
    old_rows = set()
    for rows in orig_tables():
        for r in rows:
            old_rows.add(r)
    old_list = sorted(old_rows)
    out = ["Each new table row is compared with the closest row of the original tables. Rows not listed are "
           "unchanged. Header rows of the Table of Contents, List of Figures and List of Tables are regenerated "
           "automatically and are not listed.", ""]
    for cap, rows in new_tables():
        entries = []
        for r in rows:
            if r in old_rows:
                continue
            best = difflib.get_close_matches(r, old_list, n=1, cutoff=0.55)
            if best:
                entries.append(f"- {word_diff(best[0], r)}")
            else:
                entries.append(f"- **New row:** {r}")
        if entries:
            out += [f"### {cap}", ""] + entries + [""]
    return out


if __name__ == "__main__":
    main()
