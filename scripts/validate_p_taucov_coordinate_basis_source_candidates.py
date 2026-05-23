#!/usr/bin/env python3
"""Validate the P-TauCov coordinate-basis source-candidate audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_coordinate_basis_source_candidates.md"
CSV = ROOT / "evidence/p_taucov_coordinate_basis_source_candidates.csv"
SUMMARY = ROOT / "evidence/p_taucov_coordinate_basis_source_candidates_summary.csv"
OUT = ROOT / "evidence/p_taucov_coordinate_basis_source_candidates_validation.csv"

REQUIRED_SOURCES = {
    "TauSideSymbolicDefinition",
    "CoordinateConventionOnly",
    "PublishedExternalMetadata",
    "ExistingP5CKernelV3Gains",
    "HeldOutResidualsOrTargets",
    "PostHocFamilyLocalization",
    "GenericSmoothNullTemplates",
}

FORBIDDEN_SOURCES = {
    "ExistingP5CKernelV3Gains",
    "HeldOutResidualsOrTargets",
    "PostHocFamilyLocalization",
    "GenericSmoothNullTemplates",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_COORDINATE_BASIS_SOURCE_CANDIDATES_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("csv_exists", CSV.exists())
    add("summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_COORDINATE_BASIS_SOURCE_CANDIDATES_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_sources_present", REQUIRED_SOURCES.issubset(set(df["CandidateSource"])))
    allowed_map = dict(zip(df["CandidateSource"], df["AllowedForCandidateBasis"].astype(bool)))
    for source in FORBIDDEN_SOURCES:
        add(f"{source}_forbidden", allowed_map.get(source) is False)
    for source in REQUIRED_SOURCES - FORBIDDEN_SOURCES:
        add(f"{source}_allowed", allowed_map.get(source) is True)

    add("no_concrete_basis_rows", not df["ConcreteBasisRowsProvided"].astype(bool).any())
    add("basis_packet_not_authorized", not df["CoordinateBasisPacketAuthorized"].astype(bool).any())
    add("reference_domain_not_selectable", not df["ReferenceDomainSelectable"].astype(bool).any())
    add("metric_eval_not_authorized", not df["MetricEvaluationAuthorized"].astype(bool).any())
    add("scoring_not_authorized", not df["PTauCovScoringAuthorized"].astype(bool).any())
    add("summary_no_basis_packet", not bool(summary["CoordinateBasisPacketAuthorized"].iloc[0]))
    add("summary_no_scoring", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))

    for phrase in [
        "Allowed Source Classes",
        "Forbidden Source Classes",
        "Existing P5C v3 gains",
        "Held-out residuals or targets",
        "Generic smooth null templates",
        "finite-dimensional symbolic axis map",
        "A concrete coordinate-basis packet has been built or accepted",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_COORDINATE_BASIS_SOURCE_CANDIDATES_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_COORDINATE_BASIS_SOURCE_CANDIDATES_VALID_NO_PACKET")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
