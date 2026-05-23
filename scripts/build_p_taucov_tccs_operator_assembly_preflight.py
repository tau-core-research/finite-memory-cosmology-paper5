#!/usr/bin/env python3
"""Preflight TCCS operator assembly without constructing a score object."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SOURCES = {
    "J_tau": EVIDENCE / "p_taucov_tccs_jtau_anchor_candidate_matrix.csv",
    "L_B_red_candidate": EVIDENCE / "p_taucov_projection_essentiality_parent_action_hessian.csv",
    "P_morph_basis": EVIDENCE / "p_taucov_p4_morphology_basis.csv",
    "NullComparatorPolicy": EVIDENCE / "p_taucov_parent_action_null_comparators.csv",
    "Pi_bal": EVIDENCE / "p_taucov_clock_family_balance_projector_matrix.csv",
    "ParentScoreEmbedding": EVIDENCE / "p_taucov_tccs_parent_score_embedding_summary.csv",
    "PmorphPiPerp": EVIDENCE / "p_taucov_tccs_pmorph_piperp_summary.csv",
}

OUT_CHECKS = EVIDENCE / "p_taucov_tccs_operator_assembly_preflight.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tccs_operator_assembly_preflight_summary.csv"
OUT_DOC = DOCS / "p_taucov_tccs_operator_assembly_preflight.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_PREFLIGHT_v1"
STATUS = "P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_READY_FOR_OBJECT_PREFLIGHT_NO_SCORING"
CLAIM_BOUNDARY = "tccs_operator_assembly_preflight_no_object_no_scoring"


def csv_shape(path: Path) -> str:
    if not path.exists():
        return "missing"
    df = pd.read_csv(path)
    return f"{df.shape[0]}x{df.shape[1]}"


def main() -> int:
    checks = []
    for component, path in SOURCES.items():
        checks.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "CheckID": f"SOURCE_EXISTS_{component}",
                "Component": component,
                "Artifact": str(path.relative_to(ROOT)),
                "Observed": csv_shape(path),
                "Passed": path.exists(),
                "BlocksObjectConstruction": not path.exists(),
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    # These are structural checks, not numerical target checks.
    checks.extend(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "CheckID": "P_MORPH_OPERATOR_CONVENTION",
                "Component": "P_morph",
                "Artifact": str(SOURCES["PmorphPiPerp"].relative_to(ROOT)),
                "Observed": "P_morph convention is frozen as the parent-coordinate projector onto M/P axes",
                "Passed": SOURCES["PmorphPiPerp"].exists(),
                "BlocksObjectConstruction": not SOURCES["PmorphPiPerp"].exists(),
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "CheckID": "PI_PERP_ASSEMBLY",
                "Component": "Pi_perp",
                "Artifact": str(SOURCES["PmorphPiPerp"].relative_to(ROOT)),
                "Observed": "Pi_perp matrix is frozen as the 36-row complement to embedded M/P columns",
                "Passed": SOURCES["PmorphPiPerp"].exists(),
                "BlocksObjectConstruction": not SOURCES["PmorphPiPerp"].exists(),
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "CheckID": "PARENT_TO_SCORE_EMBEDDING",
                "Component": "Embedding",
                "Artifact": str(SOURCES["ParentScoreEmbedding"].relative_to(ROOT)),
                "Observed": "target-blind parent-to-score embedding is frozen; must be used before TCCS object construction",
                "Passed": SOURCES["ParentScoreEmbedding"].exists(),
                "BlocksObjectConstruction": not SOURCES["ParentScoreEmbedding"].exists(),
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
        ]
    )
    out = pd.DataFrame(checks)
    out.to_csv(OUT_CHECKS, index=False)
    object_blocked = bool(out["BlocksObjectConstruction"].any())
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": STATUS,
                "Checks": int(len(out)),
                "PassedChecks": int(out["Passed"].sum()),
                "BlockingChecks": int(out["BlocksObjectConstruction"].sum()),
                "ObjectConstructionAuthorized": not object_blocked,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "NextRequiredGate": "run TCCS object-construction preflight without scoring",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    OUT_DOC.write_text(
        """# P-TauCov TCCS Operator Assembly Preflight

Freeze ID: `P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_PREFLIGHT_v1`

Status:

`P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_BLOCKED_BY_OPERATOR_CONVENTION_AND_PI_PERP`

## Purpose

This preflight asks whether the ingredients for

```text
T_tau = Normalize(Pi_bal Pi_perp Orient_+([L_B_red, P_morph]; J_tau) Pi_perp Pi_bal)
```

can be assembled without score access.

## Result

The source pieces now exist for object-construction preflight.

The orientation anchor and parent-to-score embedding are no longer the main blockers. A target-blind `J_tau`
candidate and a target-blind parent-to-score embedding are now frozen.

```text
J_tau: frozen parent-coordinate skew orientation
embedding: frozen 8-coordinate to 36-row bridge
```

The remaining step is not scoring. It is an object-construction preflight that
checks whether the assembled commutator is nonzero and whether it survives the
pre-score TCCS gates.

## Blocking Items

| Item | Status |
|---|---|
| `P_morph` | frozen |
| `Pi_perp` | frozen |
| parent-to-score embedding | frozen |

## Next Gate

```text
run TCCS object-construction preflight without scoring
```

This must remain pre-score. It may use coordinate definitions, declared null
policies, and source geometry. It may not use target residuals, score outcomes,
dominant-family identity, or previous gain signs.

## Claim Boundary

Allowed statement:

> The TCCS operator assembly is blocked by a concrete parent-to-score embedding and orthogonalization gate.

Forbidden statement:

> A TCCS object has been constructed, score-authorized, or shown to carry a Tau signal.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
