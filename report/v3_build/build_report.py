"""Builds report/Team_35_report_v3.docx from content_*.txt (run from report/v3_build/).

Formatting follows the rules in report/Report_Review_Findings.md (taken from report/Perfect.pdf).
Page numbers in the TOC / lists are PAGEREF fields; update_and_export.ps1 refreshes them in Word.
"""
import re
import copy
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_BREAK, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree
import latex2mathml.converter as l2m

import sys
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "v3"
ALL_HEADERS = "--all-headers" in sys.argv[2:]
OUT = (sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv
       else ("../Team_35_report_v3.docx" if VARIANT == "v3" else "../Team_35_report_patched.docx"))
CONTENT = (["content_1.txt", "content_2.txt", "content_3.txt"] if VARIANT == "v3"
           else ["content_old_1.txt", "content_old_2.txt", "content_old_3.txt"])
LOGO = "../../Phase-3-Review3/deck-source/assets/pes_logo.png"
TNR = "Times New Roman"
ARIAL = "Arial"
TITLE = ("PlantIQ: A Unified AI Platform for Smart Cultivation, Direct Market Visibility, "
         "and Advanced Advisory Services for Farmers in Karnataka")
XSL = etree.XSLT(etree.parse(r"C:/Program Files/Microsoft Office/root/Office16/MML2OMML.XSL"))

PAGE_W, PAGE_H = Inches(8.27), Inches(11.69)
LM = RM = TM = BM = Cm(2.0)
TEXT_W = PAGE_W - LM - RM

doc = Document()
_bm = [0]
toc, lof, lot, loa = [], [], [], []


# ------------------------------------------------------------------ low-level helpers
def set_font(run, size=12, bold=None, italic=None, font=TNR, color=None):
    run.font.name = font
    run.font.size = Pt(size)
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), font)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    return run


def pfmt(p, align=WD_ALIGN_PARAGRAPH.LEFT, before=0, after=8, line=1.5, keep=False, left=None,
         first=None, right=None, page_break=False):
    f = p.paragraph_format
    p.alignment = align
    f.space_before = Pt(before)
    f.space_after = Pt(after)
    f.line_spacing = line
    f.keep_with_next = keep
    f.widow_control = True
    if left is not None:
        f.left_indent = left
    if first is not None:
        f.first_line_indent = first
    if right is not None:
        f.right_indent = right
    if page_break:
        f.page_break_before = True
    return p


REF_RE = re.compile(r"(Figures? \d+\.\d+|Tables? [0-9A-D]+\.\d+|Algorithm \d+\.\d+|Equation \(\d+\.\d+\))")


def add_rich(p, text, size=12, font=TNR, base_bold=False, base_italic=False, refs=True, color=None):
    """**bold**, ~italic~ and automatic italics for figure/table/algorithm/equation references."""
    for tok in re.split(r"(\*\*.+?\*\*|~.+?~)", text):
        if not tok:
            continue
        b, i = base_bold, base_italic
        if tok.startswith("**"):
            tok, b = tok[2:-2], True
        elif tok.startswith("~") and tok.endswith("~") and len(tok) > 1:
            tok, i = tok[1:-1], True
        parts = REF_RE.split(tok) if refs else [tok]
        for part in parts:
            if not part:
                continue
            is_ref = refs and REF_RE.fullmatch(part) is not None
            set_font(p.add_run(part), size, bold=(False if is_ref else b), italic=(True if is_ref else i),
                     font=font, color=color)
    return p


def bookmark(p, name):
    _bm[0] += 1
    s = OxmlElement("w:bookmarkStart")
    s.set(qn("w:id"), str(_bm[0]))
    s.set(qn("w:name"), name)
    e = OxmlElement("w:bookmarkEnd")
    e.set(qn("w:id"), str(_bm[0]))
    p._p.insert(0, s)
    p._p.append(e)


def field(p, instr, size=12, bold=False, placeholder="1", font=TNR):
    def fc(t):
        r = p.add_run()
        set_font(r, size, bold=bold, font=font)
        el = OxmlElement("w:fldChar")
        el.set(qn("w:fldCharType"), t)
        r._element.append(el)
    fc("begin")
    r = p.add_run()
    set_font(r, size, bold=bold, font=font)
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = f" {instr} "
    r._element.append(it)
    fc("separate")
    set_font(p.add_run(placeholder), size, bold=bold, font=font)
    fc("end")


def set_cell_borders(cell, **kw):
    tcPr = cell._tc.get_or_add_tcPr()
    b = tcPr.find(qn("w:tcBorders"))
    if b is None:
        b = OxmlElement("w:tcBorders")
        tcPr.append(b)
    for edge, val in kw.items():
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), val)
        if val != "nil":
            el.set(qn("w:sz"), "6")
            el.set(qn("w:color"), "000000")
        b.append(el)


