#!/usr/bin/env python3
"""Reconcile operational reference-domain freeze with physical stability gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

REFERENCE_DOMAIN = EVIDENCE / "p_taucov_reference_domain_packet_summary.csv"
REFERENCE_CANDIDATE = EVIDENCE / "p_taucov_reference_state_candidate_spec_summary.csv"
STABILITY = EVIDENCE / "p_taucov_reference_background_stability_summary.csv"
RESPONSE_ENERGY = EVIDENCE / "p_taucov_response_energy_split_summary.csv"

OUT = EVIDENCE / "p_taucov_reference_state_status_reconciliation.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_reference_state_status_reconciliation_summary.csv"
DOC = DOCS / "p_taucov_reference_state_status_reconciliation.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_REFERENCE_STATE_STATUS_RECONCILIATION_v1"
CLAIM_BOUNDARY = "reference_state_status_reconciliation_no_scoring"


def read_status(path: Path, column: str = "Status") -> str:
    if not path.exists():
        return "MISSING"
    df = pd.read_csv(path)
    if column in df.columns:
        return str(df.iloc[0][column])
    if "PacketID" in df.columns:
        return str(df.iloc[0]["PacketID"])
    return "AVAILABLE_NO_STATUS_COLUMN"


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    domain = pd.read_csv(REFERENCE_DOMAIN).iloc[0]
    stability = pd.read_csv(STABILITY).iloc[0]
    response_energy = pd.read_csv(RESPONSE_ENERGY).iloc[0]
    candidate_status = read_status(REFERENCE_CANDIDATE)

    operational_frozen = bool(domain["ReferenceStateFrozen"]) and bool(domain["ReducedDomainFrozen"])
    full_stability = bool(stability["FullStabilityProven"])
    response_energy_ok = str(response_energy["Status"]) == "P_TAUCOV_RESPONSE_ENERGY_SPLIT_PASS_NO_SCORING"

    rows = [
        {
            "Layer": "OperationalReferenceDomain",
            "Status": "FROZEN" if operational_frozen else "NOT_FROZEN",
            "Evidence": "docs/p_taucov_reference_domain_packet.md",
            "BlocksReducedJacobianAssembly": not operational_frozen,
            "BlocksPhysicalClaim": False,
            "Interpretation": "coordinate origin and reduced domain are frozen",
        },
        {
            "Layer": "ReferenceCandidateSpec",
            "Status": candidate_status,
            "Evidence": "docs/p_taucov_reference_state_candidate_spec.md",
            "BlocksReducedJacobianAssembly": False,
            "BlocksPhysicalClaim": True,
            "Interpretation": "candidate-spec caution remains relevant for physical background claims",
        },
        {
            "Layer": "PhysicalDynamicalStability",
            "Status": "PROVEN" if full_stability else "NOT_PROVEN",
            "Evidence": "docs/p_taucov_reference_background_stability_diagnostic.md",
            "BlocksReducedJacobianAssembly": False,
            "BlocksPhysicalClaim": True,
            "Interpretation": "full dynamical stability is not proven",
        },
        {
            "Layer": "ResponseEnergyInterpretation",
            "Status": "PASS" if response_energy_ok else "NOT_PASS",
            "Evidence": "docs/p_taucov_response_energy_split_packet.md",
            "BlocksReducedJacobianAssembly": False,
            "BlocksPhysicalClaim": True,
            "Interpretation": "supports response-not-energy reading but not full dynamics",
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

    assembly_blocked = not operational_frozen
    physical_blocked = not full_stability
    status = (
        "P_TAUCOV_OPERATIONAL_REFERENCE_STATE_FROZEN_PHYSICAL_STABILITY_OPEN_NO_SCORING"
        if operational_frozen and physical_blocked
        else "P_TAUCOV_REFERENCE_STATE_RECONCILIATION_BLOCKED_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "OperationalReferenceFrozen": operational_frozen,
                "ReducedJacobianAssemblyBlockedByReference": assembly_blocked,
                "PhysicalStabilityProven": full_stability,
                "ResponseEnergySplitPass": response_energy_ok,
                "RemainingAssemblyBlockersFromThisAudit": "NONE" if not assembly_blocked else "OPERATIONAL_REFERENCE_STATE",
                "RemainingPhysicalClaimBlockers": "FULL_DYNAMICAL_STABILITY" if physical_blocked else "NONE",
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Reference-State Status Reconciliation

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This note separates two meanings that had been conflated in the blocker list:

1. operational reference/domain freeze for reduced-Jacobian assembly;
2. physical/dynamical stability of the parent background.

## Result

The operational reference state and reduced domain are frozen by:

[`p_taucov_reference_domain_packet.md`](p_taucov_reference_domain_packet.md)

Therefore `ReferenceState` no longer blocks reduced-Jacobian assembly at the
operational level.

However, the physical background stability gate remains open:

[`p_taucov_reference_background_stability_diagnostic.md`](p_taucov_reference_background_stability_diagnostic.md)

and the response/energy split packet only supports a response-operator
interpretation:

[`p_taucov_response_energy_split_packet.md`](p_taucov_response_energy_split_packet.md)

## Claim Boundary

Allowed statement:

> The operational reference/domain package is frozen for source assembly.

Forbidden statement:

> The parent background is physically stable, empirical scoring is authorized,
> or Tau Core has been validated.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
