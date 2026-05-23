#!/usr/bin/env python3
"""Freeze scoring policy for the P3 balanced object without authorizing scoring."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "p3_balanced_manifest": ROOT / "evidence/p_taucov_p3_balanced_final_manifest_summary.csv",
    "p3_structural_null_audit": ROOT / "evidence/p_taucov_p3_balanced_structural_null_audit_summary.csv",
    "signed_statistic": ROOT / "evidence/p_taucov_signed_response_statistic_summary.csv",
    "signed_null_policy": ROOT / "evidence/p_taucov_signed_response_null_policy_summary.csv",
    "signed_aggregation_policy": ROOT / "evidence/p_taucov_signed_response_aggregation_policy_summary.csv",
}
MATRIX = ROOT / "evidence/p_taucov_p3_balanced_preflight_matrix.csv"
OUT_YAML = ROOT / "evidence/p_taucov_p3_balanced_scoring_policy.yaml"
OUT_SHA = ROOT / "evidence/p_taucov_p3_balanced_scoring_policy.sha256"
OUT_SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_scoring_policy_summary.csv"
OUT_DOC = ROOT / "docs/p_taucov_p3_balanced_scoring_policy.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_P3_BALANCED_SCORING_POLICY_FREEZE_v1"
STATUS = "P_TAUCOV_P3_BALANCED_SCORING_POLICY_FROZEN_NO_SCORING"
CLAIM_BOUNDARY = "p3_balanced_scoring_policy_freeze_no_scoring"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    df = pd.read_csv(path)
    return str(df.iloc[0]["Status"]) if "Status" in df.columns else "NO_STATUS_COLUMN"


def main() -> int:
    required = {
        "p3_balanced_manifest": "P_TAUCOV_P3_BALANCED_OBJECT_FROZEN_NO_SCORING_AUTHORIZATION",
        "p3_structural_null_audit": "P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_PASS_NO_SCORING",
        "signed_statistic": "P_TAUCOV_SIGNED_RESPONSE_STATISTIC_FROZEN_NO_SCORING",
        "signed_null_policy": "P_TAUCOV_SIGNED_RESPONSE_NULL_POLICY_FROZEN_NO_SCORING",
        "signed_aggregation_policy": "P_TAUCOV_SIGNED_RESPONSE_AGGREGATION_POLICY_FROZEN_NO_SCORING",
    }
    observed = {key: status(path) for key, path in INPUTS.items()}
    ok = all(observed.get(key) == value for key, value in required.items()) and MATRIX.exists()
    policy = {
        "ProtocolID": PROTOCOL_ID,
        "FreezeID": FREEZE_ID,
        "Status": STATUS if ok else "P_TAUCOV_P3_BALANCED_SCORING_POLICY_BLOCKED_NO_SCORING",
        "PrimaryStatistic": "trace((rrT/sigma2-I)K_p3_balanced)",
        "PrimaryObject": "P3_BALANCED_PREFLIGHT_OFFDIAGONAL_OBJECT",
        "PrimaryObjectFile": str(MATRIX.relative_to(ROOT)),
        "PrimaryObjectSHA256": sha256(MATRIX) if MATRIX.exists() else "MISSING",
        "PolicyInputs": {key: str(path.relative_to(ROOT)) for key, path in INPUTS.items()},
        "PolicyInputStatus": observed,
        "PolicyInputSHA256": {key: sha256(path) for key, path in INPUTS.items() if path.exists()},
        "RequiredNullFamilies": [
            "sign_flip_orientation_control",
            "row_reverse",
            "clock_phase_shift",
            "family_cycle",
            "support_shuffle",
            "random_symmetric_offdiagonal",
            "signed_response_policy_nulls",
        ],
        "RequiredAggregationGates": [
            "primary_oos_positive",
            "required_null_max_beaten",
            "family_aggregate_positive",
            "clock_aggregate_positive",
            "positive_family_count_at_least_2",
            "max_positive_family_share_at_most_0_5",
        ],
        "ScoringAuthorized": False,
        "SurvivalClaimAuthorized": False,
        "TauCoreValidationClaimAuthorized": False,
        "MeasurementValidationAllowed": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    OUT_YAML.write_text(yaml.safe_dump(policy, sort_keys=False), encoding="utf-8")
    OUT_SHA.write_text(f"{sha256(OUT_YAML)}  {OUT_YAML.relative_to(ROOT)}\n", encoding="utf-8")
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": policy["Status"],
                "PrimaryStatistic": policy["PrimaryStatistic"],
                "RequiredNullFamilies": len(policy["RequiredNullFamilies"]),
                "RequiredAggregationGates": len(policy["RequiredAggregationGates"]),
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    OUT_DOC.write_text(
        f"""# P-TauCov P3 Balanced Scoring Policy Freeze

Freeze ID: `{FREEZE_ID}`

Status:

`{policy["Status"]}`

## Scope

This freezes the policy that would govern any later P3 balanced signed-alignment scorecard.

It does not authorize scoring.

## Primary Statistic

```text
{policy["PrimaryStatistic"]}
```

## Required Gates

- primary OOS signed statistic must be positive;
- primary OOS signed statistic must beat the required null maximum;
- family aggregate must be positive;
- clock aggregate must be positive;
- at least two families must contribute positively;
- maximum positive-family share must be at most 0.5.

## Claim Boundary

Allowed statement:

> A scoring policy has been frozen for the P3 balanced object.

Forbidden statement:

> The P3 balanced object is authorized for scoring, has survived scoring, or validates Tau Core.
""",
        encoding="utf-8",
    )
    print(policy["Status"])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
