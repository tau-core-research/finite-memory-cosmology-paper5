#!/usr/bin/env python3
"""Validate the P-TauCov minimal Tau-response model specification."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_minimal_tau_response_model_spec.md"
CSV = ROOT / "evidence/p_taucov_minimal_tau_response_model_spec.csv"
SUMMARY = ROOT / "evidence/p_taucov_minimal_tau_response_model_spec_summary.csv"
OUT = ROOT / "evidence/p_taucov_minimal_tau_response_model_spec_validation.csv"

REQUIRED_OBJECTS = {
    "BranchStateB",
    "BranchEquationFB",
    "ReducedBranchOperatorLBred",
    "BranchDomainPolicy",
    "ParentMorphologyMap",
    "ProjectionMorphologyMap",
    "TauMorphologyResponse",
    "CovarianceResponseMap",
    "NoOutcomeSelectionRule",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_MINIMAL_TAU_RESPONSE_MODEL_SPEC_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("spec_csv_exists", CSV.exists())
    add("summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_MINIMAL_TAU_RESPONSE_MODEL_SPEC_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_objects_present", REQUIRED_OBJECTS.issubset(set(df["Object"])))
    add("no_scoring_authorized", (df["ScoringAuthorized"].astype(str).str.lower() == "false").all())
    add("no_delta_c_tau_generated", not bool(summary["DeltaCTauGenerated"].iloc[0]))
    add("branch_support_not_authorized", not bool(summary["BranchSupportFreezeAuthorized"].iloc[0]))
    add("p_taucov_scoring_not_authorized", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))
    add(
        "next_step_freeze_or_reject",
        summary["NextStep"].iloc[0] == "freeze_concrete_matrices_or_reject_candidate_spec",
    )
    for phrase in [
        "F_B, L_B^red, M_parent, P_morph",
        "F_B(\\Phi,B)",
        "L_B^{\\rm red}",
        "M_{\\rm parent}(\\Phi,B)",
        "P_{\\rm morph}(\\Phi,B)",
        "This specification already produces a Tau-specific covariance signal",
        "no `delta_C_Tau`",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_MINIMAL_TAU_RESPONSE_MODEL_SPEC_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_MINIMAL_TAU_RESPONSE_MODEL_SPEC_VALID_NOT_FROZEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