def table_borders(table, val="single"):
    tblPr = table._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), val)
        if val != "nil":
            el.set(qn("w:sz"), "6")
            el.set(qn("w:color"), "000000")
        b.append(el)
    old = tblPr.find(qn("w:tblBorders"))
    if old is not None:
        tblPr.remove(old)
    tblPr.append(b)


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear")
    s.set(qn("w:color"), "auto")
    s.set(qn("w:fill"), fill)
    tcPr.append(s)


def cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    trPr.append(el)


def cell_margins(table, top=40, bottom=40, left=80, right=80):
    tblPr = table._tbl.tblPr
    m = OxmlElement("w:tblCellMar")
    for k, v in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{k}")
        el.set(qn("w:w"), str(v))
        el.set(qn("w:type"), "dxa")
        m.append(el)
    tblPr.append(m)


def tbl_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    trPr.append(el)


def make_table(rows, widths_pct, header=True, borders=True, size=12, font=TNR, keep=True,
               header_fill="F2F2F2", total_width=None, align=WD_TABLE_ALIGNMENT.CENTER, line=1.0,
               repeat_header=False):
    total = total_width or TEXT_W
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.alignment = align
    t.autofit = False
    table_borders(t, "single" if borders else "nil")
    cell_margins(t)
    widths = [int(total * w / sum(widths_pct)) for w in widths_pct]
    if header and repeat_header:
        tbl_header(t.rows[0])
    for ri, row in enumerate(rows):
        cant_split(t.rows[ri])
        for ci, val in enumerate(row):
            c = t.cell(ri, ci)
            c.width = widths[ci]
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = c.paragraphs[0]
            last = ri == len(rows) - 1
            pfmt(p, before=0, after=0, line=line, keep=(ri == 0 and not last) if not keep else (keep and not last))
            is_head = header and ri == 0
            if isinstance(val, tuple):  # (text, dict of options)
                txt, opt = val
            else:
                txt, opt = val, {}
            if "fill" in opt:
                shade(c, opt["fill"])
            if "indent" in opt:
                p.paragraph_format.left_indent = opt["indent"]
            if "align" in opt:
                p.alignment = opt["align"]
            if "pageref" in opt:
                field(p, f"PAGEREF {opt['pageref']} \\h", size=size, bold=opt.get("bold", False), font=font)
                continue
            add_rich(p, txt, size=size, font=font, base_bold=is_head or opt.get("bold", False), refs=False)
            if is_head and header_fill:
                shade(c, header_fill)
    for ci, w in enumerate(widths):
        t.columns[ci].width = w
    return t


def para(text="", **kw):
    size = kw.pop("size", 12)
    font = kw.pop("font", TNR)
    bold = kw.pop("bold", False)
    italic = kw.pop("italic", False)
    refs = kw.pop("refs", True)
    color = kw.pop("color", None)
    p = doc.add_paragraph()
    pfmt(p, **kw)
    if text:
        add_rich(p, text, size=size, font=font, base_bold=bold, base_italic=italic, refs=refs, color=color)
    return p


def caption(text, kind, keep):
    """Caption: TNR 10, italic, not bold, centred, muted navy (#444499). kind: fig/tab/alg."""
    m = re.match(r"(Figure|Table|Algorithm) ([0-9A-D]+\.\d+):\s*(.*)", text)
    label, num, title = m.group(1), m.group(2), m.group(3)
    p = doc.add_paragraph()
    pfmt(p, align=WD_ALIGN_PARAGRAPH.CENTER, before=6 if kind != "fig" else 4, after=6 if kind != "fig" else 12,
         line=1.0, keep=keep)
    set_font(p.add_run(f"{label} {num}: {title}"), 10, bold=False, italic=True, color="444499")
    name = f"_{kind}_{num.replace('.', '_')}"
    bookmark(p, name)
    {"fig": lof, "tab": lot, "alg": loa}[kind].append((num, title, name))
    return p


