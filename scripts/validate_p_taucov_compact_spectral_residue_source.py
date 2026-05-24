#!/usr/bin/env python3
"""Validate the no-score compact spectral residue source preflight."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OBJECT = ROOT / "evidence/p_taucov_compact_spectral_residue_source.csv"
SPECTRUM = ROOT / "evidence/p_taucov_compact_spectral_residue_source_spectrum.csv"
METRICS = ROOT / "evidence/p_taucov_compact_spectral_residue_source_metrics.csv"
SUMMARY = ROOT / "evidence/p_taucov_compact_spectral_residue_source_summary.csv"
DOC = ROOT / "docs/p_taucov_compact_spectral_residue_source.md"
OUT = ROOT / "evidence/p_taucov_compact_spectral_residue_source_validation.csv"

AUDIT_ID = "P_TAUCOV_COMPACT_SPECTRAL_RESIDUE_SOURCE_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_COMPACT_SPECTRAL_RESIDUE_SOURCE_PREFLIGHT_PASS_NO_SCORING"


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

    for path in [OBJECT, SPECTRUM, METRICS, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [OBJECT, SPECTRUM, METRICS, SUMMARY, DOC]):
        obj = pd.read_csv(OBJECT)
        spectrum = pd.read_csv(SPECTRUM)
        metrics = pd.read_csv(METRICS)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_expected_pass_no_scoring", str(summary["Status"]) == EXPECTED_STATUS)
        add("object_nonempty", len(obj) > 0)
        add("spectrum_has_selected_modes", bool(spectrum["SelectedForResidue"].astype(bool).any()))
        add("selected_count_matches_summary", int(summary["SelectedEigenmodes"]) == int(spectrum["SelectedForResidue"].astype(bool).sum()))
        add("all_gates_pass", bool(metrics["Passed"].all()))
        add("gate_count_matches_summary", int(summary["GatesPassed"]) == int(summary["GatesTotal"]) == len(metrics))
        add("source_nonzero", float(summary["SourceNormBeforeNormalization"]) >= 1e-10)
        add("smooth_overlap_low", float(summary["SmoothPSDProjectionOverlap"]) <= 0.50)
        add("projection_overlap_low", float(summary["ProjectionNullAbsCorrelation"]) < 0.60)
        add("q_range_native", float(summary["QRangeMembershipError"]) <= 1e-10)
        add("balanced_support", max(float(summary["MaxFamilyShare"]), float(summary["MaxClockShare"]), float(summary["MaxContextShare"])) <= 0.60)
        add("scoring_false", bool(summary["ScoringAuthorized"]) is False)
        add("survival_false", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_false", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("doc_forbids_signal_claim", "Forbidden" in doc and "Tau Core signal" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_COMPACT_SPECTRAL_RESIDUE_SOURCE_VALID" if ok else "P_TAUCOV_COMPACT_SPECTRAL_RESIDUE_SOURCE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
