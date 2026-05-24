#!/usr/bin/env python3
"""Validate the no-score parent-Hessian residue candidate preflight packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OBJECT = ROOT / "evidence/p_taucov_parent_hessian_residue_candidate.csv"
METRICS = ROOT / "evidence/p_taucov_parent_hessian_residue_candidate_metrics.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_hessian_residue_candidate_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_hessian_residue_candidate.md"
OUT = ROOT / "evidence/p_taucov_parent_hessian_residue_candidate_validation.csv"

AUDIT_ID = "P_TAUCOV_PARENT_HESSIAN_RESIDUE_CANDIDATE_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_PARENT_HESSIAN_RESIDUE_CANDIDATE_PREFLIGHT_FAIL_NO_SCORING"


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

    for path in [OBJECT, METRICS, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [OBJECT, METRICS, SUMMARY, DOC]):
        obj = pd.read_csv(OBJECT)
        metrics = pd.read_csv(METRICS)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        failed = metrics.loc[~metrics["Passed"].astype(bool), "GateID"].astype(str).tolist()
        add("status_expected_fail_no_scoring", str(summary["Status"]) == EXPECTED_STATUS)
        add("object_nonempty", len(obj) > 0)
        add("gates_count_matches_summary", int(summary["GatesTotal"]) == len(metrics) == 7)
        add("gates_passed_matches_summary", int(summary["GatesPassed"]) == int(metrics["Passed"].sum()))
        add("only_norm_gate_failed", failed == ["PHR-G1_PARENT_HESSIAN_RESIDUE_DECLARED"])
        add("norm_below_floor", float(summary["CandidateNormBeforeNormalization"]) < 1e-10)
        add("smooth_overlap_low", float(summary["SmoothPSDProjectionOverlap"]) <= 0.50)
        add("projection_overlap_low", float(summary["ProjectionNullAbsCorrelation"]) < 0.60)
        add("scoring_false", bool(summary["ScoringAuthorized"]) is False)
        add("survival_false", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_false", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("doc_forbids_empirical_claim", "does not run an empirical scorecard" in doc and "rescues a failed scorecard" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_HESSIAN_RESIDUE_CANDIDATE_VALID" if ok else "P_TAUCOV_PARENT_HESSIAN_RESIDUE_CANDIDATE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
