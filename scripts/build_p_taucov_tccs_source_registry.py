#!/usr/bin/env python3
"""Build a target-blind source registry for the TCCS route."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT_REGISTRY = EVIDENCE / "p_taucov_tccs_source_registry.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tccs_source_registry_summary.csv"
OUT_DOC = DOCS / "p_taucov_tccs_source_registry.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_TCCS_SOURCE_REGISTRY_v1"
STATUS = "P_TAUCOV_TCCS_SOURCE_REGISTRY_READY_FOR_OBJECT_PREFLIGHT_NO_SCORING"
CLAIM_BOUNDARY = "tccs_source_registry_no_object_no_scoring"


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def load_projection_fail_metric() -> tuple[str, str]:
    summary = EVIDENCE / "p_taucov_parent_hessian_commutator_summary.csv"
    if not summary.exists():
        return "", "previous_commutator_summary_missing"
    row = pd.read_csv(summary).iloc[0].to_dict()
    proj = row.get("ProjectionNullAbsCorrelation", "")
    morph = row.get("MorphologyNullAbsCorrelation", "")
    return str(proj), f"previous morphology-null={morph}; projection-null={proj}"


def main() -> int:
    projection_fail, previous_note = load_projection_fail_metric()
    rows = [
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "ComponentID": "L_B_red",
            "Role": "parent-side reduced B-Hessian or response operator",
            "CandidateSource": "evidence/p_taucov_parent_hessian_commutator_object.csv; evidence/p_taucov_projection_essentiality_parent_action_hessian.csv",
            "SourceExists": exists("evidence/p_taucov_parent_hessian_commutator_object.csv")
            and exists("evidence/p_taucov_projection_essentiality_parent_action_hessian.csv"),
            "SourceStatus": "AVAILABLE_FOR_OBJECT_PREFLIGHT",
            "BlockingIssue": "none for preflight; must still pass TCCS object-construction gates",
            "ScoringAuthorized": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "ComponentID": "P_morph",
            "Role": "morphology/projection readout operator",
            "CandidateSource": "evidence/p_taucov_p4_morphology_basis.csv; evidence/p_taucov_p4_morphology_basis_summary.csv",
            "SourceExists": exists("evidence/p_taucov_p4_morphology_basis.csv")
            and exists("evidence/p_taucov_p4_morphology_basis_summary.csv"),
            "SourceStatus": "FROZEN_OPERATOR_CONVENTION_AVAILABLE",
            "BlockingIssue": "none for preflight; convention frozen in p_taucov_tccs_pmorph_piperp_summary.csv",
            "ScoringAuthorized": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "ComponentID": "Pi_perp",
            "Role": "projection-null and morphology-null orthogonal complement projector",
            "CandidateSource": "evidence/p_taucov_p4_morphology_orthogonalization_gate.csv; projection-null controls from parent-action null comparator packet",
            "SourceExists": exists("evidence/p_taucov_p4_morphology_orthogonalization_gate.csv")
            and exists("evidence/p_taucov_parent_action_null_comparators.csv"),
            "SourceStatus": "FROZEN_MATRIX_AVAILABLE",
            "BlockingIssue": "none for preflight; matrix frozen in p_taucov_tccs_piperp_matrix.csv",
            "ScoringAuthorized": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "ComponentID": "Pi_bal",
            "Role": "family/clock balanced subspace projector",
            "CandidateSource": "evidence/p_taucov_clock_family_balance_projector_matrix.csv",
            "SourceExists": exists("evidence/p_taucov_clock_family_balance_projector_matrix.csv"),
            "SourceStatus": "AVAILABLE",
            "BlockingIssue": "none for registry; must be checked again after TCCS object construction",
            "ScoringAuthorized": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "ComponentID": "J_tau",
            "Role": "target-blind parent-side orientation anchor",
            "CandidateSource": "evidence/p_taucov_tccs_jtau_anchor_candidate_matrix.csv",
            "SourceExists": exists("evidence/p_taucov_tccs_jtau_anchor_candidate_matrix.csv"),
            "SourceStatus": "FROZEN_ANCHOR_CANDIDATE_AVAILABLE",
            "BlockingIssue": "none for preflight; target-blind J_tau candidate frozen",
            "ScoringAuthorized": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "ComponentID": "TCCS_OBJECT",
            "Role": "scoreable oriented branch-balanced projection-orthogonal commutator",
            "CandidateSource": "not constructed",
            "SourceExists": False,
            "SourceStatus": "NOT_CONSTRUCTED_PREFLIGHT_READY",
            "BlockingIssue": "object not constructed yet; next step is object-construction preflight, not scoring",
            "ScoringAuthorized": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
    ]
    registry = pd.DataFrame(rows)
    registry.to_csv(OUT_REGISTRY, index=False)
    missing = int((~registry["SourceExists"]).sum())
    blockers = int(registry["SourceStatus"].astype(str).str.contains("MISSING|BLOCKED|PARTIAL|NOT_ACCEPTED", regex=True).sum())
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": STATUS,
                "Components": int(len(registry)),
                "MissingSources": missing,
                "BlockingComponents": blockers,
                "PreviousProjectionNullAbsCorrelation": projection_fail,
                "PreviousCommutatorNote": previous_note,
                "ObjectConstructed": False,
                "ObjectConstructionPreflightAuthorized": True,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    OUT_DOC.write_text(
        f"""# P-TauCov TCCS Source Registry

Freeze ID: `P_TAUCOV_TCCS_SOURCE_REGISTRY_v1`

Status:

`{STATUS}`

## Purpose

This registry keeps the Tau Commutator Curvature Signature route target-blind. It does not build a TCCS object and does not authorize scoring. It only declares which frozen or missing sources would be needed before the object

```text
T_tau = Normalize(Pi_bal Pi_perp Orient_+([L_B_red, P_morph]; J_tau) Pi_perp Pi_bal)
```

can be constructed.

## Why This Registry Is Needed

The previous parent-Hessian commutator attempt was informative but not sufficient:

```text
{previous_note}
```

The TCCS support components are now frozen enough for object-construction preflight. This still does not authorize scoring.

## Component Status

| Component | Status | Blocking issue |
|---|---|---|
| `L_B_red` | `AVAILABLE_FOR_OBJECT_PREFLIGHT` | must pass object-construction gates |
| `P_morph` | `FROZEN_OPERATOR_CONVENTION_AVAILABLE` | none for preflight |
| `Pi_perp` | `FROZEN_MATRIX_AVAILABLE` | none for preflight |
| `Pi_bal` | `AVAILABLE` | must be rechecked after object construction |
| `J_tau` | `FROZEN_ANCHOR_CANDIDATE_AVAILABLE` | none for preflight |
| `TCCS_OBJECT` | `NOT_CONSTRUCTED_PREFLIGHT_READY` | next step is object-construction preflight |

## Claim Boundary

Allowed statement:

> The TCCS source registry identifies the required parent-side sources and authorizes object-construction preflight without scoring.

Forbidden statement:

> A TCCS object has been built, score-authorized, or shown to carry a Tau signal.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
