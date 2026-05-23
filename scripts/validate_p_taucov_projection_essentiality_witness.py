#!/usr/bin/env python3
"""Validate the P-TauCov projection-essentiality witness."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OBJECT = ROOT / "evidence/p_taucov_projection_essentiality_witness.csv"
GATES = ROOT / "evidence/p_taucov_projection_essentiality_witness_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_projection_essentiality_witness_summary.csv"
DOC = ROOT / "docs/p_taucov_projection_essentiality_witness.md"
OUT = ROOT / "evidence/p_taucov_projection_essentiality_witness_validation.csv"

AUDIT_ID = "P_TAUCOV_PROJECTION_ESSENTIALITY_WITNESS_VALIDATION"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append(
            {
                "AuditID": AUDIT_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [OBJECT, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if OBJECT.exists() and GATES.exists() and SUMMARY.exists() and DOC.exists():
        obj = pd.read_csv(OBJECT)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_pass_no_scoring", str(summary["Status"]).endswith("PASS_NO_SCORING"))
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("projection_essentiality_high", float(summary["ProjectionEssentiality"]) > 0.40)
        add("projection_null_low", float(summary["ProjectionNullAbsCorrelation"]) < 0.60)
        add("morphology_null_low", float(summary["MorphologyNullAbsCorrelation"]) < 0.75)
        add("shuffled_support_low", float(summary["ShuffledSupportAbsCorrelation"]) < 0.60)
        add("no_family_clock_dominance", max(float(summary["MaxFamilyEnergyShare"]), float(summary["MaxClockEnergyShare"])) <= 0.60)
        add("uses_no_target_residuals", not bool(obj["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(obj["UsesScoreOutcome"].any()))
        add("scoring_not_authorized", not bool(obj["ScoringAuthorized"].any()) and bool(summary["ScoringAuthorized"]) is False)
        add("doc_contains_structural_witness_only", "structural witness only" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PROJECTION_ESSENTIALITY_WITNESS_VALID" if ok else "P_TAUCOV_PROJECTION_ESSENTIALITY_WITNESS_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
