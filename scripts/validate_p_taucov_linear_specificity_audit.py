#!/usr/bin/env python3
"""Validate the P-TauCov linear specificity audit definition."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_linear_specificity_audit.md"
CSV = ROOT / "evidence/p_taucov_linear_specificity_audit.csv"
SUMMARY = ROOT / "evidence/p_taucov_linear_specificity_audit_summary.csv"
MODEL_DOC = ROOT / "docs/p_taucov_minimal_tau_response_model_spec.md"
OUT = ROOT / "evidence/p_taucov_linear_specificity_audit_validation.csv"

REQUIRED_GATES = {
    "TARGET_BLIND_INPUTS_ONLY",
    "NOT_GENERIC_LOW_RANK",
    "BRANCH_PROJECTION_NONCOMMUTATIVITY",
    "SUPPORT_NOT_FAMILY_LABEL_PROXY",
    "BEATS_GENERIC_LINEAR_NULLS_PRESCORE",
    "NO_SCORING_AUTHORIZATION",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_LINEAR_SPECIFICITY_AUDIT_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("audit_csv_exists", CSV.exists())
    add("summary_exists", SUMMARY.exists())
    add("model_doc_exists", MODEL_DOC.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY, MODEL_DOC]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_LINEAR_SPECIFICITY_AUDIT_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    model_text = MODEL_DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_gates_present", REQUIRED_GATES.issubset(set(df["GateName"])))
    add("all_required_before_linear_freeze", df["RequiredBeforeLinearFreeze"].astype(bool).all())
    add("no_scoring_authorized", (df["ScoringAuthorized"].astype(str).str.lower() == "false").all())
    add("linear_candidate_not_frozen", not bool(summary["LinearCandidateFrozen"].iloc[0]))
    add("delta_c_tau_not_generated", not bool(summary["DeltaCTauGenerated"].iloc[0]))
    add("p_taucov_scoring_not_authorized", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))
    add("model_doc_references_audit", "P_TAUCOV_LINEAR_SPECIFICITY_AUDIT" in model_text)
    for phrase in [
        "must not be frozen automatically",
        "lambda_B = 0",
        "epsilon_P = 0",
        "BRANCH_PROJECTION_NONCOMMUTATIVITY",
        "lambda_B fixed nonzero",
        "epsilon_P fixed nonzero",
        "already a Tau-specific covariance model",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_SPECIFICITY_AUDIT_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_LINEAR_SPECIFICITY_AUDIT_VALID_NOT_FROZEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
