#!/usr/bin/env python3
"""Diagnose clock and family failure modes for the diagonal-orthogonal P-TauCov scorecard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OOS = ROOT / "evidence/p_taucov_diagonal_orthogonal_oos_scorecard.csv"
SUMMARY = ROOT / "evidence/p_taucov_diagonal_orthogonal_scorecard_summary.csv"
OUT_FOLD = ROOT / "evidence/p_taucov_diagonal_orthogonal_failure_fold_diagnostic.csv"
OUT_AGG = ROOT / "evidence/p_taucov_diagonal_orthogonal_failure_aggregate_diagnostic.csv"
OUT_MD = ROOT / "docs/p_taucov_diagonal_orthogonal_failure_diagnostic.md"

AUDIT_ID = "P_TAUCOV_DIAGONAL_ORTHOGONAL_FAILURE_DIAGNOSTIC_v1"
STATUS = "P_TAUCOV_CLOCK_AND_FAMILY_FAILURE_LOCALIZED_NO_NEW_SCORING"


def main() -> int:
    oos = pd.read_csv(OOS)
    summary = pd.read_csv(SUMMARY).iloc[0].to_dict()

    primary = oos[oos["PrimaryOOS"].astype(bool)]
    family = primary[primary["FoldClass"].eq("primary_leave_one_family_out")].copy()
    clock = primary[primary["FoldClass"].eq("primary_contiguous_clock_block")].copy()
    family_clock = oos[oos["FoldClass"].eq("secondary_family_x_clock_block")].copy()

    fold_rows = []
    for frame_name, frame in [
        ("primary_family", family),
        ("primary_clock", clock),
        ("secondary_family_x_clock", family_clock),
    ]:
        for row in frame.itertuples(index=False):
            fold_rows.append(
                {
                    "AuditID": AUDIT_ID,
                    "FoldGroup": frame_name,
                    "FoldID": row.FoldID,
                    "TestFamilies": row.TestFamilies,
                    "TestClockBlocks": row.TestClockBlocks,
                    "SignedS": float(row.SignedS),
                    "Positive": bool(float(row.SignedS) > 0.0),
                }
            )
    fold_diag = pd.DataFrame(fold_rows)
    fold_diag.to_csv(OUT_FOLD, index=False)

    fam_pos = family[family["SignedS"] > 0.0]
    fam_pos_sum = float(fam_pos["SignedS"].sum())
    dominant_family = str(fam_pos.sort_values("SignedS", ascending=False).iloc[0]["TestFamilies"]) if len(fam_pos) else "NONE"
    dominant_family_signed_s = float(fam_pos["SignedS"].max()) if len(fam_pos) else 0.0
    dominant_family_share = float(dominant_family_signed_s / fam_pos_sum) if fam_pos_sum > 0.0 else 1.0

    clock_pos_count = int((clock["SignedS"] > 0.0).sum())
    clock_neg_count = int((clock["SignedS"] < 0.0).sum())
    worst_clock = clock.sort_values("SignedS").iloc[0]
    best_clock = clock.sort_values("SignedS", ascending=False).iloc[0]

    fc_best = family_clock.sort_values("SignedS", ascending=False).iloc[0]
    fc_worst = family_clock.sort_values("SignedS").iloc[0]
    fc_positive = family_clock[family_clock["SignedS"] > 0.0]
    fc_positive_sum = float(fc_positive["SignedS"].sum())
    fc_top_share = float(fc_positive["SignedS"].max() / fc_positive_sum) if fc_positive_sum > 0.0 else 1.0

    aggregate = pd.DataFrame(
        [
            {
                "AuditID": AUDIT_ID,
                "Status": STATUS,
                "PrimarySignedS": float(summary["PrimarySignedS"]),
                "RequiredNullMaxSignedS": float(summary["RequiredNullMaxSignedS"]),
                "PrimaryBeatsNullMax": bool(float(summary["PrimarySignedS"]) > float(summary["RequiredNullMaxSignedS"])),
                "FamilySignedS": float(summary["FamilySignedS"]),
                "ClockSignedS": float(summary["ClockSignedS"]),
                "PositiveFamilyCount": int(summary["PositiveFamilyCount"]),
                "DominantPositiveFamily": dominant_family,
                "DominantPositiveFamilySignedS": dominant_family_signed_s,
                "DominantPositiveFamilyShare": dominant_family_share,
                "ClockPositiveBlockCount": clock_pos_count,
                "ClockNegativeBlockCount": clock_neg_count,
                "WorstClockBlock": str(worst_clock["TestClockBlocks"]),
                "WorstClockSignedS": float(worst_clock["SignedS"]),
                "BestClockBlock": str(best_clock["TestClockBlocks"]),
                "BestClockSignedS": float(best_clock["SignedS"]),
                "BestFamilyClockFold": str(fc_best["FoldID"]),
                "BestFamilyClockSignedS": float(fc_best["SignedS"]),
                "WorstFamilyClockFold": str(fc_worst["FoldID"]),
                "WorstFamilyClockSignedS": float(fc_worst["SignedS"]),
                "PositiveFamilyClockTopShare": fc_top_share,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "NextGate": "predeclared_clock_consistent_family_balanced_support_required",
            }
        ]
    )
    aggregate.to_csv(OUT_AGG, index=False)

    md = f"""# P-TauCov Diagonal-Orthogonal Failure Diagnostic

