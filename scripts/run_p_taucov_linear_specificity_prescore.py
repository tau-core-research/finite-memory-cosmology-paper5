#!/usr/bin/env python3
"""Run or block the P-TauCov linear specificity prescore audit.

This script is intentionally conservative. It only evaluates metrics if a
concrete target-blind linear model packet is present. Otherwise it writes a
blocked audit artifact and authorizes nothing.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"
MODEL_PACKET = EVIDENCE / "p_taucov_linear_model_packet.yaml"
THRESHOLDS = EVIDENCE / "p_taucov_linear_specificity_threshold_freeze.csv"
METRICS = EVIDENCE / "p_taucov_linear_specificity_metric_registry.csv"

OUT_DOC = DOCS / "p_taucov_linear_specificity_prescore.md"
OUT_CSV = EVIDENCE / "p_taucov_linear_specificity_prescore.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_linear_specificity_prescore_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_LINEAR_SPECIFICITY_AUDIT_v1"
RUN_ID = "P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_RUN_v1"
CLAIM_BOUNDARY = "linear_specificity_prescore_blocked_until_model_packet_exists"


def write_blocked(reason: str) -> int:
    metrics = pd.read_csv(METRICS) if METRICS.exists() else pd.DataFrame()
    metric_ids = list(metrics["MetricID"]) if "MetricID" in metrics.columns else []
    rows = []
    for metric_id in metric_ids:
        rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "RunID": RUN_ID,
                "MetricID": metric_id,
                "MetricValue": "NOT_EVALUATED",
                "Pass": False,
                "Status": "BLOCKED",
                "BlockReason": reason,
                "UsesTargetResiduals": False,
                "UsesP5Cv3Outcome": False,
                "LinearCandidateFrozen": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    if not rows:
        rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "RunID": RUN_ID,
                "MetricID": "NO_METRICS_LOADED",
                "MetricValue": "NOT_EVALUATED",
                "Pass": False,
                "Status": "BLOCKED",
                "BlockReason": reason,
                "UsesTargetResiduals": False,
                "UsesP5Cv3Outcome": False,
                "LinearCandidateFrozen": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "RunID": RUN_ID,
                "Status": "BLOCKED",
                "BlockReason": reason,
                "MetricsEvaluated": False,
                "MetricsPassed": "0/6",
                "LinearCandidateFrozen": False,
                "DeltaCTauGenerated": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "create_target_blind_linear_model_packet",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        f"""# P-TauCov Linear Specificity Prescore

Status: blocked / no metric evaluation / no linear freeze / no scoring
authorization.

The prescore evaluator was invoked, but it did not evaluate the linear
specificity metrics.

## Block Reason

```text
{reason}
```

## Required Missing Artifact

```text
evidence/p_taucov_linear_model_packet.yaml
```

That packet must contain concrete target-blind matrices/operators for the
strictly linear candidate:

```text
L0_B
R_B
P_red
A_Phi
A_B
P0
observable coordinate basis
input provenance hashes
```

## Current Boundary

```text
LinearCandidateFrozen: false
DeltaCTauGenerated: false
PTauCovScoringAuthorized: false
```

Allowed statement:

```text
The prescore evaluator exists and correctly blocks without a target-blind linear
model packet.
```

Forbidden statement:

```text
The strictly linear candidate passed the specificity audit.
```
""",
        encoding="utf-8",
    )
    print("P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_BLOCKED")
    return 0


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    if not THRESHOLDS.exists():
        return write_blocked("missing_threshold_freeze")
    if not METRICS.exists():
        return write_blocked("missing_metric_registry")
    if not MODEL_PACKET.exists():
        return write_blocked("missing_target_blind_linear_model_packet")

    return write_blocked("evaluation_not_implemented_for_model_packet_yet")


if __name__ == "__main__":
    raise SystemExit(main())
