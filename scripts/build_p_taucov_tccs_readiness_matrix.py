#!/usr/bin/env python3
"""Build the TCCS readiness matrix from protocol and source artifacts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_SUMMARY = EVIDENCE / "p_taucov_tccs_protocol_summary.csv"
SOURCE_SUMMARY = EVIDENCE / "p_taucov_tccs_source_registry_summary.csv"
ANCHOR_SUMMARY = EVIDENCE / "p_taucov_tccs_orientation_anchor_summary.csv"
JTAU_SUMMARY = EVIDENCE / "p_taucov_tccs_jtau_anchor_candidate_summary.csv"

OUT_MATRIX = EVIDENCE / "p_taucov_tccs_readiness_matrix.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tccs_readiness_summary.csv"
OUT_DOC = DOCS / "p_taucov_tccs_readiness_matrix.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_TCCS_READINESS_MATRIX_v1"
STATUS = "P_TAUCOV_TCCS_READY_AS_PROTOCOL_OBJECT_BLOCKED_NO_SCORING"
CLAIM_BOUNDARY = "tccs_readiness_matrix_protocol_only_no_object_no_scoring"


def read_status(path: Path, status_col: str = "Status") -> str:
    if not path.exists():
        return "MISSING"
    return str(pd.read_csv(path).iloc[0][status_col])


def main() -> int:
    rows = [
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "LayerID": "TCCS_PROTOCOL",
            "SourceArtifact": str(PROTOCOL_SUMMARY.relative_to(ROOT)),
            "LayerStatus": read_status(PROTOCOL_SUMMARY),
            "Ready": True,
            "BlocksObjectConstruction": False,
            "BlocksScoring": True,
            "Reason": "protocol and gates are defined, but they intentionally authorize no object or score",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "LayerID": "TCCS_SOURCE_REGISTRY",
            "SourceArtifact": str(SOURCE_SUMMARY.relative_to(ROOT)),
            "LayerStatus": read_status(SOURCE_SUMMARY),
            "Ready": True,
            "BlocksObjectConstruction": True,
            "BlocksScoring": True,
            "Reason": "source registry identifies missing J_tau and incomplete Pi_perp/operator freeze",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "LayerID": "TCCS_ORIENTATION_ANCHOR",
            "SourceArtifact": str(ANCHOR_SUMMARY.relative_to(ROOT)),
            "LayerStatus": read_status(ANCHOR_SUMMARY),
            "Ready": True,
            "BlocksObjectConstruction": False,
            "BlocksScoring": True,
            "Reason": "anchor classes are specified; a separate J_tau candidate freeze is now available",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "LayerID": "TCCS_JTAU_ANCHOR_CANDIDATE",
            "SourceArtifact": str(JTAU_SUMMARY.relative_to(ROOT)),
            "LayerStatus": read_status(JTAU_SUMMARY),
            "Ready": True,
            "BlocksObjectConstruction": False,
            "BlocksScoring": True,
            "Reason": "target-blind skew orientation anchor candidate is frozen, but object construction still needs Pi_perp/P_morph/L_B_red assembly",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
    ]
    matrix = pd.DataFrame(rows)
    matrix.to_csv(OUT_MATRIX, index=False)

    object_blocked = bool(matrix["BlocksObjectConstruction"].any())
    scoring_blocked = bool(matrix["BlocksScoring"].any())
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": STATUS,
                "Layers": int(len(matrix)),
                "AllLayersReady": bool(matrix["Ready"].all()),
                "ObjectConstructionAuthorized": not object_blocked,
                "ScoringAuthorized": not scoring_blocked,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "NextRequiredGate": "assemble Pi_perp/P_morph/L_B_red around frozen J_tau without score access",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov TCCS Readiness Matrix

Freeze ID: `P_TAUCOV_TCCS_READINESS_MATRIX_v1`

Status:

`P_TAUCOV_TCCS_READY_AS_PROTOCOL_OBJECT_BLOCKED_NO_SCORING`

## Current State

The Tau Commutator Curvature Signature route is ready as a protocol, not as a constructed object.

```text
T_tau = Normalize(Pi_bal Pi_perp Orient_+([L_B_red, P_morph]; J_tau) Pi_perp Pi_bal)
```

## Readiness Result

| Layer | Result |
|---|---|
| protocol/gates | ready |
| source registry | ready, but object-blocking sources remain |
| orientation anchor | spec ready |
| `J_tau` candidate | frozen, target-blind, no scoring |
| TCCS object | not constructed |
| scoring | not authorized |
| survival claim | not authorized |

## Next Gate

The next legitimate Tau-specific step is not scoring. It is:

```text
assemble Pi_perp/P_morph/L_B_red around frozen J_tau without score access
```

Only after that can a pre-score object-construction validator decide whether a TCCS object exists at all.

## Claim Boundary

Allowed statement:

> The TCCS route is now a defined protocol with a source/readiness audit.

Forbidden statement:

> TCCS has produced an empirical Tau signal or survived a scorecard.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
