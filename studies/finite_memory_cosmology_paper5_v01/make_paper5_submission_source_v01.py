#!/usr/bin/env python3
"""Build the Paper 5 submission-source packet.

The repository keeps the working manuscript in Markdown because the current
paper is a method-note packet. This generator creates a lightweight LaTeX
facsimile, refreshes the ReportLab PDF, and builds an arXiv-style source ZIP.
"""

from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SUBMISSION = ROOT / "paper5_submission_source"
ZIP_PATH = ROOT / "arxiv_submission_source.zip"


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def inline_to_tex(text: str) -> str:
    """Convert simple Markdown inline markup while preserving LaTeX math."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)

    pieces = re.split(r"(\$[^$]+\$)", text)
    converted = []
    for piece in pieces:
        if len(piece) >= 2 and piece.startswith("$") and piece.endswith("$"):
            converted.append(piece)
        else:
            converted.append(latex_escape(piece))
    return "".join(converted)


def markdown_to_tex(markdown: str) -> str:
    lines = []
    in_code = False
    in_math = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if line.strip() == "$$":
            if in_math:
                lines.append(r"\]")
                in_math = False
            else:
                lines.append(r"\[")
                in_math = True
            continue
        if in_math:
            lines.append(line)
            continue
        if line.startswith("```"):
            if in_code:
                lines.append(r"\end{verbatim}")
                in_code = False
            else:
                lines.append(r"\begin{verbatim}")
                in_code = True
            continue
        if in_code:
            lines.append(line)
            continue
        if not line:
            lines.append("")
            continue
        if line.startswith("# "):
            lines.append(r"\section*{" + inline_to_tex(line[2:].strip()) + "}")
        elif line.startswith("## "):
            lines.append(r"\subsection*{" + inline_to_tex(line[3:].strip()) + "}")
        elif line.startswith("### "):
            lines.append(r"\subsubsection*{" + inline_to_tex(line[4:].strip()) + "}")
        elif line.startswith("- "):
            lines.append(r"\noindent $\bullet$ " + inline_to_tex(line[2:].strip()) + r"\\")
        else:
            lines.append(inline_to_tex(line))
    if in_code:
        lines.append(r"\end{verbatim}")
    if in_math:
        lines.append(r"\]")
    return "\n".join(lines)


def build_main_tex() -> None:
    draft = (ROOT / "draft.md").read_text(encoding="utf-8")
    body = markdown_to_tex(draft)
    tex = rf"""\documentclass[11pt]{{article}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{hyperref}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\title{{Finite-memory projection corrections as a diagnostic gate for cosmological consistency tests}}
\author{{Jozsef Olcsak}}
\date{{2026-05-19}}
\begin{{document}}
\maketitle

\begin{{abstract}}
This is a cautious method-note packet. It defines a locked finite-memory
projection operator and a reproducible diagnostic gate for current cosmological
consistency packets. It does not claim a discovery, measurement validation, or
proof of a background theory.
\end{{abstract}}

{body}

\end{{document}}
"""
    SUBMISSION.mkdir(parents=True, exist_ok=True)
    (SUBMISSION / "main.tex").write_text(tex, encoding="utf-8")
    shutil.copy2(ROOT / "draft.md", SUBMISSION / "draft.md")


def refresh_pdf() -> None:
    tectonic = shutil.which("tectonic")
    if tectonic:
        subprocess.run(
            [tectonic, "main.tex"],
            cwd=SUBMISSION,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        shutil.copy2(SUBMISSION / "main.pdf", ROOT / "finite_memory_projection_corrections.pdf")
        return

    try:
        subprocess.run(
            [sys.executable, str(ROOT / "make_pdf.py")],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError:
        existing = ROOT / "finite_memory_projection_corrections.pdf"
        if not existing.exists():
            raise
    shutil.copy2(ROOT / "finite_memory_projection_corrections.pdf", SUBMISSION / "main.pdf")


def build_zip() -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in [
            SUBMISSION / "main.tex",
            SUBMISSION / "draft.md",
            SUBMISSION / "main.pdf",
            ROOT / "README.md",
            ROOT / "DATA_NOTICE.md",
            ROOT / "CITATION.cff",
        ]:
            zf.write(path, path.relative_to(ROOT))
        for rel in [
            "evidence/tau_core_a2_preflight_proof_packet_summary.csv",
            "evidence/author_protocol_guided_dominance_summary.csv",
            "evidence/source_native_reproduction_family_dominance_summary.csv",
            "evidence/gate_results_current.csv",
        ]:
            path = ROOT / rel
            if path.exists():
                zf.write(path, rel)


def main() -> None:
    build_main_tex()
    refresh_pdf()
    build_zip()
    print(f"Wrote {SUBMISSION / 'main.tex'}")
    print(f"Wrote {SUBMISSION / 'main.pdf'}")
    print(f"Wrote {ZIP_PATH}")


if __name__ == "__main__":
    main()
