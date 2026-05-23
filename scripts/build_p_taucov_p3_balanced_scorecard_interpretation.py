#!/usr/bin/env python3
"""Build interpretation artifact for the P3 balanced scorecard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_scorecard_summary.csv"
NULLS = ROOT / "evidence/p_taucov_p3_balanced_null_scorecard.csv"
OOS = ROOT / "evidence/p_taucov_p3_balanced_oos_scorecard.csv"
OUT_CSV = ROOT / "evidence/p_taucov_p3_balanced_scorecard_interpretation.csv"
OUT_MD = ROOT / "docs/p_taucov_p3_balanced_scorecard_interpretation.md"

AUDIT_ID = "P_TAUCOV_P3_BALANCED_SCORECARD_INTERPRETATION_v1"
STATUS = "P_TAUCOV_P3_BALANCED_NEGATIVE_ALIGNMENT_RESULT_NO_SURVIVAL_CLAIM"


def main() -> int:
    summary = pd.read_csv(SUMMARY).iloc[0]
    nulls = pd.read_csv(NULLS)
    oos = pd.read_csv(OOS)
    primary = oos[oos["PrimaryOOS"].astype(bool)]
    family = primary[primary["FoldClass"].eq("primary_leave_one_family_out")]
    clock = primary[primary["FoldClass"].eq("primary_contiguous_clock_block")]
    strongest_null = nulls.sort_values("PrimarySignedS", ascending=False).iloc[0]
    pd.DataFrame(
        [
            {
                "AuditID": AUDIT_ID,
                "Status": STATUS,
                "ScorecardStatus": summary["Status"],
                "PrimarySignedS": float(summary["PrimarySignedS"]),
                "FamilySignedS": float(summary["FamilySignedS"]),
                "ClockSignedS": float(summary["ClockSignedS"]),
                "RequiredNullMaxSignedS": float(summary["RequiredNullMaxSignedS"]),
                "StrongestNullID": strongest_null["NullID"],
                "PositiveFamilyCount": int(summary["PositiveFamilyCount"]),
                "MaxPositiveFamilyShare": float(summary["MaxPositiveFamilyShare"]),
                "FamilyRows": int(len(family)),
                "ClockRows": int(len(clock)),
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "Interpretation": "balanced_p3_removes_local_positive_anomaly_and_returns_negative_primary_alignment",
            }
        ]
    ).to_csv(OUT_CSV, index=False)
    OUT_MD.write_text(
        f"""# P-TauCov P3 Balanced Scorecard Interpretation

Audit ID: `{AUDIT_ID}`

Status:

`{STATUS}`

## Result

The P3 balanced scorecard was authorized and run under the frozen signed-alignment policy.

```text
PrimarySignedS = {float(summary["PrimarySignedS"])}
FamilySignedS = {float(summary["FamilySignedS"])}
ClockSignedS = {float(summary["ClockSignedS"])}
RequiredNullMaxSignedS = {float(summary["RequiredNullMaxSignedS"])}
StrongestNullID = {strongest_null["NullID"]}
PositiveFamilyCount = {int(summary["PositiveFamilyCount"])}
MaxPositiveFamilyShare = {float(summary["MaxPositiveFamilyShare"])}
```

## Interpretation

This is a negative result.

After family/clock balance projection and structural-null filtering, the P3 object does not produce a positive primary signed alignment. The primary statistic is negative, and the sign-flip orientation control is the strongest positive null.

This means the earlier local positive anomaly does not survive the stricter P3 balanced route.

## Claim Boundary

Allowed statement:

> The P3 balanced signed-alignment scorecard was run and failed; the result is a negative alignment result.

Forbidden statement:

> The P3 balanced scorecard validates Tau Core, authorizes a survival claim, or establishes a physical covariance response.

## Next Scientific Consequence

The current P-TauCov path should not be escalated as evidence. The useful result is methodological: the stricter balance projector removes the previous local anomaly, suggesting that any future Tau-specific route needs a genuinely new parent-derived response structure rather than another post-hoc support refinement.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
