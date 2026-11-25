"""Iteratively keeps sections on one page: build -> measure in Word -> mark every split section that fits on a page
-> rebuild, until no fixable split is left (later sections move down as earlier ones are fixed).
Usage: python fit_sections.py v3|old"""
import subprocess
import sys

VARIANT = sys.argv[1]
NAME = "Team_35_report_v3" if VARIANT == "v3" else "Team_35_report_patched"
TOP, BOTTOM, LINE = 90.0, 842.0 - 75.6, 18.0   # body text area on A4 (points)
USABLE = BOTTOM - TOP
KEEPFILE = f"keep_{VARIANT}.txt"


def measure():
    out = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "measure_sections.ps1",
                          "-Docx", fr"D:\plantiq-capstone\report\{NAME}.docx"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    rows = []
    for ln in out.splitlines():
        f = ln.split("\t")
        if len(f) >= 6 and f[0].isdigit():
            rows.append((int(f[0]), int(f[1]), int(f[2]), float(f[3]), float(f[4]), f[5]))
    return rows


def height(sp, ep, sy, ey):
    if sp == ep:
        return ey + LINE - sy
    return (BOTTOM - sy) + (ep - sp - 1) * USABLE + (ey + LINE - TOP)


keep = set()
open(KEEPFILE, "w").write("")
for it in range(12):
    subprocess.run([sys.executable, "build_report.py", VARIANT], check=True, capture_output=True)
    rows = measure()
    split = [r for r in rows if r[1] != r[2]]
    fixable = [r for r in split if height(r[1], r[2], r[3], r[4]) <= USABLE - 6 and r[0] not in keep]
    print(f"pass {it + 1}: {len(rows)} sections, {len(split)} split, {len(fixable)} newly fixable")
    if not fixable:
        break
    keep |= {r[0] for r in fixable}
    open(KEEPFILE, "w").write("\n".join(map(str, sorted(keep))))

print("kept together:", len(keep))
print("still split (longer than one page):")
for r in rows:
    if r[1] != r[2]:
        print(f"  {r[5]}  pages {r[1]}-{r[2]}, height {height(r[1], r[2], r[3], r[4]):.0f} pt")
