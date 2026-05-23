#!/usr/bin/env python3
"""Validate the P-TauCov delta_C_Tau source schema readiness state."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_delta_c_tau_source_schema.md"
CSV = ROOT / "evidence/p_taucov_delta_c_tau_source_schema.csv"
SUMMARY = ROOT / "evidence/p_taucov_delta_c_tau_source_readiness.csv"
OUT = ROOT / "evidence/p_taucov_delta_c_tau_source_schema_validation.csv"

REQUIRED_OBJECTS = {
    "PhiPerturbationFamily",
    "BranchEquationFB",
    "ReducedBranchOperatorLBred",
    "BranchDomainPolicy",
    "BranchResponseRule",
    "ParentMorphologyMap",
    "ProjectionMorphologyMap",
    "ProjectedMorphologyDerivativePhi",
    "ProjectedMorphologyDerivativeB",
    "CovarianceFunctionalDerivative",
    "ObservableCoordinateIndex",
    "NormalizationPolicy",
    "LeakageExclusionAudit",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_DELTA_C_TAU_SOURCE_SCHEMA_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("source_schema_exists", CSV.exists())
    add("readiness_summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_DELTA_C_TAU_SOURCE_SCHEMA_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)
    add("required_objects_present", REQUIRED_OBJECTS.issubset(set(df["SourceObject"])))
    add("all_required_for_delta_c_tau", df["RequiredForDeltaCTau"].astype(bool).all())
    add("no_scoring_authorized", (df["ScoringAuthorized"].astype(str).str.lower() == "false").all())
    add(
        "generation_blocked_until_inputs_exist",
        summary["DeltaCTauGenerationStatus"].iloc[0] == "BLOCKED_PENDING_CONCRETE_TAU_RESPONSE_INPUTS",
    )
    add("branch_support_not_authorized", not bool(summary["BranchSupportFreezeAuthorized"].iloc[0]))
    add("p_taucov_scoring_not_authorized", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))
    add("v4_not_authorized", not bool(summary["V4KernelAuthorized"].iloc[0]))
    for phrase in [
        "does not fabricate a response matrix",
        "BLOCKED_PENDING_CONCRETE_TAU_RESPONSE_INPUTS",
        "F_B, L_B^red, branch-domain policy",
        "leakage exclusion audit",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_DELTA_C_TAU_SOURCE_SCHEMA_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_DELTA_C_TAU_SOURCE_SCHEMA_VALID_BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
