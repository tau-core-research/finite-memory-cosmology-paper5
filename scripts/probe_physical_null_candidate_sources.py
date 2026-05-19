#!/usr/bin/env python3
"""Probe arXiv source packages for first physical-null acquisition targets.

This script downloads public arXiv e-print source packages and records only
source-structure metadata. It does not promote extracted values to benchmark
inputs and does not create measurement-validation artifacts.
"""

from __future__ import annotations

import gzip
import io
import tarfile
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "physical_nulls" / "raw"
EVIDENCE = ROOT / "evidence"

OUT = EVIDENCE / "physical_null_candidate_source_probe.csv"
OUT_SUMMARY = EVIDENCE / "physical_null_candidate_source_probe_summary.csv"

TARGETS = [
    {
        "CandidateID": "PNC_BACKREACTION_KOKSBANG_2604_11249",
        "ArxivID": "2604.11249",
        "NullID": "BACKREACTION_ONLY",
        "Priority": 1,
    },
    {
        "CandidateID": "PNC_DYER_ROEDER_SNE_GRB_1303_1574",
        "ArxivID": "1303.1574",
        "NullID": "DYER_ROEDER_OPTICAL",
        "Priority": 2,
    },
    {
        "CandidateID": "PNC_DYER_ROEDER_SMOOTHNESS_DD_1305_6989",
        "ArxivID": "1305.6989",
        "NullID": "DYER_ROEDER_OPTICAL",
        "Priority": 3,
    },
]


def fetch(arxiv_id: str) -> bytes:
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "finite-memory-cosmology-source-probe/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def safe_text(data: bytes) -> str:
    for payload in (data, gzip.decompress(data) if data.startswith(b"\x1f\x8b") else b""):
        if not payload:
            continue
        try:
            return payload.decode("utf-8", errors="ignore")
        except Exception:
            pass
    return ""


def inspect_source(data: bytes, target_dir: Path) -> dict[str, object]:
    target_dir.mkdir(parents=True, exist_ok=True)
    source_path = target_dir / "source_package.bin"
    source_path.write_bytes(data)

    names: list[str] = []
    tex_texts: list[str] = []
    package_type = "unknown"
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            package_type = "tar"
            for member in archive.getmembers():
                names.append(member.name)
                suffix = Path(member.name).suffix.lower()
                if suffix in {".tex", ".bbl", ".sty"} and member.isfile():
                    extracted = archive.extractfile(member)
                    if extracted is not None:
                        tex_texts.append(extracted.read().decode("utf-8", errors="ignore"))
    except tarfile.TarError:
        text = safe_text(data)
        if text:
            package_type = "single_text_or_gzip"
            names = ["source.tex"]
            tex_texts = [text]
        elif data.startswith(b"%PDF"):
            package_type = "pdf_only"
            names = ["source.pdf"]

    lower_names = [name.lower() for name in names]
    combined_text = "\n".join(tex_texts).lower()
    figure_files = [name for name in names if Path(name).suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".eps"}]
    data_files = [
        name
        for name in names
        if Path(name).suffix.lower() in {".csv", ".dat", ".txt", ".tsv", ".json", ".yaml", ".yml"}
    ]
    table_markers = combined_text.count("\\begin{tabular}") + combined_text.count("\\begin{array}")
    includegraphics_markers = combined_text.count("\\includegraphics")
    keyword_hits = {
        "backreaction": combined_text.count("backreaction"),
        "dyer_roeder": combined_text.count("dyer") + combined_text.count("roeder"),
        "alpha": combined_text.count("alpha"),
        "constraint": combined_text.count("constraint"),
    }

    return {
        "PackageType": package_type,
        "FileCount": len(names),
        "TexLikeFileCount": len(tex_texts),
        "FigureFileCount": len(figure_files),
        "DataLikeFileCount": len(data_files),
        "TableMarkers": table_markers,
        "IncludeGraphicsMarkers": includegraphics_markers,
        "HasDataLikeFiles": bool(data_files),
        "HasTexTables": table_markers > 0,
        "HasFigures": bool(figure_files) or includegraphics_markers > 0,
        "BackreactionKeywordHits": keyword_hits["backreaction"],
        "DyerRoederKeywordHits": keyword_hits["dyer_roeder"],
        "AlphaKeywordHits": keyword_hits["alpha"],
        "ConstraintKeywordHits": keyword_hits["constraint"],
        "StoredSourcePath": str(source_path.relative_to(ROOT)),
        "ExampleFiles": ";".join(names[:8]),
        "PotentialExtractionRoute": (
            "source_data_file"
            if data_files
            else "tex_table"
            if table_markers > 0
            else "figure_digitization_or_formula_extraction"
            if figure_files or includegraphics_markers > 0
            else "manual_paper_inspection_required"
        ),
    }


def main() -> None:
    rows = []
    for target in TARGETS:
        arxiv_id = target["ArxivID"]
        target_dir = RAW / f"arxiv_{arxiv_id.replace('.', '_')}"
        try:
            payload = fetch(arxiv_id)
            inspection = inspect_source(payload, target_dir)
            status = "source_probe_completed"
            blocking = "candidate_values_not_extracted_or_mapped"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            inspection = {
                "PackageType": "unavailable",
                "FileCount": 0,
                "TexLikeFileCount": 0,
                "FigureFileCount": 0,
                "DataLikeFileCount": 0,
                "TableMarkers": 0,
                "IncludeGraphicsMarkers": 0,
                "HasDataLikeFiles": False,
                "HasTexTables": False,
                "HasFigures": False,
                "BackreactionKeywordHits": 0,
                "DyerRoederKeywordHits": 0,
                "AlphaKeywordHits": 0,
                "ConstraintKeywordHits": 0,
                "StoredSourcePath": "",
                "ExampleFiles": "",
                "PotentialExtractionRoute": "download_failed",
            }
            status = "source_probe_failed"
            blocking = f"download_failed:{type(exc).__name__}"

        rows.append(
            {
                "CandidateID": target["CandidateID"],
                "ArxivID": arxiv_id,
                "NullID": target["NullID"],
                "Priority": target["Priority"],
                **inspection,
                "Status": status,
                "CanUseAsCalibrationInputNow": False,
                "BlockingIssue": blocking,
                "NextAction": "extract candidate values into provisional source CSV, then run mapping and covariance readiness checks",
                "ClaimBoundary": "physical_null_source_probe_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "PHYSICAL_NULL_CANDIDATE_SOURCE_PROBE_SUMMARY",
                "TargetsProbed": len(output),
                "ProbeCompleted": int(output["Status"].eq("source_probe_completed").sum()),
                "SourcesWithDataLikeFiles": int(output["HasDataLikeFiles"].sum()),
                "SourcesWithTexTables": int(output["HasTexTables"].sum()),
                "SourcesWithFigures": int(output["HasFigures"].sum()),
                "CalibrationInputsReadyNow": 0,
                "RecommendedNextAction": "begin provisional extraction from highest-priority completed source probe",
                "PrimaryBlockingIssue": "candidate_values_not_extracted_or_mapped",
                "Interpretation": "source packages are probed for extractability, but no calibration values are ingested yet",
                "ClaimBoundary": "physical_null_source_probe_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
