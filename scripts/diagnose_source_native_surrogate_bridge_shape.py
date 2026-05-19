#!/usr/bin/env python3
"""Diagnose surrogate backreaction bridge failures by shape vs amplitude.

Best-scale diagnostics are reported only to identify whether a mismatch is
mostly amplitude, sign, or shape. They are forbidden for claims and do not
modify locked K2.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ROW_AUDIT = EVIDENCE / "source_native_surrogate_bridge_row_audit.csv"
SCORECARD = EVIDENCE / "source_native_surrogate_bridge_scorecard.csv"

OUT_DIAG = EVIDENCE / "source_native_surrogate_bridge_shape_diagnosis.csv"
OUT_SUMMARY = EVIDENCE / "source_native_surrogate_bridge_shape_summary.csv"
OUT_DOC = DOCS / "source_native_surrogate_bridge_shape_diagnosis.md"

CLAIM_BOUNDARY = "source_native_surrogate_bridge_shape_diagnosis_no_measurement_validation"


def chi2(y: np.ndarray, x: np.ndarray) -> float:
    residual = y - x
    return float(residual @ residual)


def best_scale(y: np.ndarray, x: np.ndarray) -> float:
    den = float(x @ x)
    if den <= 1e-15:
        return float("nan")
    return float((y @ x) / den)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.std(a) <= 0.0 or np.std(b) <= 0.0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def classify(row: dict[str, object]) -> str:
    corr_k2 = float(row["CorrelationSurrogateWithK2"])
    corr_target = float(row["CorrelationSurrogateWithTarget"])
    beta_target = float(row["ForbiddenBestScaleToTarget"])
    beta_k2 = float(row["ForbiddenBestScaleToK2"])
    scaled_improvement = float(row["RawMinusScaledChi2ToTarget"])
    stable_match_target = float(row["StableSignMatchFractionTarget"])
    stable_match_k2 = float(row["StableSignMatchFractionK2"])

    if corr_k2 < 0.0 or beta_k2 < 0.0:
        return "SIGN_OR_SHAPE_MISMATCH_TO_K2"
    if corr_target < 0.0 or beta_target < 0.0:
        return "SIGN_OR_SHAPE_MISMATCH_TO_TARGET"
    if scaled_improvement > 1.0 and stable_match_target >= 0.6:
        return "AMPLITUDE_DOMINATED_TARGET_MISMATCH"
    if corr_k2 >= 0.5 and stable_match_k2 >= 0.6:
        return "K2_LIKE_SHAPE_BUT_TARGET_WEAK"
    return "MIXED_SHAPE_AND_AMPLITUDE_MISMATCH"


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    rows = pd.read_csv(ROW_AUDIT)
    score = pd.read_csv(SCORECARD)
    diag_rows = []

    for (route_id, family_id, sample_id), group in rows.groupby(["RouteID", "FamilyID", "SampleID"]):
        group = group.sort_values("GridIndex")
        target = group["WhitenedTarget"].to_numpy(float)
        k2 = group["K2LockedWhitened"].to_numpy(float)
        surrogate = group["SurrogateBackreactionWhitened"].to_numpy(float)
        stable = group["SignStable"].astype(str).str.lower().eq("true").to_numpy()

        beta_target = best_scale(target, surrogate)
        beta_k2 = best_scale(k2, surrogate)
        scaled_target = beta_target * surrogate
        scaled_k2 = beta_k2 * surrogate
        raw_target_chi2 = chi2(target, surrogate)
        scaled_target_chi2 = chi2(target, scaled_target)
        raw_k2_chi2 = chi2(k2, surrogate)
        scaled_k2_chi2 = chi2(k2, scaled_k2)
        stable_count = int(np.sum(stable))
        stable_target_matches = int(np.sum(np.sign(surrogate[stable]) == np.sign(target[stable])))
        stable_k2_matches = int(np.sum(np.sign(surrogate[stable]) == np.sign(k2[stable])))

        base = {
            "AuditID": "SOURCE_NATIVE_SURROGATE_BRIDGE_SHAPE_DIAGNOSIS_V1",
            "RouteID": route_id,
            "FamilyID": family_id,
            "SampleID": sample_id,
            "Rows": len(group),
            "StableRows": stable_count,
            "RawChi2ToTarget": raw_target_chi2,
            "ForbiddenBestScaleToTarget": beta_target,
            "ForbiddenScaledChi2ToTarget": scaled_target_chi2,
            "RawMinusScaledChi2ToTarget": raw_target_chi2 - scaled_target_chi2,
            "RawChi2ToK2": raw_k2_chi2,
            "ForbiddenBestScaleToK2": beta_k2,
            "ForbiddenScaledChi2ToK2": scaled_k2_chi2,
            "RawMinusScaledChi2ToK2": raw_k2_chi2 - scaled_k2_chi2,
            "CorrelationSurrogateWithTarget": corr(surrogate, target),
            "CorrelationSurrogateWithK2": corr(surrogate, k2),
            "StableSignMatchesTarget": stable_target_matches,
            "StableSignMatchFractionTarget": stable_target_matches / stable_count if stable_count else float("nan"),
            "StableSignMatchesK2": stable_k2_matches,
            "StableSignMatchFractionK2": stable_k2_matches / stable_count if stable_count else float("nan"),
            "LockedK2Changed": False,
            "ScaleFitAllowedForClaims": False,
            "MeasurementValidationAllowed": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
        base["MismatchClass"] = classify(base)
        diag_rows.append(base)

    diag = pd.DataFrame(diag_rows)
    diag = diag.merge(
        score[
            [
                "RouteID",
                "FamilyID",
                "SampleID",
                "SurrogateBackreactionChi2",
                "K1Chi2AgainstTarget",
                "K2Chi2AgainstTarget",
                "DeltaChi2_K2_minus_SurrogateBackreaction",
                "DeltaChi2_K2_minus_K1",
            ]
        ],
        on=["RouteID", "FamilyID", "SampleID"],
        how="left",
    )
    diag.to_csv(OUT_DIAG, index=False)

    class_counts = diag["MismatchClass"].value_counts().to_dict()
    k2_like = diag[diag["MismatchClass"].eq("K2_LIKE_SHAPE_BUT_TARGET_WEAK")]
    amp_like = diag[diag["MismatchClass"].eq("AMPLITUDE_DOMINATED_TARGET_MISMATCH")]
    sign_shape = diag[diag["MismatchClass"].str.contains("SIGN_OR_SHAPE", regex=False)]
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_SURROGATE_BRIDGE_SHAPE_DIAGNOSIS_V1",
                "Cases": len(diag),
                "K2LikeShapeCases": len(k2_like),
                "AmplitudeDominatedCases": len(amp_like),
                "SignOrShapeMismatchCases": len(sign_shape),
                "MedianCorrelationSurrogateWithK2": float(diag["CorrelationSurrogateWithK2"].median()),
                "MedianCorrelationSurrogateWithTarget": float(diag["CorrelationSurrogateWithTarget"].median()),
                "MedianForbiddenBestScaleToK2": float(diag["ForbiddenBestScaleToK2"].median()),
                "MedianForbiddenBestScaleToTarget": float(diag["ForbiddenBestScaleToTarget"].median()),
                "K2BeatsSurrogateCases": int((diag["DeltaChi2_K2_minus_SurrogateBackreaction"] < 0.0).sum()),
                "ClassCounts": ";".join(f"{k}={v}" for k, v in sorted(class_counts.items())),
                "LockedK2Changed": False,
                "ScaleFitAllowedForClaims": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SURROGATE_BRIDGE_MISMATCH_DIAGNOSED_SOURCE_NATIVE_STILL_MISSING",
                "StrongestAllowedClaim": (
                    "surrogate bridge mismatches are diagnosable as shape/amplitude warnings without changing locked K2"
                ),
                "PrimaryResidualRisk": (
                    "surrogate families are not source-native and fitted scale diagnostics are forbidden for claims"
                ),
                "NextAction": "repeat the same shape/amplitude diagnosis on real source-native exports and covariance",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Surrogate Bridge Shape Diagnosis",
                "",
                "Status: surrogate mismatch diagnosed; source-native bridge still missing.",
                "",
                "This diagnostic separates amplitude, sign, and shape mismatch modes. Best-scale values are explicitly forbidden for claims and are used only to understand the failure mode.",
                "",
                "## Result",
                "",
                f"- Cases: {len(diag)}",
                f"- K2-like shape cases: {len(k2_like)}",
                f"- Amplitude-dominated target mismatch cases: {len(amp_like)}",
                f"- Sign/shape mismatch cases: {len(sign_shape)}",
                f"- Median corr(surrogate,K2): {float(diag['CorrelationSurrogateWithK2'].median()):.3f}",
                f"- Median corr(surrogate,target): {float(diag['CorrelationSurrogateWithTarget'].median()):.3f}",
                "",
                "## Outputs",
                "",
                f"- Diagnosis: `{OUT_DIAG.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DIAG}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
