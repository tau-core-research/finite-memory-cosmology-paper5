#!/usr/bin/env python3
"""Freeze prescore thresholds for the P-TauCov linear specificity audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_linear_specificity_threshold_freeze.md"
OUT_CSV = EVIDENCE / "p_taucov_linear_specificity_threshold_freeze.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_linear_specificity_threshold_freeze_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_LINEAR_SPECIFICITY_AUDIT_v1"
FREEZE_ID = "P_TAUCOV_LINEAR_SPECIFICITY_THRESHOLD_FREEZE_v1"
CLAIM_BOUNDARY = "linear_specificity_threshold_freeze_no_metric_evaluation_no_scoring"


ROWS = [
    {
        "MetricID": "M1_NONCOMMUTATOR_SHARE",
        "FrozenThreshold": ">=0.10",
        "Reason": "requires nontrivial branch-projection noncommutativity",
        "FailureMeaning": "linear candidate collapses toward commuting morphology",
    },
    {
        "MetricID": "M2_EFFECTIVE_RANK",
        "FrozenThreshold": "0.10<=effective_rank_fraction<=0.85",
        "Reason": "rejects rank-1/diagonal collapse and full generic covariance spread",
        "FailureMeaning": "linear candidate is either too concentrated or too generic",
    },
    {
        "MetricID": "M3_SUPPORT_ENTROPY",
        "FrozenThreshold": "0.25<=normalized_entropy<=0.85",
        "Reason": "rejects single-family proxy and uniform-noise support",
        "FailureMeaning": "predicted support is too localized without theory or too diffuse",
    },
    {
        "MetricID": "M4_LABEL_PROXY_OVERLAP",
        "FrozenThreshold": "<=0.35",
        "Reason": "prevents support from being a known family/clock-label proxy",
        "FailureMeaning": "linear candidate inherits labels rather than Tau structure",
    },
    {
        "MetricID": "M5_NULL_SEPARATION_MARGIN",
        "FrozenThreshold": ">0_against_each_declared_prescore_null_and_>=0.05_against_strongest_null",
        "Reason": "requires structural separation from generic linear nulls",
        "FailureMeaning": "generic linear nulls are as specific as the candidate",
    },
    {
        "MetricID": "M6_OUTCOME_LEAKAGE_CERTIFICATE",
        "FrozenThreshold": "must_be_true",
        "Reason": "all metrics are invalid if target residuals or P5C v3 outcomes leak in",
        "FailureMeaning": "audit is contaminated and cannot support a freeze",
    },
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "FreezeID": FREEZE_ID,
                **row,
                "ThresholdFrozenBeforeEvaluation": True,
                "MetricEvaluated": False,
                "LinearCandidateFrozen": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in ROWS
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "FreezeID": FREEZE_ID,
                "ThresholdsDeclared": len(df),
                "MetricsEvaluated": False,
                "LinearCandidateFrozen": False,
                "DeltaCTauGenerated": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "evaluate_prescore_metrics_or_reject_threshold_policy",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Linear Specificity Threshold Freeze

Status: threshold freeze / no metric evaluation / no linear freeze / no
scoring authorization.

This artifact freezes the prescore thresholds for
`P_TAUCOV_LINEAR_SPECIFICITY_AUDIT_v1`. The thresholds are declared before any
linear-specificity metric is evaluated and before any `delta_C_Tau` matrix is
generated.

## Frozen Thresholds

| Metric | Frozen threshold | Failure meaning |
| --- | --- | --- |
| `M1_NONCOMMUTATOR_SHARE` | `>=0.10` | Candidate collapses toward commuting morphology. |
| `M2_EFFECTIVE_RANK` | `0.10 <= effective_rank_fraction <= 0.85` | Candidate is rank/diagonal collapse or fully generic spread. |
| `M3_SUPPORT_ENTROPY` | `0.25 <= normalized_entropy <= 0.85` | Support is single-family proxy or uniform-noise-like. |
| `M4_LABEL_PROXY_OVERLAP` | `<=0.35` | Support is too close to known family/clock labels. |
| `M5_NULL_SEPARATION_MARGIN` | `>0` against each null and `>=0.05` against strongest null | Generic linear nulls are as specific as candidate. |
| `M6_OUTCOME_LEAKAGE_CERTIFICATE` | `must_be_true` | Outcome leakage contaminates the audit. |

## Decision Rule

The strictly linear candidate can advance to a concrete freeze only if all
thresholds pass. Failing any threshold blocks the strictly linear freeze and
routes the program to either rejection or a separately frozen minimal nonzero
term:

```text
lambda_B fixed nonzero
or epsilon_P fixed nonzero
```

## Claim Boundary

Allowed statement:

```text
The linear-specificity thresholds are frozen before metric evaluation.
```

Forbidden statement:

```text
The frozen thresholds show that the strictly linear candidate passes.
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
