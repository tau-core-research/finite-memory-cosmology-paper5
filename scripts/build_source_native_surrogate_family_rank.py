#!/usr/bin/env python3
"""Rank surrogate backreaction families for source-native follow-up.

The ranking is diagnostic only. It identifies which surrogate family shapes are
closest to K2/target under the current preflight routes, without selecting a
physical null, fitting a scale, or changing locked K2.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

DIAG = EVIDENCE / "source_native_surrogate_bridge_shape_diagnosis.csv"
OUT_RANK = EVIDENCE / "source_native_surrogate_family_rank.csv"
OUT_SUMMARY = EVIDENCE / "source_native_surrogate_family_rank_summary.csv"
OUT_DOC = DOCS / "source_native_surrogate_family_rank.md"

CLAIM_BOUNDARY = "source_native_surrogate_family_rank_no_measurement_validation"


def minmax_score(values: pd.Series, higher_is_better: bool = True) -> pd.Series:
    vals = values.astype(float)
    lo = float(vals.min())
    hi = float(vals.max())
    if abs(hi - lo) < 1e-12:
        return pd.Series(np.ones(len(vals)), index=values.index)
    scaled = (vals - lo) / (hi - lo)
    return scaled if higher_is_better else 1.0 - scaled


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    diag = pd.read_csv(DIAG)
    grouped = []
    for family_id, group in diag.groupby("FamilyID"):
        k2_like_cases = int(group["MismatchClass"].eq("K2_LIKE_SHAPE_BUT_TARGET_WEAK").sum())
        amp_cases = int(group["MismatchClass"].eq("AMPLITUDE_DOMINATED_TARGET_MISMATCH").sum())
        sign_shape_cases = int(group["MismatchClass"].str.contains("SIGN_OR_SHAPE", regex=False).sum())
        mixed_cases = int(group["MismatchClass"].eq("MIXED_SHAPE_AND_AMPLITUDE_MISMATCH").sum())
        grouped.append(
            {
                "FamilyID": family_id,
                "Routes": group["RouteID"].nunique(),
                "Cases": len(group),
                "MeanCorrelationWithK2": float(group["CorrelationSurrogateWithK2"].mean()),
                "MedianCorrelationWithK2": float(group["CorrelationSurrogateWithK2"].median()),
                "MeanCorrelationWithTarget": float(group["CorrelationSurrogateWithTarget"].mean()),
                "MedianCorrelationWithTarget": float(group["CorrelationSurrogateWithTarget"].median()),
                "MeanRawChi2ToTarget": float(group["RawChi2ToTarget"].mean()),
                "MeanRawChi2ToK2": float(group["RawChi2ToK2"].mean()),
                "MeanDeltaChi2_K2_minus_Surrogate": float(group["DeltaChi2_K2_minus_SurrogateBackreaction"].mean()),
                "K2BeatsSurrogateCases": int((group["DeltaChi2_K2_minus_SurrogateBackreaction"] < 0.0).sum()),
                "MeanStableSignFractionTarget": float(group["StableSignMatchFractionTarget"].mean()),
                "MeanStableSignFractionK2": float(group["StableSignMatchFractionK2"].mean()),
                "K2LikeShapeCases": k2_like_cases,
                "AmplitudeDominatedCases": amp_cases,
                "SignOrShapeMismatchCases": sign_shape_cases,
                "MixedMismatchCases": mixed_cases,
            }
        )

    rank = pd.DataFrame(grouped)
    rank["K2ShapeScore"] = minmax_score(rank["MeanCorrelationWithK2"], higher_is_better=True)
    rank["TargetShapeScore"] = minmax_score(rank["MeanCorrelationWithTarget"], higher_is_better=True)
    rank["K2DistanceScore"] = minmax_score(rank["MeanRawChi2ToK2"], higher_is_better=False)
    rank["TargetDistanceScore"] = minmax_score(rank["MeanRawChi2ToTarget"], higher_is_better=False)
    rank["StableSignK2Score"] = minmax_score(rank["MeanStableSignFractionK2"], higher_is_better=True)
    rank["PenaltySignShapeMismatch"] = rank["SignOrShapeMismatchCases"] / rank["Cases"]
    rank["DiagnosticCompositeScore"] = (
        0.30 * rank["K2ShapeScore"]
        + 0.20 * rank["TargetShapeScore"]
        + 0.20 * rank["K2DistanceScore"]
        + 0.10 * rank["TargetDistanceScore"]
        + 0.10 * rank["StableSignK2Score"]
        + 0.10 * (1.0 - rank["PenaltySignShapeMismatch"])
    )
    rank = rank.sort_values(["DiagnosticCompositeScore", "MeanCorrelationWithK2"], ascending=[False, False]).reset_index(drop=True)
    rank["DiagnosticRank"] = np.arange(1, len(rank) + 1)
    rank["LockedK2Changed"] = False
    rank["ScaleFitAllowedForClaims"] = False
    rank["MeasurementValidationAllowed"] = False
    rank["ClaimBoundary"] = CLAIM_BOUNDARY
    rank.to_csv(OUT_RANK, index=False)

    top = rank.iloc[0]
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_SURROGATE_FAMILY_RANK_V1",
                "FamiliesRanked": len(rank),
                "TopFamilyID": top["FamilyID"],
                "TopFamilyCompositeScore": float(top["DiagnosticCompositeScore"]),
                "TopFamilyMeanCorrelationWithK2": float(top["MeanCorrelationWithK2"]),
                "TopFamilyMeanCorrelationWithTarget": float(top["MeanCorrelationWithTarget"]),
                "TopFamilyK2BeatsSurrogateCases": int(top["K2BeatsSurrogateCases"]),
                "FamiliesWithPositiveMeanK2Correlation": int((rank["MeanCorrelationWithK2"] > 0.0).sum()),
                "FamiliesWithSignOrShapeMismatch": int((rank["SignOrShapeMismatchCases"] > 0).sum()),
                "LockedK2Changed": False,
                "ScaleFitAllowedForClaims": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SURROGATE_FAMILY_RANK_READY_SOURCE_NATIVE_FOLLOWUP_PRIORITIZED",
                "StrongestAllowedClaim": (
                    "surrogate families can be prioritized for source-native follow-up by shape and sign diagnostics"
                ),
                "PrimaryResidualRisk": (
                    "surrogate ranking is not a physical-null selection rule and cannot replace source-native exports"
                ),
                "NextAction": (
                    "use the ranked family diagnostics to check whether future source-native exports resemble K2-like or mismatch-like surrogate classes"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Surrogate Family Rank",
                "",
                "Status: surrogate follow-up ranking ready.",
                "",
                "This diagnostic ranks surrogate backreaction families by K2/target shape agreement and stable-sign behavior. It is not a source-native physical-null selection rule.",
                "",
                "## Result",
                "",
                f"- Families ranked: {len(rank)}",
                f"- Top surrogate family: `{top['FamilyID']}`",
                f"- Top mean corr(surrogate,K2): {float(top['MeanCorrelationWithK2']):.3f}",
                f"- Top mean corr(surrogate,target): {float(top['MeanCorrelationWithTarget']):.3f}",
                "",
                "## Outputs",
                "",
                f"- Rank table: `{OUT_RANK.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_RANK}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