def equation(latex, number):
    """Display equation centred, its number right-aligned on the same line (borderless 1 x 3 table)."""
    if doc.paragraphs:
        doc.paragraphs[-1].paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=3)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    table_borders(t, "nil")
    cant_split(t.rows[0])
    ws = [int(TEXT_W * 0.12), int(TEXT_W * 0.76), int(TEXT_W * 0.12)]
    for ci, w in enumerate(ws):
        t.cell(0, ci).width = w
        t.columns[ci].width = w
        t.cell(0, ci).vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        pfmt(t.cell(0, ci).paragraphs[0], before=4, after=4, line=1.0)
    p = t.cell(0, 1).paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    np_ = t.cell(0, 2).paragraphs[0]
    np_.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_font(np_.add_run(number), 12)
    bookmark(np_, "_eq_" + number.strip("()").replace(".", "_"))
    omml = XSL(etree.fromstring(l2m.convert(latex))).getroot()
    # make the equation Cambria Math 12 pt
    for r in omml.iter("{http://schemas.openxmlformats.org/officeDocument/2006/math}r"):
        rpr = OxmlElement("w:rPr")
        f = OxmlElement("w:rFonts")
        f.set(qn("w:ascii"), "Cambria Math")
        f.set(qn("w:hAnsi"), "Cambria Math")
        rpr.append(f)
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), "26")
        rpr.append(sz)
        r.insert(1 if r.find("{http://schemas.openxmlformats.org/officeDocument/2006/math}rPr") is not None else 0, rpr)
    M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
    om = etree.fromstring(etree.tostring(omml))
    para_el = etree.SubElement(etree.Element(M + "oMathPara"), M + "oMathParaPr")
    mp = para_el.getparent()
    jc = etree.SubElement(para_el, M + "jc")
    jc.set(M + "val", "center")
    mp.append(om)
    p._p.append(mp)
    para("", after=2, line=1.0)


ALG_TOK_RE = re.compile(
    r'(//.*|"[^"]*"|\b(?:INPUT|CREATE|SEARCH|IF|THEN|ELSE|FOR|RETURN|ON FAILURE|VALIDATE|each|in|exists|and|if)\b|[A-Za-z_][A-Za-z0-9_-]*(?=\()|\b\d+(?:\.\d+)?\b)'
)
ALG_KW = {"INPUT", "CREATE", "SEARCH", "IF", "THEN", "ELSE", "FOR", "RETURN", "ON FAILURE", "VALIDATE",
          "each", "in", "exists", "and", "if"}


def add_code_runs(p, text, base_bold=False):
    for i, tok in enumerate(ALG_TOK_RE.split(text)):
        if not tok:
            continue
        if tok.startswith("//"):
            set_font(p.add_run(tok), 10, font="Consolas", color="888888")
        elif tok.startswith('"') or re.fullmatch(r"\d+(?:\.\d+)?", tok):
            set_font(p.add_run(tok), 10, font="Consolas", bold=base_bold, color="880000")
        elif tok in ALG_KW:
            set_font(p.add_run(tok), 10, font="Consolas", bold=True, color="444444")
        elif i % 2 == 1:  # function call matched before '('
            set_font(p.add_run(tok), 10, font="Consolas", bold=True, color="397300")
        else:
            set_font(p.add_run(tok), 10, font="Consolas", bold=base_bold, color="444444")


def algorithm(cap, lines):
    caption(cap, "alg", keep=True)
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_borders(t, "single")
    cell_margins(t, 80, 80, 140, 140)
    cant_split(t.rows[0])
    c = t.cell(0, 0)
    c.width = int(TEXT_W * 0.96)
    shade(c, "F7F7F7")
    first = True
    for ln in lines:
        p = c.paragraphs[0] if first else c.add_paragraph()
        first = False
        m = re.match(r"^(\d+)\.\s", ln)
        cont = ln.startswith("      ")
        pfmt(p, before=0, after=0, line=1.15, keep=True,
             left=Inches(0.3) if (m or cont) else Inches(0), first=Inches(-0.3) if m else Inches(0))
        if m:
            p.paragraph_format.tab_stops.add_tab_stop(Inches(0.3))
            set_font(p.add_run(m.group(1) + ".\t"), 10, font="Consolas", color="444444")
            ln = ln[len(m.group(0)):]
        add_code_runs(p, ln.strip() if cont else ln)
    para("", after=4, line=1.0)


def figure(path, cap, width_in):
    p = doc.add_paragraph()
    pfmt(p, align=WD_ALIGN_PARAGRAPH.CENTER, before=6, after=2, line=1.0, keep=True)
    p.add_run().add_picture(path, width=Inches(width_in))
    caption(cap, "fig", keep=False)


_body_started = [False]
_in_ref_sec = [False]


def chapter(label, title, number=None):
    pb = True
    if not _body_started[0]:
        _body_started[0] = True
        pb = False
    elif not _in_ref_sec[0]:
        # Each chapter (and REFERENCES) starts a new section so opening pages omit headers
        s = doc.add_section(WD_SECTION.NEW_PAGE)
        setup_section(s)
        set_page_borders(s, False)
        pb = False
        if label is None and title.upper() == "REFERENCES":
            _in_ref_sec[0] = True
    if label:
        para(label, size=18, bold=True, before=0, after=6, line=1.15, keep=True, page_break=pb, refs=False)
        t = para(title, size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=18, line=1.15,
                 keep=True, refs=False)
    else:
        t = para(title, size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=18, line=1.15,
                 keep=True, page_break=pb, refs=False)
    name = f"_toc_{len(toc)}"
    bookmark(t, name)
    toc.append((0, number, title if not label or label.startswith("CHAPTER") else f"{label}: {title}", name))


