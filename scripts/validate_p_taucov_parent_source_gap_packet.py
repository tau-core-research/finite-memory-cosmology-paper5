#!/usr/bin/env python3
"""Validate the P-TauCov parent-source gap packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_parent_source_gap_packet.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_source_gap_packet_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_source_gap_packet.md"
OUT = ROOT / "evidence/p_taucov_parent_source_gap_packet_validation.csv"

AUDIT_ID = "P_TAUCOV_PARENT_SOURCE_GAP_PACKET_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_PARENT_SOURCE_GAP_IDENTIFIED_NO_SCORING"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append(
            {
                "AuditID": AUDIT_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": True,
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [TABLE, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        table = pd.read_csv(TABLE)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        gaps = set(table["GapID"].astype(str))
        required = {
            "SG1_NO_NONZERO_RESIDUE_AFTER_CLEANING",
            "SG2_SMOOTH_PSD_COMPETITOR_STRONGER",
            "SG3_PROJECTION_NULL_LEAKAGE_IN_COMMUTATOR_ROUTE",
            "SG4_MISSING_MICROSCOPIC_SOURCE_SELECTOR",
        }
        add("status_expected", str(summary["Status"]) == EXPECTED_STATUS)
        add("all_required_gaps_present", required.issubset(gaps))
        add("gap_count_matches", int(summary["GapCount"]) == len(table) == 4)
        add("records_residue_collapse", float(summary["ResidueNormBeforeNormalization"]) < 1e-10)
        add("records_smooth_psd_loss", float(summary["ExpandedPrimaryMinusStrongestNull"]) < 0.0)
        add("records_projection_leakage", float(summary["CommutatorProjectionNullAbsCorrelation"]) > 0.60)
        add("next_artifact_declared", str(summary["NextAllowedArtifact"]) == "p_taucov_microscopic_residue_source_spec_v1_no_score")
        add("scoring_false", bool(summary["ScoringAuthorized"]) is False)
        add("survival_false", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_false", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("doc_forbids_new_kernel", "Forbidden: building another empirical covariance kernel" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_SOURCE_GAP_PACKET_VALID" if ok else "P_TAUCOV_PARENT_SOURCE_GAP_PACKET_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
