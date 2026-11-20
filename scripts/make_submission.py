"""Build a flat LaTeX submission package for Elsevier Editorial Manager.

Editorial Manager stores uploaded files in one folder, so the manuscript must
not refer to subfolders. This script copies the manuscript, the generated
macros, every table and every figure into paper/submission/, rewrites the
\\input and \\includegraphics paths, compiles the copy three times in that folder and
writes paper/submission.zip.

Usage: python scripts/make_submission.py
"""
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
OUT = PAPER / "submission"
MAIN = "paper1_cor.tex"
# Template files of cas-sc 2.4 (also in TeX Live as els-cas-templates).
TEMPLATE = ["cas-sc.cls", "cas-common.sty", "cas-model2-names.bst"]


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    tex = (PAPER / MAIN).read_text()

    tables = re.findall(r"\\input\{tables/([^}]+)\}", tex)
    for t in tables:
        shutil.copy(PAPER / "tables" / t, OUT / t)
    tex = re.sub(r"\\input\{tables/([^}]+)\}", r"\\input{\1}", tex)

    figs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{\.\./results/figures/([^}]+)\}", tex)
    for f in figs:
        shutil.copy(ROOT / "results" / "figures" / f, OUT / f)
    tex = tex.replace("{../results/figures/", "{")

    assert "tables/" not in tex and "../" not in tex, "a subfolder path is left"
    (OUT / MAIN).write_text(tex)
    shutil.copy(PAPER / "generated_macros.tex", OUT / "generated_macros.tex")
    for f in TEMPLATE:
        shutil.copy(PAPER / f, OUT / f)
    for f in ["highlights.docx", "highlights.pdf"]:
        shutil.copy(PAPER / f, OUT / f)

    for _ in range(3):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", MAIN],
                           cwd=OUT, capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("submission copy does not compile:\n" + r.stdout[-3000:])
    log = (OUT / MAIN.replace(".tex", ".log")).read_text(errors="replace")
    for bad in ["undefined", "Rerun to get", "same identifier"]:
        if bad in log:
            raise SystemExit(f"log of the submission copy contains '{bad}'")

    for ext in [".aux", ".log", ".out", ".abs"]:
        p = OUT / MAIN.replace(".tex", ext)
        if p.exists():
            p.unlink()
    with zipfile.ZipFile(PAPER / "submission.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.iterdir()):
            z.write(p, p.name)
    print(f"{len(tables)} tables, {len(figs)} figures -> {OUT} and paper/submission.zip")


if __name__ == "__main__":
    main()