def heading(level, text):
    size = 16 if level == 2 else 14
    p = para(text, size=size, bold=True, before=18 if level == 2 else 12, after=8 if level == 2 else 6,
             line=1.15, keep=True, refs=False)
    name = f"_toc_{len(toc)}"
    bookmark(p, name)
    toc.append((level, None, text, name))


def list_item(text, marker, size=12):
    p = doc.add_paragraph()
    pfmt(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=0, after=4, line=1.5, left=Inches(0.5), first=Inches(-0.25))
    p.paragraph_format.tab_stops.add_tab_stop(Inches(0.5))
    set_font(p.add_run(marker + "\t"), size, font=ARIAL if marker == "\u25cf" else TNR,
             )
    if marker == "\u25cf":
        p.runs[0].font.size = Pt(9)
    add_rich(p, text, size=size)
    return p


# ------------------------------------------------------------------ content parser
def render(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    i, num = 0, 0
    pending_keep = None
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln:
            num = 0
            i += 1
            continue
        if ln.startswith("= "):
            body = ln[2:]
            if "|" in body:
                label, title = [s.strip() for s in body.split("|")]
                n = label.split()[-1] if label.startswith("CHAPTER") else None
                chapter(label, title, n)
            else:
                chapter(None, body.strip())
        elif ln.startswith("=== "):
            heading(3, ln[4:])
        elif ln.startswith("== "):
            heading(2, ln[3:])
        elif ln.startswith("T: "):
            cap = ln[3:]
            i += 1
            widths = None
            if lines[i].startswith("W: "):
                widths = [int(x) for x in lines[i][3:].split(",")]
                i += 1
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            caption(cap, "tab", keep=True)
            multi_page_tbl = cap.startswith("Table A.1:")
            make_table(rows, widths or [1] * len(rows[0]), keep=not multi_page_tbl, repeat_header=multi_page_tbl)
            para("", after=2, line=1.0)
            continue
        elif ln.startswith("F: "):
            f, cap, w = [s.strip() for s in ln[3:].split("|")]
            figure(f, cap, float(w))
        elif ln.startswith("E: "):
            lt, n = [s.strip() for s in ln[3:].rsplit("|", 1)]
            equation(lt, n)
        elif ln.startswith("A: "):
            cap = ln[3:]
            i += 1
            body = []
            while i < len(lines) and lines[i].strip():
                body.append(lines[i].rstrip())
                i += 1
            algorithm(cap, body)
            continue
        elif ln.startswith("# "):
            num += 1
            list_item(ln[2:], f"{num}.")
        elif ln.startswith("- "):
            list_item(ln[2:], "\u25cf")
        elif ln.startswith("Q: "):
            para(ln[3:], italic=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, left=Inches(0.5), right=Inches(0.5), before=4, after=10)
        elif ln.startswith("R: "):
            num += 1
            p = doc.add_paragraph()
            pfmt(p, before=0, after=6, line=1.15, left=Inches(0.5), first=Inches(-0.5))
            p.paragraph_format.tab_stops.add_tab_stop(Inches(0.5))
            set_font(p.add_run(f"[{num}]\t"), 12)
            add_rich(p, ln[3:], refs=False)
        else:
            num = 0 if not ln.startswith("**Step") else num
            para(ln, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        i += 1


# ------------------------------------------------------------------ front matter
def setup_section(sec):
    sec.page_width, sec.page_height = PAGE_W, PAGE_H
    sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = LM, RM, TM, BM
    sec.header_distance = Cm(0.55)
    sec.footer_distance = Cm(0.80)


def set_page_borders(sec, enabled=True, sz="24", space="14", color="000000"):
    sectPr = sec._sectPr
    old = sectPr.find(qn("w:pgBorders"))
    if old is not None:
        sectPr.remove(old)
    if not enabled:
        return
    pb = OxmlElement("w:pgBorders")
    pb.set(qn("w:offsetFrom"), "text")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), sz)
        el.set(qn("w:space"), space)
        el.set(qn("w:color"), color)
        pb.append(el)
    pgMar = sectPr.find(qn("w:pgMar"))
    if pgMar is not None:
        pgMar.addnext(pb)
    else:
        sectPr.append(pb)


def centre(text, size, bold=False, italic=False, font=ARIAL, before=0, after=0, line=1.15, color=None):
    return para(text, size=size, bold=bold, italic=italic, font=font, align=WD_ALIGN_PARAGRAPH.CENTER,
                before=before, after=after, line=line, refs=False, color=color)


MEMBERS = [("Jeel Nada", "PES2UG23CS357"), ("Nidhi N", "PES2UG23CS384"), ("Mohammed Ayaan", "PES2UG23AM058")]


