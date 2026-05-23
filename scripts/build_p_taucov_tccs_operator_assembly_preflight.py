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
}

OUT_CHECKS = EVIDENCE / "p_taucov_tccs_operator_assembly_preflight.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tccs_operator_assembly_preflight_summary.csv"
OUT_DOC = DOCS / "p_taucov_tccs_operator_assembly_preflight.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_PREFLIGHT_v1"
STATUS = "P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_BLOCKED_BY_PARENT_TO_SCORE_EMBEDDING"
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
                "Artifact": str(SOURCES["P_morph_basis"].relative_to(ROOT)),
                "Observed": "basis vectors exist, but no single frozen P_morph operator convention is selected",
                "Passed": False,
                "BlocksObjectConstruction": True,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "CheckID": "PI_PERP_ASSEMBLY",
                "Component": "Pi_perp",
                "Artifact": "not yet built",
                "Observed": "projection-null and morphology-null policies exist, but no combined orthogonal-complement matrix is frozen",
                "Passed": False,
                "BlocksObjectConstruction": True,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "CheckID": "PARENT_TO_SCORE_EMBEDDING",
                "Component": "Embedding",
                "Artifact": "not yet built",
                "Observed": "parent-coordinate operators are 8-coordinate artifacts; Pi_bal is a 36-row score-space projector",
                "Passed": False,
                "BlocksObjectConstruction": True,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
        ]
    )
    out = pd.DataFrame(checks)
    out.to_csv(OUT_CHECKS, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": STATUS,
                "Checks": int(len(out)),
                "PassedChecks": int(out["Passed"].sum()),
                "BlockingChecks": int(out["BlocksObjectConstruction"].sum()),
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "NextRequiredGate": "freeze parent-to-score embedding plus P_morph operator convention and Pi_perp matrix",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    OUT_DOC.write_text(
        """# P-TauCov TCCS Operator Assembly Preflight

Freeze ID: `P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_PREFLIGHT_v1`

Status:

`P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_BLOCKED_BY_PARENT_TO_SCORE_EMBEDDING`

## Purpose

This preflight asks whether the ingredients for

```text
T_tau = Normalize(Pi_bal Pi_perp Orient_+([L_B_red, P_morph]; J_tau) Pi_perp Pi_bal)
```

can be assembled without score access.

## Result

The source pieces exist, but object construction is still blocked.

The main reason is not the orientation anchor anymore. A target-blind `J_tau`
candidate is now frozen. The blocking issue is dimensional and operational:

```text
parent-coordinate operators live in the 8-coordinate symbolic parent space;
Pi_bal lives in the 36-row score/covariance geometry.
```

Therefore a frozen parent-to-score embedding is required before the TCCS
commutator can be projected, balanced, and evaluated.

## Blocking Items

| Item | Status |
|---|---|
| `P_morph` | morphology basis exists, but no single operator convention is frozen |
| `Pi_perp` | projection-null and morphology-null policies exist, but no combined matrix is frozen |
| parent-to-score embedding | missing |

## Next Gate

```text
freeze parent-to-score embedding plus P_morph operator convention and Pi_perp matrix
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
