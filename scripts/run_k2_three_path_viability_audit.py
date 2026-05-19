#!/usr/bin/env python3
"""Compare three K2 amplitude-gap explanations.

Paths:
1. normalization gap: y ~= s*K2
2. source-coherent residual mode: y ~= s*K2 + c
3. depth-zone viability: K2 is only expected to be strong at larger depth

This is a diagnostic preflight. It does not change the locked K2 kernel, does
not allow rho>4, and does not fit a new K1 baseline.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

DECOMP = EVIDENCE / "k2_residual_decomposition.csv"
OUT_MODELS = EVIDENCE / "k2_three_path_model_audit.csv"
OUT_ZONES = EVIDENCE / "k2_three_path_zone_audit.csv"
OUT_SUMMARY = EVIDENCE / "k2_three_path_viability_summary.csv"


def rms(v: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(v, dtype=float) ** 2)))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(a, b) / denom)


def chi2_diag(y: np.ndarray, m: np.ndarray, sigma: np.ndarray) -> float:
    usable = np.isfinite(y) & np.isfinite(m) & np.isfinite(sigma) & (sigma > 0.0)
    if not np.any(usable):
        return float("nan")
    r = (y[usable] - m[usable]) / sigma[usable]
    return float(np.dot(r, r))


def aic(chi2: float, k: int) -> float:
    return float(chi2 + 2 * k)


def bic(chi2: float, k: int, n: int) -> float:
    return float(chi2 + k * np.log(n))


def fit_scale(y: np.ndarray, k2: np.ndarray) -> float:
    denom = float(np.dot(k2, k2))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(k2, y) / denom)


def fit_scale_offset(y: np.ndarray, k2: np.ndarray) -> tuple[float, float]:
    design = np.column_stack([k2, np.ones_like(k2)])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    return float(beta[0]), float(beta[1])


def model_row(
    path_id: str,
    subset: str,
    y: np.ndarray,
    k2: np.ndarray,
    sigma: np.ndarray,
    pred: np.ndarray,
    parameter_count: int,
    scale: float | None = None,
    offset: float | None = None,
) -> dict[str, object]:
    c2 = chi2_diag(y, pred, sigma)
    return {
        "PathID": path_id,
        "Subset": subset,
        "Rows": len(y),
        "ParameterCount": parameter_count,
        "Scale": scale,
        "CoherentOffset": offset,
        "TargetRMS": rms(y),
        "PredictionRMS": rms(pred),
        "PredictionToTargetRMSRatio": rms(pred) / rms(y) if rms(y) > 0.0 else float("nan"),
        "ResidualRMS": rms(y - pred),
        "CosineTargetVsPrediction": cosine(y, pred),
        "Chi2DiagProxy": c2,
        "AIC": aic(c2, parameter_count),
        "BIC": bic(c2, parameter_count, len(y)),
        "ClaimBoundary": "three_path_viability_preflight_no_measurement_validation",
    }


def summarize_subset(df: pd.DataFrame, subset: str) -> list[dict[str, object]]:
    y = df["SourceSplitResponse"].to_numpy(float)
    y_after = df["ResidualAfterAlpha"].to_numpy(float)
    k2 = df["K2LockedRho4"].to_numpy(float)
    sigma = df["SigmaDiagProxy"].to_numpy(float)

    rows: list[dict[str, object]] = []
    rows.append(model_row("LOCKED_K2_RHO4", subset, y, k2, sigma, k2, 0, scale=1.0))

    s = fit_scale(y, k2)
    rows.append(model_row("NORMALIZATION_SCALE_ONLY", subset, y, k2, sigma, s * k2, 1, scale=s))

    s2, c = fit_scale_offset(y, k2)
    rows.append(model_row("SOURCE_COHERENT_SCALE_PLUS_OFFSET", subset, y, k2, sigma, s2 * k2 + c, 2, scale=s2, offset=c))

    s_after = fit_scale(y_after, k2)
    rows.append(
        model_row("AFTER_ALPHA_NORMALIZATION_SCALE_ONLY", subset, y_after, k2, sigma, s_after * k2, 1, scale=s_after)
    )

    s2_after, c_after = fit_scale_offset(y_after, k2)
    rows.append(
        model_row(
            "AFTER_ALPHA_SOURCE_COHERENT_SCALE_PLUS_OFFSET",
            subset,
            y_after,
            k2,
            sigma,
            s2_after * k2 + c_after,
            2,
            scale=s2_after,
            offset=c_after,
        )
    )
    return rows


def viability_label(row: pd.Series) -> str:
    if row["PathID"] == "NORMALIZATION_SCALE_ONLY":
        scale = abs(float(row["Scale"]))
        if 2.0 <= scale <= 8.0 and row["CosineTargetVsPrediction"] > 0.75:
            return "viable_if_normalization_source_is_derived"
        return "weak_or_unstable_normalization"
    if row["PathID"] == "SOURCE_COHERENT_SCALE_PLUS_OFFSET":
        if row["AIC"] < row["LockedK2AIC"] and row["ResidualRMS"] < row["LockedK2ResidualRMS"]:
            return "viable_but_needs_tau_core_offset_derivation"
        return "not_preferred_over_locked_k2"
    if row["PathID"] == "LOCKED_K2_RHO4":
        if row["PredictionToTargetRMSRatio"] > 0.4 and row["CosineTargetVsPrediction"] > 0.9:
            return "strong_at_this_depth_subset"
        return "directional_backbone_not_full_amplitude"
    return "diagnostic_control"


def main() -> None:
    df = pd.read_csv(DECOMP)
    stable = df["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"])

    subsets: list[tuple[str, pd.DataFrame]] = [
        ("all_points", df),
        ("sign_stable_only", df[stable]),
        ("low_depth", df[df["DepthBin"] == "low_depth"]),
        ("mid_depth", df[df["DepthBin"] == "mid_depth"]),
        ("high_depth", df[df["DepthBin"] == "high_depth"]),
    ]

    model_rows: list[dict[str, object]] = []
    for subset, sub in subsets:
        if len(sub) >= 2:
            model_rows.extend(summarize_subset(sub, subset))

    models = pd.DataFrame(model_rows)
    locked_lookup = models[models["PathID"] == "LOCKED_K2_RHO4"][
        ["Subset", "AIC", "BIC", "ResidualRMS"]
    ].rename(columns={"AIC": "LockedK2AIC", "BIC": "LockedK2BIC", "ResidualRMS": "LockedK2ResidualRMS"})
    models = models.merge(locked_lookup, on="Subset", how="left")
    models["DeltaAICVsLockedK2"] = models["AIC"] - models["LockedK2AIC"]
    models["DeltaBICVsLockedK2"] = models["BIC"] - models["LockedK2BIC"]
    models["ViabilityLabel"] = models.apply(viability_label, axis=1)
    models.to_csv(OUT_MODELS, index=False)

    zone_rows: list[dict[str, object]] = []
    for zone in ["low_depth", "mid_depth", "high_depth"]:
        zdf = df[df["DepthBin"] == zone]
        if zdf.empty:
            continue
        zone_rows.append(
            {
                "DepthBin": zone,
                "Rows": len(zdf),
                "MeanX": float(zdf["x_coordinate"].mean()),
                "TargetRMS": rms(zdf["SourceSplitResponse"].to_numpy(float)),
                "K2RMS": rms(zdf["K2LockedRho4"].to_numpy(float)),
                "K2ToTargetRMSRatio": rms(zdf["K2LockedRho4"].to_numpy(float))
                / rms(zdf["SourceSplitResponse"].to_numpy(float)),
                "CosineTargetVsK2": cosine(
                    zdf["SourceSplitResponse"].to_numpy(float), zdf["K2LockedRho4"].to_numpy(float)
                ),
                "MeanExplainedFractionProxy": float(zdf["K2ExplainedFractionProxy"].mean()),
                "DepthPathInterpretation": "k2_strengthens_with_depth"
                if zone != "low_depth"
                else "k2_expected_to_be_weak_at_low_depth",
                "ClaimBoundary": "three_path_viability_preflight_no_measurement_validation",
            }
        )
    pd.DataFrame(zone_rows).to_csv(OUT_ZONES, index=False)

    best_by_subset = models.sort_values(["Subset", "AIC"]).groupby("Subset", as_index=False).first()
    path_counts = best_by_subset["PathID"].value_counts().to_dict()
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "K2_THREE_PATH_VIABILITY_SUMMARY",
                "BestAICPathCounts": path_counts,
                "NormalizationScaleAllPoints": float(
                    models[(models["Subset"] == "all_points") & (models["PathID"] == "NORMALIZATION_SCALE_ONLY")][
                        "Scale"
                    ].iloc[0]
                ),
                "CoherentOffsetAllPoints": float(
                    models[
                        (models["Subset"] == "all_points")
                        & (models["PathID"] == "SOURCE_COHERENT_SCALE_PLUS_OFFSET")
                    ]["CoherentOffset"].iloc[0]
                ),
                "HighDepthK2ToTargetRMSRatio": float(
                    pd.DataFrame(zone_rows).set_index("DepthBin").loc["high_depth", "K2ToTargetRMSRatio"]
                ),
                "HighDepthCosineTargetVsK2": float(
                    pd.DataFrame(zone_rows).set_index("DepthBin").loc["high_depth", "CosineTargetVsK2"]
                ),
                "MostViableNextDirection": "derive_tau_core_amplitude_normalization_and_test_depth_native_coherent_mode",
                "Reason": "locked_k2_already_has_depth_backbone; scale_only_and_scale_plus_offset_improve_proxy_scores_but require non-posthoc tau-core derivation",
                "ClaimBoundary": "three_path_viability_preflight_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_MODELS}")
    print(f"Wrote {OUT_ZONES}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