def names_table(font=ARIAL, size=12):
    t = make_table([[n, s] for n, s in MEMBERS], [55, 45], header=False, borders=False, size=size, font=font,
                   keep=True, total_width=Inches(4.2), line=1.15)
    for r in t.rows:
        for c in r.cells:
            c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in c.paragraphs[0].runs:
                run.bold = True
    return t


def cover():
    p = centre("", 12, before=26)  # balances the page vertically
    p.add_run().add_picture(LOGO, width=Inches(1.6))
    centre("Dissertation on", 16, bold=True, italic=True, before=10, after=10)
    centre(f"\u201c{TITLE}\u201d", 16, bold=True, after=14, color="006FBF")
    centre("Submitted in partial fulfilment of the requirements for the award of degree of", 12.5,
           italic=True, after=10)
    centre("Bachelor of Technology", 16, bold=True)
    centre("in", 16, bold=True)
    centre("Computer Science & Engineering", 16, bold=True, after=14)
    centre("UE23CS441A \u2013 Capstone Project Phase - 3", 16, bold=True, after=16)
    centre("Submitted by:", 12, bold=True, italic=True, after=6)
    names_table()
    centre("Under the guidance of", 12, italic=True, before=14, after=6)
    centre("Prof. Deepti C.", 14, bold=True, font=TNR)
    centre("Assistant Professor", 14, font=TNR)
    centre("PES University", 14, font=TNR, after=14)
    centre("Aug - Nov 2026", 12, bold=True, after=14, color="BF4F4C")
    centre("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", 12, bold=True)
    centre("FACULTY OF ENGINEERING", 12)
    centre("PES UNIVERSITY", 12, bold=True)
    centre("(Established under Karnataka Act No. 16 of 2013)", 10)
    centre("Electronic City, Hosur Road, Bengaluru \u2013 560 100, Karnataka, India", 10)


def certificate():
    p = centre("", 12, before=18)
    p.paragraph_format.page_break_before = True
    p.add_run().add_picture(LOGO, width=Inches(1.3))
    centre("PES UNIVERSITY", 16, bold=True, before=2)
    centre("(Established under Karnataka Act No. 16 of 2013)", 8)
    centre("Electronic City, Hosur Road, Bengaluru \u2013 560 100, Karnataka, India", 10, after=8)
    centre("FACULTY OF ENGINEERING", 12, bold=True, after=8)
    centre("CERTIFICATE", 20, bold=True, after=8)
    centre("This is to certify that the dissertation entitled", 12, italic=True, after=8)
    centre(f"\u2018{TITLE}\u2019", 14, bold=True, after=8)
    centre("is a bonafide work carried out by", 11, italic=True, after=8)
    names_table()
    p = para("In partial fulfilment for the completion of seventh semester Capstone Project Phase - 3 (UE23CS441A) "
             "in the Program of Study - Bachelor of Technology in Computer Science and Engineering under rules and "
             "regulations of PES University, Bengaluru during the period Aug 2026 \u2013 Nov. 2026. It is certified "
             "that all corrections / suggestions indicated for internal assessment have been incorporated in the "
             "report. The dissertation has been approved as it satisfies the 7", size=10, font=ARIAL,
             align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=10, after=18, line=1.4, refs=False)
    sup = set_font(p.add_run("th"), 10, font=ARIAL)
    sup.font.superscript = True
    set_font(p.add_run(" semester academic requirements in respect of project work."), 10, font=ARIAL)
    rows = [["Signature", "Signature", "Signature"],
            [("Prof. Deepti C.", {"bold": True}), ("Dr. Sandesh B J", {"bold": True}), ("Dr. Sridhar K S", {"bold": True})],
            ["Assistant Professor", "Chairperson", "Registrar"]]
    t = make_table(rows, [1, 1, 1], header=False, borders=False, size=10, font=ARIAL, line=1.15)
    for r in t.rows:
        for c in r.cells:
            c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    centre("External Viva", 10, bold=True, before=18, after=6)
    rows = [[("Name of the Examiners", {"bold": True}), ("Signature with Date", {"bold": True})],
            ["1. ______________________________", "______________________________"],
            ["2. ______________________________", "______________________________"]]
    t = make_table(rows, [1, 1], header=False, borders=False, size=10, font=ARIAL, line=1.8,
                   total_width=Inches(5.4))
    for r in t.rows:
        for c in r.cells:
            c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER


def front_page(title, first=False, page_break=True):
    p = para(title, size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=24, line=1.15,
             page_break=page_break, refs=False)
    return p


