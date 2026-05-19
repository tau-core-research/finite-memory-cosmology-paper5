#!/usr/bin/env python3
"""Render the finite-memory cosmology draft to a simple PDF."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "draft.md"
PDF = ROOT / "finite_memory_projection_corrections.pdf"


def xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline_markup(text: str) -> str:
    text = xml_escape(text)
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\$([^$]+)\$", r"<font name='Times-Italic'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=23,
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "Heading2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12.5,
            leftIndent=14,
            firstLineIndent=-8,
            spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8.4,
            leading=11,
            backColor=colors.HexColor("#f4f4f4"),
            borderColor=colors.HexColor("#dddddd"),
            borderWidth=0.4,
            borderPadding=5,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "equation": ParagraphStyle(
            "Equation",
            parent=base["BodyText"],
            fontName="Times-Italic",
            fontSize=10.5,
            leading=14,
            alignment=1,
            backColor=colors.HexColor("#fafafa"),
            borderColor=colors.HexColor("#e0e0e0"),
            borderWidth=0.3,
            borderPadding=5,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.5,
            leading=7.8,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=6.2,
            leading=7.4,
        ),
    }


def parse_table(lines: list[str], idx: int, style_map: dict[str, ParagraphStyle]) -> tuple[Table, int]:
    rows = []
    while idx < len(lines) and lines[idx].strip().startswith("|"):
        line = lines[idx].strip()
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            row_style = style_map["table_header"] if not rows else style_map["table_cell"]
            rows.append([Paragraph(inline_markup(cell), row_style) for cell in cells])
        idx += 1
    col_width = (7.1 * inch) / max(len(rows[0]), 1)
    table = Table(rows, repeatRows=1, hAlign="LEFT", colWidths=[col_width] * len(rows[0]))
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table, idx


def render() -> None:
    s = styles()
    story = []
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    idx = 0
    in_code = False
    in_equation = False
    code_lines: list[str] = []
    equation_lines: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph)), s["body"]))
            paragraph.clear()

    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()
        if stripped == "$$":
            if in_equation:
                equation = "<br/>".join(inline_markup(item) for item in equation_lines)
                story.append(Paragraph(equation, s["equation"]))
                equation_lines = []
                in_equation = False
            else:
                flush_paragraph()
                in_equation = True
            idx += 1
            continue
        if in_equation:
            equation_lines.append(line)
            idx += 1
            continue
        if stripped.startswith("```"):
            if in_code:
                story.append(Preformatted("\n".join(code_lines), s["code"]))
                code_lines = []
                in_code = False
            else:
                flush_paragraph()
                in_code = True
            idx += 1
            continue
        if in_code:
            code_lines.append(line)
            idx += 1
            continue
        if not stripped:
            flush_paragraph()
            idx += 1
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), s["title"]))
            idx += 1
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[3:]), s["h2"]))
            idx += 1
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            story.append(Paragraph("• " + inline_markup(stripped[2:]), s["bullet"]))
            idx += 1
            continue
        if stripped.startswith("|"):
            flush_paragraph()
            table, idx = parse_table(lines, idx, s)
            story.append(table)
            story.append(Spacer(1, 8))
            continue
        paragraph.append(stripped)
        idx += 1

    flush_paragraph()
    doc = SimpleDocTemplate(
        str(PDF),
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Finite-Memory Projection Corrections In Cosmological Consistency Diagnostics",
    )
    doc.build(story)
    print(PDF)


if __name__ == "__main__":
    render()
