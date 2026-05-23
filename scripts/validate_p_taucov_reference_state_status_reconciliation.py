#!/usr/bin/env python3
"""Validate reference-state status reconciliation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ROWS = ROOT / "evidence/p_taucov_reference_state_status_reconciliation.csv"
SUMMARY = ROOT / "evidence/p_taucov_reference_state_status_reconciliation_summary.csv"
DOC = ROOT / "docs/p_taucov_reference_state_status_reconciliation.md"
OUT = ROOT / "evidence/p_taucov_reference_state_status_reconciliation_validation.csv"

AUDIT_ID = "P_TAUCOV_REFERENCE_STATE_STATUS_RECONCILIATION_VALIDATION"


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
        add("status_expected", str(summary["Status"]) == "P_TAUCOV_OPERATIONAL_REFERENCE_STATE_FROZEN_PHYSICAL_STABILITY_OPEN_NO_SCORING")
        add("all_layers_present", layers == {"OperationalReferenceDomain", "ReferenceCandidateSpec", "PhysicalDynamicalStability", "ResponseEnergyInterpretation"})
        add("operational_reference_frozen", bool(summary["OperationalReferenceFrozen"]) is True)
        add("assembly_not_blocked_by_reference", bool(summary["ReducedJacobianAssemblyBlockedByReference"]) is False)
        add("physical_stability_not_proven", bool(summary["PhysicalStabilityProven"]) is False)
        add("response_energy_pass", bool(summary["ResponseEnergySplitPass"]) is True)
        add("no_assembly_blocker_from_this_audit", str(summary["RemainingAssemblyBlockersFromThisAudit"]) == "NONE")
        add("physical_blocker_declared", str(summary["RemainingPhysicalClaimBlockers"]) == "FULL_DYNAMICAL_STABILITY")
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("doc_separates_operational_and_physical", "operational reference/domain freeze" in doc and "physical/dynamical stability" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_REFERENCE_STATE_STATUS_RECONCILIATION_VALID" if ok else "P_TAUCOV_REFERENCE_STATE_STATUS_RECONCILIATION_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
