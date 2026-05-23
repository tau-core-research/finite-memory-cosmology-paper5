#!/usr/bin/env python3
"""Build the P-TauCov linear model packet schema.

The schema defines the files and hashes required before the prescore evaluator
may compute linear specificity metrics.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_linear_model_packet_schema.md"
OUT_CSV = EVIDENCE / "p_taucov_linear_model_packet_schema.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_linear_model_packet_schema_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
SCHEMA_ID = "P_TAUCOV_LINEAR_MODEL_PACKET_SCHEMA_v1"
CLAIM_BOUNDARY = "linear_model_packet_schema_tracks_packet_presence_no_scoring"

ROWS = [
    ("L0_B", "matrix", "linear branch relaxation operator", "data/p_taucov/linear/L0_B.csv"),
    ("R_B", "matrix", "parent perturbation to branch forcing operator", "data/p_taucov/linear/R_B.csv"),
    ("P_red", "matrix", "projector onto invertible reduced branch domain", "data/p_taucov/linear/P_red.csv"),
    ("A_Phi", "matrix", "parent perturbation to morphology map", "data/p_taucov/linear/A_Phi.csv"),
    ("A_B", "matrix", "branch state to morphology map", "data/p_taucov/linear/A_B.csv"),
    ("P0", "matrix", "fixed projection morphology map for epsilon_P=0", "data/p_taucov/linear/P0.csv"),
    ("coordinate_basis", "table", "frozen observable/source coordinate basis", "data/p_taucov/linear/coordinate_basis.csv"),
    ("packet_manifest", "yaml", "hash manifest for all packet inputs", "evidence/p_taucov_linear_model_packet.yaml"),
    ("packet_sha256", "sha256", "sha256 of packet manifest", "evidence/p_taucov_linear_model_packet.sha256"),
    ("leakage_audit", "csv", "audit that packet inputs exclude target residuals and P5C v3 outcomes", "evidence/p_taucov_linear_model_packet_leakage_audit.csv"),
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SchemaID": SCHEMA_ID,
                "ObjectID": obj,
                "ObjectType": obj_type,
                "Role": role,
                "RequiredPath": path,
                "RequiredBeforeMetricEvaluation": True,
                "PresentNow": (ROOT / path).exists(),
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for obj, obj_type, role, path in ROWS
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    present = int(df["PresentNow"].astype(bool).sum())
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SchemaID": SCHEMA_ID,
                "RequiredObjects": len(df),
                "PresentObjects": present,
                "MissingObjects": len(df) - present,
                "PacketReady": present == len(df),
                "MetricEvaluationAuthorized": present == len(df),
                "LinearCandidateFrozen": present == len(df),
                "PTauCovScoringAuthorized": False,
                "NextStep": "run_linear_specificity_audit" if present == len(df) else "create_target_blind_packet_files_and_hash_manifest",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Linear Model Packet Schema

Status: packet schema / tracks packet-file presence / no scoring
authorization.

The prescore evaluator requires a concrete target-blind linear model packet
before it can evaluate the linear specificity metrics. This schema defines the
required files. It does not by itself create scoring authorization.

## Required Packet Files

| Object | Required path | Role |
| --- | --- | --- |
| `L0_B` | `data/p_taucov/linear/L0_B.csv` | linear branch relaxation operator |
| `R_B` | `data/p_taucov/linear/R_B.csv` | parent perturbation to branch forcing operator |
| `P_red` | `data/p_taucov/linear/P_red.csv` | projector onto invertible reduced branch domain |
| `A_Phi` | `data/p_taucov/linear/A_Phi.csv` | parent perturbation to morphology map |
| `A_B` | `data/p_taucov/linear/A_B.csv` | branch state to morphology map |
| `P0` | `data/p_taucov/linear/P0.csv` | fixed projection morphology map for `epsilon_P=0` |
| `coordinate_basis` | `data/p_taucov/linear/coordinate_basis.csv` | frozen observable/source coordinate basis |
| `packet_manifest` | `evidence/p_taucov_linear_model_packet.yaml` | hash manifest |
| `packet_sha256` | `evidence/p_taucov_linear_model_packet.sha256` | manifest hash |
| `leakage_audit` | `evidence/p_taucov_linear_model_packet_leakage_audit.csv` | no outcome leakage audit |

## Required Manifest Claims

The future manifest must state:

```text
lambda_B: 0
epsilon_P: 0
uses_target_residuals: false
uses_p5c_v3_outcome: false
metric_evaluation_authorized: true or false
p_taucov_scoring_authorized: false
```

## Boundary

Allowed statement:

```text
The required target-blind linear model packet schema is declared.
```

Forbidden statement:

```text
The linear model packet has passed the specificity audit or produced a
P-TauCov score.
```
""",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DOC}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
