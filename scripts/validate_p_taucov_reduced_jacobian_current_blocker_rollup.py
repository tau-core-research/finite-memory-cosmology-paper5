#!/usr/bin/env python3
"""Validate the current reduced-Jacobian blocker rollup."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ROLLUP = ROOT / "evidence/p_taucov_reduced_jacobian_current_blocker_rollup.csv"
SUMMARY = ROOT / "evidence/p_taucov_reduced_jacobian_current_blocker_rollup_summary.csv"
DOC = ROOT / "docs/p_taucov_reduced_jacobian_current_blocker_rollup.md"
OUT = ROOT / "evidence/p_taucov_reduced_jacobian_current_blocker_rollup_validation.csv"

AUDIT_ID = "P_TAUCOV_REDUCED_JACOBIAN_CURRENT_BLOCKER_ROLLUP_VALIDATION"


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

    for path in [ROLLUP, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [ROLLUP, SUMMARY, DOC]):
        rollup = pd.read_csv(ROLLUP)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        blockers = set(
            rollup.loc[rollup["StillBlocksReducedJacobian"].astype(bool), "ObjectID"].astype(str)
        )
        nonblockers = set(
            rollup.loc[~rollup["StillBlocksReducedJacobian"].astype(bool), "ObjectID"].astype(str)
        )
        add("status_still_blocked_no_scoring", str(summary["Status"]).endswith("STILL_BLOCKED_NO_SCORING"))
        add("expected_remaining_blockers", blockers == {"ReferenceState", "DynamicalStability"})
        add("expected_resolved_nonblockers", {"L_B_red", "D_Phi_F_B", "D_B_M_proj", "CovarianceMap"}.issubset(nonblockers))
        add("mediated_forcing_pass_recorded", "PASS" in str(summary["MediatedForcingStatus"]))
        add("projected_derivative_pass_recorded", "PASS" in str(summary["ProjectedMorphologyDerivativeStatus"]))
        add("covariance_map_pass_recorded", "PASS" in str(summary["CovarianceMapStatus"]))
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("doc_forbids_delta_c_tau_claim", "delta_C_Tau" in doc and "Tau Core has been validated" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_REDUCED_JACOBIAN_CURRENT_BLOCKER_ROLLUP_VALID" if ok else "P_TAUCOV_REDUCED_JACOBIAN_CURRENT_BLOCKER_ROLLUP_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
