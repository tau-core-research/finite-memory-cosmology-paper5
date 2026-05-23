#!/usr/bin/env python3
"""Validate the P-TauCov mediated parent-forcing chain audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "evidence/p_taucov_mediated_parent_forcing_chain_matrix.csv"
AUDIT = ROOT / "evidence/p_taucov_mediated_parent_forcing_chain_audit.csv"
SUMMARY = ROOT / "evidence/p_taucov_mediated_parent_forcing_chain_summary.csv"
DOC = ROOT / "docs/p_taucov_mediated_parent_forcing_chain_audit.md"
OUT = ROOT / "evidence/p_taucov_mediated_parent_forcing_chain_validation.csv"

AUDIT_ID = "P_TAUCOV_MEDIATED_PARENT_FORCING_CHAIN_VALIDATION"


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

    for path in [MATRIX, AUDIT, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [MATRIX, AUDIT, SUMMARY, DOC]):
        matrix = pd.read_csv(MATRIX)
        audit = pd.read_csv(AUDIT)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")

        add("status_pass_no_scoring", str(summary["Status"]).endswith("NO_SCORING") and "PASS" in str(summary["Status"]))
        add("all_gates_pass", bool(audit["Passed"].all()))
        add("direct_forcing_zero", abs(float(summary["Direct_D_Phi_F_B"])) < 1e-12)
        add("mediator_couplings_nonzero", abs(float(summary["D_P_F_B"])) > 1e-12 and abs(float(summary["D_Phi_F_P"])) > 1e-12)
        add("branch_block_invertible", abs(float(summary["Det_L_X"])) > 1e-12)
        add("effective_b_response_nonzero", abs(float(summary["EffectiveDeltaBPerDeltaPhi"])) > 1e-12)
        add("stability_not_overclaimed", bool(summary["FullStabilityResolved"]) is False)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("matrix_records_three_blocks", set(matrix["MatrixID"].astype(str)) == {"L_X_branch_mediated", "D_Phi_F_X", "minus_L_X_inverse_D_Phi_F_X"})
        add("doc_forbids_validation_claim", "Tau Core has been validated" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_MEDIATED_PARENT_FORCING_CHAIN_VALID" if ok else "P_TAUCOV_MEDIATED_PARENT_FORCING_CHAIN_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