def declaration():
    front_page("DECLARATION", page_break=False)
    p = para("", size=14, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line=1.5, after=24)
    add_rich(p, "We hereby declare that the Capstone Project Phase - 3 entitled **\u201c" + TITLE + "\u201d** has been "
             "carried out by us under the guidance of Prof. Deepti C., Assistant Professor, and submitted in partial "
             "fulfilment of the course requirements for the award of degree of **Bachelor of Technology** in "
             "**Computer Science and Engineering** of **PES University, Bengaluru** during the academic semester "
             "Aug \u2013 Nov. 2026. The matter embodied in this report has not been submitted to any other university "
             "or institution for the award of any degree.", size=14, refs=False)
    rows = [[(s, {"bold": True}), (n, {"bold": True}), ("______________", {"bold": True})] for n, s in
            [(m[0], m[1]) for m in MEMBERS]]
    make_table(rows, [34, 38, 28], header=False, borders=False, size=14, line=1.5, total_width=Inches(5.6))


ACK = [
    "I would like to express my gratitude to Prof. Deepti C., Assistant Professor, Department of Computer Science and "
    "Engineering, PES University, for her continuous guidance, assistance and encouragement throughout the development "
    "of this UE23CS441A Capstone Project Phase - 3. The feedback she gave me across all three project reviews pushed me "
    "to treat the work as an engineering exercise and not only as a demonstration.",
    "I am grateful to the Capstone Project Coordinator, Dr. Vandana M. Ladwani, Associate Professor, Department of "
    "Computer Science and Engineering, PES University, for organising, managing and helping with the entire process.",
    "I take this opportunity to thank Dr. Sandesh B J, Chairperson, Department of Computer Science and Engineering, PES "
    "University, for all the knowledge and support I have received from the department. I would like to thank Dr. "
    "Sridhar K S, Registrar, PES University, for his help.",
    "I am deeply grateful to Late Dr. M. R. Doreswamy, Founder, PES University, whose vision and dedication continue to "
    "inspire generations of learners. I would like to express my sincere gratitude to Prof. Jawahar Doreswamy, "
    "Chancellor, PES University, Dr. Suryaprasad J, Vice-Chancellor, PES University, and Dr. Nagarjuna Sadineni, Pro "
    "Vice-Chancellor, PES University, for providing me with various opportunities and enlightenment every step of the way.",
    "I am also grateful to the coffee planters who were willing to test the application and gave their honest feedback, "
    "which shaped the direction of the next version. Last but by no means least, this project would not have been "
    "possible without the ongoing support and encouragement I have received from my family and friends.",
]

ABSTRACT = [
    "While Karnataka is the leading producer of coffee in India, its small farmers lack timely advice on leaf diseases "
    "in their local language and have little direct access to buyers without intermediaries. Diagnosis, advice, "
    "conversation and market access are brought together in one application. Five leaf conditions are identified by a "
    "fine-tuned ResNet-50, which scores about 90% on validation images, about 80% on unseen leaves and 97.9% in a leak-free "
    "cross-validation on public images. Its result is passed to a hybrid retrieval-augmented advisory engine that combines "
    "FAISS, BM25, rank fusion, a cross-encoder reranker and live weather, and each answer is labelled Verified or "
    "Caution by a dosage audit.",
    "Voice or text input is accepted by a Kannada and English chatbot, and listings are sorted by distance in a direct "
    "marketplace with one-tap Maps, call and WhatsApp. On 75 coffee questions, the supporting evidence is found by the "
    "hybrid retriever for 87% of questions, against 50% for dense-only retrieval. All 373 automated tests pass; one latency target, the "
    "first CNN call after start-up (704 ms), was missed.",
]


def list_page(title, header, entries, groups=None):
    front_page(title)
    rows = [[(h, {"bold": True}) for h in header]]
    for e in entries:
        rows.append(e)
    t = make_table(rows, [16, 70, 14], header=True, borders=False, size=12, line=1.3, header_fill=None)
    for r in t.rows:
        r.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    return t


ABSTRACT_OLD = [
    "While Karnataka is the leading producer of coffee in India, its small farmers lack timely advice on leaf diseases "
    "in their local language and have little direct access to buyers without intermediaries. Five leaf conditions "
    "are identified by a fine-tuned ResNet-50, which scores about 90% on validation images and about 80% on unseen "
    "leaves. Its result is passed to a hybrid retrieval-augmented advisory engine that combines FAISS, BM25, rank "
    "fusion, a cross-encoder reranker and live weather, and each answer is labelled Verified or Caution by a dosage audit.",
    "Voice or text input is accepted by a Kannada and English chatbot, and listings are sorted by distance in a direct "
    "marketplace with one-tap Maps, call and WhatsApp. All 48 automated tests pass in about 103 seconds; one latency target, the first "
    "CNN call after start-up (704 ms), was missed.",
]
if VARIANT != "v3":
    ABSTRACT = ABSTRACT_OLD

