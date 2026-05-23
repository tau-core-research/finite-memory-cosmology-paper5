#!/usr/bin/env python3
"""Validate dynamical-stability status reconciliation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ROWS = ROOT / "evidence/p_taucov_dynamical_stability_status_reconciliation.csv"
SUMMARY = ROOT / "evidence/p_taucov_dynamical_stability_status_reconciliation_summary.csv"
DOC = ROOT / "docs/p_taucov_dynamical_stability_status_reconciliation.md"
OUT = ROOT / "evidence/p_taucov_dynamical_stability_status_reconciliation_validation.csv"

AUDIT_ID = "P_TAUCOV_DYNAMICAL_STABILITY_STATUS_RECONCILIATION_VALIDATION"


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

    for path in [ROWS, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [ROWS, SUMMARY, DOC]):
        rows = pd.read_csv(ROWS)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        layers = set(rows["Layer"].astype(str))
        add("status_expected", str(summary["Status"]) == "P_TAUCOV_LINEAR_DYNAMICAL_STABILITY_ASSEMBLY_READY_PHYSICAL_STABILITY_OPEN_NO_SCORING")
        add("all_layers_present", layers == {"ResponseEnergySplit", "LinearDynamicalStability", "NonlinearUVStability", "BackgroundEnergyHessian"})
        add("response_energy_pass", bool(summary["ResponseEnergySplitPass"]) is True)
        add("linear_stability_pass", bool(summary["LinearDynamicalStabilityPass"]) is True)
        add("assembly_not_blocked_by_stability", bool(summary["ReducedJacobianAssemblyBlockedByStability"]) is False)
        add("nonlinear_not_proven", bool(summary["PhysicalNonlinearStabilityProven"]) is False)
        add("uv_not_proven", bool(summary["MicroscopicUVCompletionProven"]) is False)
        add("no_assembly_blocker_from_this_audit", str(summary["RemainingAssemblyBlockersFromThisAudit"]) == "NONE")
        add("physical_blockers_declared", str(summary["RemainingPhysicalClaimBlockers"]) == "NONLINEAR_STABILITY;MICROSCOPIC_UV_COMPLETION")
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("doc_forbids_uv_validation", "UV completion" in doc and "Tau Core validation" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_DYNAMICAL_STABILITY_STATUS_RECONCILIATION_VALID" if ok else "P_TAUCOV_DYNAMICAL_STABILITY_STATUS_RECONCILIATION_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
