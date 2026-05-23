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
STATUS = "P_TAUCOV_TCCS_SOURCE_REGISTRY_READY_OBJECT_BLOCKED"
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
            "SourceStatus": "AVAILABLE_BUT_NOT_ACCEPTED_FOR_TCCS",
            "BlockingIssue": "prior commutator source failed projection-null separation; TCCS needs a projection-orthogonalized reduced Hessian source",
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
            "SourceStatus": "AVAILABLE_AS_MORPHOLOGY_BASIS_NOT_YET_OPERATOR_FREEZE",
            "BlockingIssue": "requires explicit operator convention P_morph before commutator construction",
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
            "SourceStatus": "PARTIAL_SOURCE_AVAILABLE_NOT_ASSEMBLED",
            "BlockingIssue": "must combine projection-null and morphology-null bases into one frozen orthogonal projector",
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
            "CandidateSource": "none frozen",
            "SourceExists": False,
            "SourceStatus": "MISSING_REQUIRED_SOURCE",
            "BlockingIssue": "orientation anchor must be derived from parent-side conventions, not score sign or dominant family identity",
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
            "SourceStatus": "BLOCKED",
            "BlockingIssue": "blocked until L_B_red, P_morph, Pi_perp, Pi_bal, and J_tau are frozen and validated",
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

Thus the next object must be explicitly projection-orthogonal, branch-balanced, and orientation-anchored before any empirical score is touched.

## Component Status

| Component | Status | Blocking issue |
|---|---|---|
| `L_B_red` | `AVAILABLE_BUT_NOT_ACCEPTED_FOR_TCCS` | prior commutator source failed projection-null separation |
| `P_morph` | `AVAILABLE_AS_MORPHOLOGY_BASIS_NOT_YET_OPERATOR_FREEZE` | needs explicit operator convention |
| `Pi_perp` | `PARTIAL_SOURCE_AVAILABLE_NOT_ASSEMBLED` | projection-null and morphology-null bases must be combined |
| `Pi_bal` | `AVAILABLE` | must be rechecked after object construction |
| `J_tau` | `MISSING_REQUIRED_SOURCE` | target-blind orientation anchor is not frozen |
| `TCCS_OBJECT` | `BLOCKED` | no object until all source components are frozen |

## Claim Boundary

Allowed statement:

> The TCCS source registry identifies the required parent-side sources and shows that object construction is still blocked.

Forbidden statement:

> A TCCS object has been built, score-authorized, or shown to carry a Tau signal.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