# ------------------------------------------------------------------ build
sec0 = doc.sections[0]
setup_section(sec0)
sec0.left_margin = sec0.right_margin = (LM + RM) // 2  # equal side margins, same text width
sec0.header_distance, sec0.footer_distance = TM, BM  # keep pgBorders aligned with body margins, not empty header/footer distance
set_page_borders(sec0, True)
st = doc.styles["Normal"]
st.font.name = TNR
st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), TNR)

cover()
certificate()

# Remaining front matter (Declaration through List of Tables) has no page border
front_sec = doc.add_section(WD_SECTION.NEW_PAGE)
setup_section(front_sec)
front_sec.left_margin = front_sec.right_margin = (LM + RM) // 2
set_page_borders(front_sec, False)

declaration()
front_page("ACKNOWLEDGEMENT")
for a in ACK:
    para(a, size=14, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line=1.5, after=10, refs=False)
front_page("ABSTRACT")
for a in ABSTRACT:
    para(a, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line=1.5, after=10, refs=False)

# placeholders for TOC/LOF/LOT: built after the body (needs bookmark lists), then moved here
marker = para("")
marker_el = marker._p

# body section (Chapter 1 starts here; subsequent chapters add new sections in chapter())
body_sec = doc.add_section(WD_SECTION.NEW_PAGE)
setup_section(body_sec)
set_page_borders(body_sec, False)
body_start = len(doc.element.body)
for f in CONTENT:
    render(f)


# ---- keep chosen sections on one page (ids listed in keep_<variant>.txt by fit_sections.py)
def keep_sections(ids):
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

    from docx.text.paragraph import Paragraph as _P

    def set_keep(p_el):
        f = _P(p_el, None).paragraph_format  # python-docx writes the elements in schema order
        f.keep_with_next = True
        f.keep_together = True

    current, members = None, {}
    for el in doc.element.body.iterchildren():
        if el.tag == W + "p":
            ppr = el.find(W + "pPr")
            if ppr is not None and ppr.find(W + "pageBreakBefore") is not None:
                current = None  # a new page ends the current section
            for bm in el.iter(W + "bookmarkStart"):
                name = bm.get(qn("w:name"))
                if name and name.startswith("_toc_"):
                    current = int(name[5:])
        if current in ids:
            members.setdefault(current, []).append(el)
        if el.tag == W + "p":
            ppr = el.find(W + "pPr")
            if ppr is not None and ppr.find(W + "sectPr") is not None:
                current = None  # section break starts the next chapter on a new page
    for sid, els in members.items():
        # trailing empty spacer paragraphs do not count as the section's last element
        while els and els[-1].tag == W + "p" and not "".join(els[-1].itertext()).strip() \
                and not list(els[-1].iter(W + "drawing")):
            els.pop()
        for k, el in enumerate(els):
            ps = [el] if el.tag == W + "p" else list(el.iter(W + "p"))
            for p_el in ps:
                if k < len(els) - 1:
                    set_keep(p_el)
                else:  # last element: never split it, but do not chain it to the next section
                    _P(p_el, None).paragraph_format.keep_together = True


try:
    KEEP = {int(x) for x in open(f"keep_{VARIANT}.txt").read().split()}
except FileNotFoundError:
    KEEP = set()
keep_sections(KEEP)

# ---- TOC / LOF / LOT, built at the end of the document, then moved before the marker
tail_before = len(doc.element.body) - 1  # last element is sectPr
front_page("TABLE OF CONTENTS")
rows = [[("Chapter No.", {"bold": True}), ("Title", {"bold": True}), ("Page No.", {"bold": True})]]
for level, number, title, name in toc:
    if level == 0:
        rows.append([(f"{number}." if number else "", {"bold": True}), (title.upper(), {"bold": True}),
                     ("", {"pageref": name, "bold": True})])
    else:
        ind = Inches(0.25) if level == 2 else Inches(0.55)
        rows.append(["", (title, {"indent": ind}), ("", {"pageref": name})])
t = make_table(rows, [14, 74, 12], header=True, borders=False, size=12, line=1.25, header_fill=None)
for r in t.rows:
    r.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
for r in t.rows:  # TOC is long: allow it to flow across pages
    for c in r.cells:
        c.paragraphs[0].paragraph_format.keep_with_next = False

list_page("LIST OF FIGURES", ["Figure No.", "Title", "Page No."],
          [[n, t_, ("", {"pageref": nm})] for n, t_, nm in lof])
rows_t = [[n, t_, ("", {"pageref": nm})] for n, t_, nm in lot]
rows_t.append(["", ("Algorithms", {"bold": True}), ""])
rows_t += [[n, t_, ("", {"pageref": nm})] for n, t_, nm in loa]
tt = list_page("LIST OF TABLES", ["Table No.", "Title", "Page No."], rows_t)
for r in tt.rows:
    for c in r.cells:
        c.paragraphs[0].paragraph_format.keep_with_next = False