Audit ID: `{AUDIT_ID}`

Status:

`{STATUS}`

## Diagnostic Result

The diagonal-orthogonal scorecard produced a positive raw primary signed statistic and exceeded the frozen null maximum, but the failure is now localized.

```text
PrimarySignedS = {float(summary["PrimarySignedS"])}
RequiredNullMaxSignedS = {float(summary["RequiredNullMaxSignedS"])}
FamilySignedS = {float(summary["FamilySignedS"])}
ClockSignedS = {float(summary["ClockSignedS"])}
```

## Family Failure

The positive family contribution is concentrated almost entirely in one family:

```text
DominantPositiveFamily = {dominant_family}
DominantPositiveFamilySignedS = {dominant_family_signed_s}
DominantPositiveFamilyShare = {dominant_family_share}
```

This confirms that the scorecard failure is not merely a weak total signal. The signal is too localized in family space to support a Tau-specific global response claim.

## Clock Failure

The clock aggregation also fails:

```text
ClockPositiveBlockCount = {clock_pos_count}
ClockNegativeBlockCount = {clock_neg_count}
WorstClockBlock = {worst_clock["TestClockBlocks"]}
WorstClockSignedS = {float(worst_clock["SignedS"])}
BestClockBlock = {best_clock["TestClockBlocks"]}
BestClockSignedS = {float(best_clock["SignedS"])}
```

The negative clock aggregate means the candidate does not behave like a stable response across the frozen clock-block partition.

## Family x Clock Localization

The strongest secondary family-by-clock cell is:

```text
BestFamilyClockFold = {fc_best["FoldID"]}
BestFamilyClockSignedS = {float(fc_best["SignedS"])}
```

The weakest cell is:

```text
WorstFamilyClockFold = {fc_worst["FoldID"]}
WorstFamilyClockSignedS = {float(fc_worst["SignedS"])}
```

This supports the same conclusion: the candidate contains a localized alignment feature, but not a globally stable Tau-specific covariance response.

## Claim Boundary

This diagnostic does not authorize a new score, a new candidate, or a survival claim.

It only authorizes the following interpretation:

> The diagonal-orthogonal P-TauCov candidate fails because its positive alignment is clock-inconsistent and family-localized.

## Next Gate

Any next candidate must be defined before scoring and must enforce:

- clock-consistent support;
- family-balanced support;
- zero diagonal leakage;
- no reuse of this failure diagnostic as a post-score tuning objective;
- the same null and claim-boundary discipline as the frozen P-TauCov protocol.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
