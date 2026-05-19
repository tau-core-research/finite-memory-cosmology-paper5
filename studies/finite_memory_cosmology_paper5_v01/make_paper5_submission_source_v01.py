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


def is_markdown_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def markdown_table_to_tex(table_lines: list[str]) -> list[str]:
    rows = []
    for line in table_lines:
        if is_markdown_table_separator(line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(cells)

    if not rows:
        return []

    col_count = max(len(row) for row in rows)
    normalized = [row + [""] * (col_count - len(row)) for row in rows]
    spec = "l" * col_count
    tex_rows = []
    for row_index, row in enumerate(normalized):
        rendered = " & ".join(inline_to_tex(cell) for cell in row)
        tex_rows.append(rendered + r" \\")
        if row_index == 0:
            tex_rows.append(r"\hline")

    return [
        r"\begin{center}",
        r"\begingroup",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{1.15}",
        r"\resizebox{\textwidth}{!}{%",
        rf"\begin{{tabular}}{{{spec}}}",
        r"\hline",
        *tex_rows,
        r"\hline",
        r"\end{tabular}%",
        r"}",
        r"\endgroup",
        r"\end{center}",
    ]


def markdown_to_tex(markdown: str) -> str:
    lines = []
    in_code = False
    in_math = False
    source_lines = markdown.splitlines()
    idx = 0
    while idx < len(source_lines):
        raw = source_lines[idx]
        line = raw.rstrip()
        if line.strip() == "Working manuscript draft. Current claim level: theory-method diagnostic.":
            idx += 1
            continue
        if line.strip() == "$$":
            if in_math:
                lines.append(r"\]")
                in_math = False
            else:
                lines.append(r"\[")
                in_math = True
            idx += 1
            continue
        if in_math:
            lines.append(line)
            idx += 1
            continue
        if line.startswith("```"):
            if in_code:
                lines.append(r"\end{verbatim}")
                in_code = False
            else:
                lines.append(r"\begin{verbatim}")
                in_code = True
            idx += 1
            continue
        if in_code:
            lines.append(line)
            idx += 1
            continue
        image_match = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", line.strip())
        if image_match:
            caption = inline_to_tex(image_match.group(1).strip())
            image_path = image_match.group(2).strip()
            lines.extend(
                [
                    r"\begin{figure}[htbp]",
                    r"\centering",
                    rf"\includegraphics[width=0.95\textwidth]{{{image_path}}}",
                    rf"\caption{{{caption}}}",
                    r"\end{figure}",
                ]
            )
            idx += 1
            continue
        if line.strip().startswith("|"):
            table_lines = []
            while idx < len(source_lines) and source_lines[idx].strip().startswith("|"):
                table_lines.append(source_lines[idx].rstrip())
                idx += 1
            lines.extend(markdown_table_to_tex(table_lines))
            continue
        if line.startswith("- "):
            lines.append(r"\begin{itemize}")
            while idx < len(source_lines) and source_lines[idx].startswith("- "):
                item = source_lines[idx][2:].strip()
                idx += 1
                while idx < len(source_lines) and source_lines[idx].startswith("  "):
                    item += " " + source_lines[idx].strip()
                    idx += 1
                lines.append(r"\item " + inline_to_tex(item))
            lines.append(r"\end{itemize}")
            continue
        if not line:
            lines.append("")
            idx += 1
            continue
        if line.startswith("# "):
            idx += 1
            continue
        elif line.startswith("## "):
            lines.append(r"\Needspace{10\baselineskip}")
            lines.append(r"\subsection*{" + inline_to_tex(line[3:].strip()) + "}")
        elif line.startswith("### "):
            lines.append(r"\Needspace{16\baselineskip}")
            lines.append(r"\subsubsection*{" + inline_to_tex(line[4:].strip()) + "}")
        else:
            lines.append(inline_to_tex(line))
        idx += 1
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
\usepackage{{graphicx}}
\usepackage{{needspace}}
\title{{Finite-memory projection corrections as a diagnostic gate for cosmological consistency tests}}
\author{{Jozsef Olcsak}}
\date{{2026-05-19}}
\begin{{document}}
\maketitle

{body}

\end{{document}}
"""
    SUBMISSION.mkdir(parents=True, exist_ok=True)
    (SUBMISSION / "main.tex").write_text(tex, encoding="utf-8")
    shutil.copy2(ROOT / "draft.md", SUBMISSION / "draft.md")
    submission_figures = SUBMISSION / "figures"
    if submission_figures.exists():
        shutil.rmtree(submission_figures)
    figures = ROOT / "figures"
    if figures.exists():
        submission_figures.mkdir(parents=True, exist_ok=True)
        for path in figures.glob("*.pdf"):
            shutil.copy2(path, submission_figures / path.name)


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
        for path in sorted((SUBMISSION / "figures").glob("*.pdf")):
            zf.write(path, path.relative_to(ROOT))
        for rel in [
            "evidence/finite_memory_preflight_summary.csv",
            "evidence/registered_protocol_guided_dominance_summary.csv",
            "evidence/source_native_reproduction_family_dominance_summary.csv",
            "evidence/gate_results_current.csv",
            "evidence/threshold_sensitivity.csv",
            "evidence/threshold_kernel_outcomes.csv",
            "evidence/diagnostic_point_audit.csv",
            "evidence/result_summary.csv",
            "wolfram/README.md",
            "wolfram/FiniteMemory_Diagnostic_Check.wl",
            "studies/finite_memory_cosmology_paper5_v01/wolfram_audit_logs/finite_memory_diagnostic_check_wolfram.csv",
            "studies/finite_memory_cosmology_paper5_v01/wolfram_audit_logs/finite_memory_diagnostic_check_wolfram.log",
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