body = doc.element.body
tail = list(body)[tail_before:]
sectPr = body[-1] if body[-1].tag == qn("w:sectPr") else None
for el in tail:
    if el is sectPr:
        continue
    marker_el.addprevious(el)
# the marker paragraph carries the front-matter section break (sectPr of section 0)

# ---- header / footer for body sections (no header on chapter opening pages; footer on all body pages)
def build_header(h):
    hp = h.paragraphs[0]
    ht = h.add_table(rows=1, cols=2, width=TEXT_W)
    table_borders(ht, "nil")
    ht.autofit = False
    c0, c1 = ht.cell(0, 0), ht.cell(0, 1)
    c0.width, c1.width = int(TEXT_W * 0.78), int(TEXT_W * 0.22)
    c0.vertical_alignment = c1.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    set_cell_borders(c0, bottom="single")
    set_cell_borders(c1, bottom="single")
    p = c0.paragraphs[0]
    pfmt(p, before=0, after=2, line=1.0)
    set_font(p.add_run(TITLE), 10)
    p = c1.paragraphs[0]
    pfmt(p, align=WD_ALIGN_PARAGRAPH.RIGHT, before=0, after=2, line=1.0)
    p.add_run().add_picture(LOGO, width=Inches(0.9))
    hp._p.getparent().remove(hp._p)
    ep = h.add_paragraph()
    pfmt(ep, before=0, after=0, line=1.0)
    set_font(ep.add_run(""), 4)


def build_footer(f):
    fp = f.paragraphs[0]
    pfmt(fp, before=0, after=0, line=1.0)
    pPr = fp._p.get_or_add_pPr()
    pb = OxmlElement("w:pBdr")
    top = OxmlElement("w:top")
    for k, v in (("w:val", "single"), ("w:sz", "6"), ("w:space", "6"), ("w:color", "000000")):
        top.set(qn(k), v)
    pb.append(top)
    pPr.append(pb)
    ts = fp.paragraph_format.tab_stops
    ts.add_tab_stop(int(TEXT_W / 2), WD_TAB_ALIGNMENT.CENTER)
    ts.add_tab_stop(TEXT_W, WD_TAB_ALIGNMENT.RIGHT)
    set_font(fp.add_run("Dept. of CSE\tAugust - November, 2026\tPage No."), 10)
    field(fp, "PAGE", size=10)


# front matter sections (Cover/Certificate and Declaration..LOT): empty header/footer
for s in doc.sections[:2]:
    s.different_first_page_header_footer = False
    for hp in (s.header, s.footer):
        hp.is_linked_to_previous = False

# Chapter 1 section: page numbering restarts at 1; no header on page 1 (starts on page 2); footer on all pages
ch1_sec = doc.sections[2]
ch1_sec.different_first_page_header_footer = True
ch1_sec.header.is_linked_to_previous = False
ch1_sec.first_page_header.is_linked_to_previous = False
ch1_sec.footer.is_linked_to_previous = False
ch1_sec.first_page_footer.is_linked_to_previous = False

pg = ch1_sec._sectPr.find(qn("w:pgNumType"))
if pg is None:
    pg = OxmlElement("w:pgNumType")
    ch1_sec._sectPr.append(pg)
pg.set(qn("w:start"), "1")
pg.set(qn("w:fmt"), "decimal")

build_header(ch1_sec.header)
build_footer(ch1_sec.footer)
build_footer(ch1_sec.first_page_footer)

# Chapters 2-9: no header on each chapter's opening page; header on pages 2+; footer on all pages
for s in doc.sections[3:-1]:
    s.different_first_page_header_footer = True
    s.header.is_linked_to_previous = True
    s.first_page_header.is_linked_to_previous = True
    s.footer.is_linked_to_previous = True
    s.first_page_footer.is_linked_to_previous = True
    old_pg = s._sectPr.find(qn("w:pgNumType"))
    if old_pg is not None:
        s._sectPr.remove(old_pg)

# REFERENCES through Appendix D: no header on any page (unless --all-headers); continuous footer
ref_sec = doc.sections[-1]
ref_sec.different_first_page_header_footer = False
ref_sec.header.is_linked_to_previous = ALL_HEADERS
ref_sec.footer.is_linked_to_previous = True
old_pg = ref_sec._sectPr.find(qn("w:pgNumType"))
if old_pg is not None:
    ref_sec._sectPr.remove(old_pg)

doc.core_properties.title = "PlantIQ Capstone Report"
doc.core_properties.author = "Team 35"
doc.save(OUT)
print("saved", OUT, "| toc", len(toc), "figs", len(lof), "tables", len(lot), "algs", len(loa))
