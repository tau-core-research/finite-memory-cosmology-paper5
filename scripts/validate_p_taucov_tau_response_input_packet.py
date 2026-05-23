#!/usr/bin/env python3
"""Validate the P-TauCov Tau-response input packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_tau_response_input_packet.md"
CSV = ROOT / "evidence/p_taucov_tau_response_input_packet.csv"
SUMMARY = ROOT / "evidence/p_taucov_tau_response_input_packet_summary.csv"
OUT = ROOT / "evidence/p_taucov_tau_response_input_packet_validation.csv"

REQUIRED_CLASSES = {
    "TAU_THEORY_BLOCKER",
    "POLICY_FREEZABLE",
    "POLICY_AND_THEORY",
    "FORMULA_READY",
    "DERIVED_AFTER_MAPS",
    "AUDIT_REQUIRED",
}

PRIMARY_BLOCKERS = {
    "BranchEquationFB",
    "ReducedBranchOperatorLBred",
    "ParentMorphologyMap",
    "ProjectionMorphologyMap",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_TAU_RESPONSE_INPUT_PACKET_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("packet_csv_exists", CSV.exists())
    add("summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_TAU_RESPONSE_INPUT_PACKET_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("all_required_classes_present", REQUIRED_CLASSES.issubset(set(df["SourceClass"])))
    add("primary_blockers_present", PRIMARY_BLOCKERS.issubset(set(df["SourceObject"])))
    add(
        "primary_blockers_are_theory_blockers",
        set(df.loc[df["SourceObject"].isin(PRIMARY_BLOCKERS), "SourceClass"]) == {"TAU_THEORY_BLOCKER"},
    )
    add("no_scoring_authorized", (df["ScoringAuthorized"].astype(str).str.lower() == "false").all())
    add(
        "generation_blocked_by_tau_theory_inputs",
        summary["DeltaCTauGenerationStatus"].iloc[0] == "BLOCKED_BY_TAU_THEORY_INPUTS",
    )
    add(
        "next_step_is_core_tau_response",
        summary["PrimaryNextStep"].iloc[0] == "define_F_B_LBred_M_parent_P_morph",
    )
    for phrase in [
        "primary bottleneck is not statistics",
        "F_B, L_B^red, M_parent, P_morph",
        "would be an artificial placeholder and must not be scored",
        "has isolated the Tau-side objects required",
        "has already produced a Tau-specific covariance response",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_TAU_RESPONSE_INPUT_PACKET_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_TAU_RESPONSE_INPUT_PACKET_VALID_BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
