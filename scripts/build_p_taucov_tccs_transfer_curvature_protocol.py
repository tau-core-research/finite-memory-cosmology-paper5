#!/usr/bin/env python3
"""Define the TCCS transfer-curvature protocol implied by the no-go theorem."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT_GATES = EVIDENCE / "p_taucov_tccs_transfer_curvature_protocol_gates.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tccs_transfer_curvature_protocol_summary.csv"
OUT_DOC = DOCS / "p_taucov_tccs_transfer_curvature_protocol.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_TCCS_TRANSFER_CURVATURE_PROTOCOL_v1"
STATUS = "P_TAUCOV_TCCS_TRANSFER_CURVATURE_PROTOCOL_DEFINED_NO_OBJECT_NO_SCORING"
CLAIM_BOUNDARY = "tccs_transfer_curvature_protocol_no_object_no_scoring"


GATES = [
    ("TC-G1_NOGO_ACKNOWLEDGED", "double-sided Pi_perp commutator is forbidden by no-go theorem", "required"),
    ("TC-G2_OFFDIAGONAL_TRANSFER", "primary transfer must be Pi_perp [H,P] P or its adjoint", "required"),
    ("TC-G3_COVARIANCE_SAFE_CURVATURE", "PSD route must be K_curv = Pi_perp [H,P] P [H,P]^T Pi_perp", "required for covariance scoring"),
    ("TC-G4_NO_SCORE_BASED_H_SELECTION", "H component must be selected before empirical scoring", "required"),
    ("TC-G5_NULL_OVERLAP", "transfer-curvature must pass projection/morphology/generic null pre-score gates", "required"),
    ("TC-G6_BALANCE_RETENTION", "Pi_bal K_curv Pi_bal must retain nontrivial norm", ">=0.20"),
    ("TC-G7_FAMILY_DIAGONAL_CONTROLS", "family dominance and diagonal inflation must remain below frozen limits", "required"),
    ("TC-G8_SCORING_FIREWALL", "no survival claim until separate final manifest and scorecard authorization", "required"),
]


def main() -> int:
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "Requirement": requirement,
                "Threshold": threshold,
                "ScoringAuthorizedByGate": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, requirement, threshold in GATES
        ]
    ).to_csv(OUT_GATES, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": STATUS,
                "CorrectedObjectClass": "transfer_curvature",
                "ForbiddenObjectClass": "Pi_perp_[H_P]_Pi_perp",
                "PrimaryTransfer": "T_transfer = Pi_perp [H,P] P",
                "CovarianceSafeObject": "K_curv = Pi_perp [H,P] P [H,P]^T Pi_perp",
                "ObjectConstructed": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    OUT_DOC.write_text(
        """# P-TauCov TCCS Transfer-Curvature Protocol

Freeze ID: `P_TAUCOV_TCCS_TRANSFER_CURVATURE_PROTOCOL_v1`

Status:

`P_TAUCOV_TCCS_TRANSFER_CURVATURE_PROTOCOL_DEFINED_NO_OBJECT_NO_SCORING`

## Motivation

The double-sided projected commutator is mathematically blocked:

```text
Pi_perp [H,P] Pi_perp = 0
```

for an exact projector `P` and its complement `Pi_perp`.

Therefore the next TCCS object class must measure transfer between the
morphology/projection subspace and its complement, not a double-sided
complement restriction of the raw commutator.

## Corrected Candidate Class

Signed transfer:

```text
T_transfer = Pi_perp [H,P] P
```

Covariance-safe curvature:

```text
K_curv = Pi_perp [H,P] P [H,P]^T Pi_perp
```

The PSD form may become a reviewer-friendly covariance-deformation candidate
only after pre-score gates pass and a separate scoring manifest is frozen.

## Forbidden Move

Do not return to:

```text
Pi_perp [H,P] Pi_perp
```

as a scoreable object. The no-go theorem already rules it out.

## Claim Boundary

Allowed statement:

> The TCCS no-go theorem implies a transfer-curvature object class as the next pre-score candidate.

Forbidden statement:

> The transfer-curvature protocol has produced a Tau signal or authorizes empirical scoring.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
