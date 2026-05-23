#!/usr/bin/env python3
"""Reconcile linear dynamical stability with nonlinear/UV stability claims."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

LINEAR = EVIDENCE / "p_taucov_linear_dynamical_stability_summary.csv"
RESPONSE_ENERGY = EVIDENCE / "p_taucov_response_energy_split_summary.csv"
BACKGROUND = EVIDENCE / "p_taucov_reference_background_stability_summary.csv"

OUT = EVIDENCE / "p_taucov_dynamical_stability_status_reconciliation.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_dynamical_stability_status_reconciliation_summary.csv"
DOC = DOCS / "p_taucov_dynamical_stability_status_reconciliation.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_DYNAMICAL_STABILITY_STATUS_RECONCILIATION_v1"
CLAIM_BOUNDARY = "dynamical_stability_status_reconciliation_no_scoring"


def status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    return str(pd.read_csv(path).iloc[0]["Status"])


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    linear = pd.read_csv(LINEAR).iloc[0]
    response = pd.read_csv(RESPONSE_ENERGY).iloc[0]
    background = pd.read_csv(BACKGROUND).iloc[0]
    linear_pass = str(linear["Status"]) == "P_TAUCOV_LINEAR_DYNAMICAL_STABILITY_PASS_NO_SCORING"
    response_pass = str(response["Status"]) == "P_TAUCOV_RESPONSE_ENERGY_SPLIT_PASS_NO_SCORING"
    background_full = bool(background["FullStabilityProven"])
    assembly_resolved = linear_pass and response_pass

    rows = [
        {
            "Layer": "ResponseEnergySplit",
            "Status": status(RESPONSE_ENERGY),
            "Evidence": "docs/p_taucov_response_energy_split_packet.md",
            "BlocksReducedJacobianAssembly": not response_pass,
            "BlocksPhysicalClaim": True,
            "Interpretation": "signed response can come from positive microscopic branch energy",
        },
        {
            "Layer": "LinearDynamicalStability",
            "Status": status(LINEAR),
            "Evidence": "docs/p_taucov_linear_dynamical_stability_packet.md",
            "BlocksReducedJacobianAssembly": not linear_pass,
            "BlocksPhysicalClaim": True,
            "Interpretation": "bounded one-mode linear dynamics supplied",
        },
        {
            "Layer": "NonlinearUVStability",
            "Status": "NOT_PROVEN",
            "Evidence": "none",
            "BlocksReducedJacobianAssembly": False,
            "BlocksPhysicalClaim": True,
            "Interpretation": "nonlinear stability and microscopic UV completion remain open",
        },
        {
            "Layer": "BackgroundEnergyHessian",
            "Status": status(BACKGROUND),
            "Evidence": "docs/p_taucov_reference_background_stability_diagnostic.md",
            "BlocksReducedJacobianAssembly": False,
            "BlocksPhysicalClaim": True,
            "Interpretation": "active Hessian is a response witness, not positive energy Hessian",
        },
    ]
    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **row,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in rows
        ]
    )
    df.to_csv(OUT, index=False)

    status_value = (
        "P_TAUCOV_LINEAR_DYNAMICAL_STABILITY_ASSEMBLY_READY_PHYSICAL_STABILITY_OPEN_NO_SCORING"
        if assembly_resolved and not background_full
        else "P_TAUCOV_DYNAMICAL_STABILITY_RECONCILIATION_BLOCKED_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status_value,
                "ResponseEnergySplitPass": response_pass,
                "LinearDynamicalStabilityPass": linear_pass,
                "ReducedJacobianAssemblyBlockedByStability": not assembly_resolved,
                "PhysicalNonlinearStabilityProven": False,
                "MicroscopicUVCompletionProven": False,
                "RemainingAssemblyBlockersFromThisAudit": "NONE" if assembly_resolved else "LINEAR_DYNAMICAL_STABILITY",
                "RemainingPhysicalClaimBlockers": "NONLINEAR_STABILITY;MICROSCOPIC_UV_COMPLETION",
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Dynamical-Stability Status Reconciliation

Freeze ID: `{FREEZE_ID}`

Status:

`{status_value}`

## Purpose

This note separates reduced-Jacobian assembly readiness from physical
stability claims.

## Result

The response/energy split packet and the linear dynamical stability packet
jointly show that the signed response can be embedded in a linearly bounded
one-mode branch dynamics:

[`p_taucov_response_energy_split_packet.md`](p_taucov_response_energy_split_packet.md)

[`p_taucov_linear_dynamical_stability_packet.md`](p_taucov_linear_dynamical_stability_packet.md)

Therefore `DynamicalStability` no longer blocks reduced-Jacobian assembly at
the minimal linear level.

However, nonlinear stability and microscopic UV completion remain open. This
still forbids physical validation claims.

## Claim Boundary

Allowed statement:

> The minimal linear branch dynamics is stable enough for source assembly.

Forbidden statement:

> Nonlinear stability, UV completion, empirical scoring, or Tau Core validation
> has been established.
""",
        encoding="utf-8",
    )
    print(status_value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
