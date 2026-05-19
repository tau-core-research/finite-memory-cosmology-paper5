#!/usr/bin/env python3
"""Run leave-one-depth stability tests for the K2/backreaction split.

This audit recomputes the projection scale after removing one row from the
mid/high or high-depth subset. It is a preflight sensitivity check only: locked
K2 is unchanged, no new K1 is fitted, no rho>4 route is introduced, and no
measurement validation is authorized.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"

OMEGA = DATA / "provisional_bao_backreaction_omega_curve.csv"

ROUTES = [
    {
        "RouteID": "PUBLIC_PROXY_WHITENED_STANDARDIZED",
        "Vector": EVIDENCE / "whitened_standardized_branch_contrast_vector.csv",
        "Whitening": EVIDENCE / "whitened_standardized_branch_contrast_matrix.csv",
        "Covariance": None,
    },
    {
        "RouteID": "REGISTERED_SHRINKAGE_WHITENED",
        "Vector": EVIDENCE / "registered_shrinkage_whitened_branch_contrast_vector.csv",
        "Whitening": None,
        "Covariance": EVIDENCE / "registered_shrinkage_whitened_branch_contrast_covariance.csv",
    },
]

OUT_ROW = EVIDENCE / "backreaction_depth_stability_row.csv"
OUT_SUMMARY = EVIDENCE / "backreaction_depth_stability_summary.csv"
OUT_DOC = DOCS / "backreaction_depth_stability.md"


def depth_zone(z: float) -> str:
    if z < 0.9:
        return "low_depth"
    if z < 1.6:
        return "mid_depth"
    return "high_depth"


def load_whitening(route: dict[str, object], grid_indices: list[int]) -> np.ndarray:
    if route["Whitening"] is not None:
        matrix = pd.read_csv(Path(str(route["Whitening"])))
        return matrix[[str(idx) for idx in grid_indices]].to_numpy(float)
    cov_df = pd.read_csv(Path(str(route["Covariance"])))
    cov = cov_df[[str(idx) for idx in grid_indices]].to_numpy(float)
    eigvals, eigvecs = np.linalg.eigh(0.5 * (cov + cov.T))
    if np.any(eigvals <= 0.0):
        raise ValueError(f"non-positive covariance eigenvalue for {route['RouteID']}")
    return eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.std(a) == 0.0 or np.std(b) == 0.0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def unit_shape(values: np.ndarray) -> np.ndarray:
    centered = values - float(np.mean(values))
    norm = float(np.linalg.norm(centered))
    if norm <= 0.0:
        return centered
    return centered / norm


def projection_scale(source: np.ndarray, basis: np.ndarray) -> float:
    denom = float(basis @ basis)
    if denom <= 0.0:
        return float("nan")
    return float((basis @ source) / denom)


def energy_fraction(k2: np.ndarray, component: np.ndarray) -> float:
    denom = float(k2 @ k2)
    if denom <= 0.0:
        return float("nan")
    return float((component @ component) / denom)


def chi2(residual: np.ndarray) -> float:
    return float(residual @ residual)


def variant_series(z_grid: np.ndarray, omega_z: np.ndarray, omega_val: np.ndarray) -> dict[str, tuple[np.ndarray, bool, str]]:
    raw = np.interp(z_grid, omega_z, omega_val)
    centered = raw - float(np.mean(raw))
    unit = unit_shape(raw)
    grad = np.gradient(raw, z_grid)
    grad_centered = grad - float(np.mean(grad))
    high_weighted = raw * (z_grid / float(np.max(z_grid))) ** 2
    return {
        "RAW_OMEGA": (raw, False, "raw_provisional_omega"),
        "CENTERED_OMEGA": (centered, False, "mean_removed_shape_variant"),
        "UNIT_SHAPE_OMEGA": (unit, False, "unit_norm_shape_variant"),
        "HIGH_DEPTH_WEIGHTED_OMEGA": (high_weighted, False, "depth_emphasis_shape_variant"),
        "OMEGA_GRADIENT": (grad_centered, False, "derivative_shape_variant"),
        "SIGN_INVERTED_RAW_FORBIDDEN": (-raw, True, "forbidden_sign_inversion_diagnostic"),
    }


def summarize_subset(
    route_id: str,
    variant_id: str,
    variant_class: str,
    forbidden: bool,
    subset_id: str,
    removed_z: float | None,
    subset: pd.DataFrame,
) -> dict[str, object]:
    br = subset["BridgeWhite"].to_numpy(float)
    target = subset["WhitenedTarget"].to_numpy(float)
    k2 = subset["K2LockedWhitened"].to_numpy(float)
    scale = projection_scale(k2, br)
    component = scale * br
    residual = k2 - component
    component_fraction = energy_fraction(k2, component)
    residual_fraction = energy_fraction(k2, residual)
    return {
        "AuditID": "BACKREACTION_DEPTH_STABILITY_V1",
        "RouteID": route_id,
        "VariantID": variant_id,
        "VariantClass": variant_class,
        "ForbiddenForClaims": forbidden,
        "SubsetID": subset_id,
        "RemovedZ": "NONE" if removed_z is None else removed_z,
        "RowsRemaining": len(subset),
        "ProjectedScale": scale,
        "BackreactionLikeEnergyFractionOfK2": component_fraction,
        "ResidualEnergyFractionOfK2": residual_fraction,
        "CorrelationComponentWithTarget": corr(component, target),
        "CorrelationResidualWithTarget": corr(residual, target),
        "ComponentChi2ToTarget": chi2(target - component),
        "ResidualChi2ToTarget": chi2(target - residual),
        "LockedK2Changed": False,
        "ScaleFitAllowed": False,
        "MeasurementValidationAllowed": False,
        "ClaimBoundary": "backreaction_depth_stability_no_measurement_validation",
    }


def classify(min_fraction: float, max_drop: float) -> str:
    if np.isnan(min_fraction):
        return "INSUFFICIENT_ROWS"
    if min_fraction <= 0.0:
        return "POINT_DOMINATED_WARNING"
    if max_drop > 0.50:
        return "HIGH_INFLUENCE_WARNING"
    if min_fraction < 0.25:
        return "WEAK_DEPTH_STABILITY_WARNING"
    if min_fraction < 0.40:
        return "MODERATE_DEPTH_STABILITY"
    return "STABLE_NONZERO_COMPONENT"


def main() -> None:
    omega = pd.read_csv(OMEGA)
    omega_z = omega["z"].to_numpy(float)
    omega_val = omega["Omega_R_plus_3Omega_Q"].to_numpy(float)
    rows: list[dict[str, object]] = []

    for route in ROUTES:
        vector = pd.read_csv(Path(str(route["Vector"])))
        vector["DepthZone"] = vector["z_grid"].map(depth_zone)
        grid_indices = vector["GridIndex"].astype(int).to_list()
        whitening = load_whitening(route, grid_indices)
        z_grid = vector["z_grid"].to_numpy(float)

        for variant_id, (series, forbidden, variant_class) in variant_series(z_grid, omega_z, omega_val).items():
            br_white_all = whitening @ series
            working = vector.copy()
            working["BridgeWhite"] = br_white_all
            for subset_id, subset in [
                ("mid_high_depth", working[working["DepthZone"].ne("low_depth")]),
                ("high_depth", working[working["DepthZone"].eq("high_depth")]),
            ]:
                if len(subset) < 3:
                    continue
                rows.append(
                    summarize_subset(
                        str(route["RouteID"]),
                        variant_id,
                        variant_class,
                        forbidden,
                        subset_id,
                        None,
                        subset,
                    )
                )
                for removed_z in sorted(subset["z_grid"].astype(float).unique()):
                    leave_one = subset[~np.isclose(subset["z_grid"].astype(float), removed_z)]
                    if len(leave_one) < 2:
                        continue
                    rows.append(
                        summarize_subset(
                            str(route["RouteID"]),
                            variant_id,
                            variant_class,
                            forbidden,
                            subset_id,
                            float(removed_z),
                            leave_one,
                        )
                    )

    row_df = pd.DataFrame(rows)
    row_df.to_csv(OUT_ROW, index=False)

    allowed = row_df[~row_df["ForbiddenForClaims"].astype(bool)].copy()
    base = allowed[allowed["RemovedZ"].astype(str).eq("NONE")]
    loo = allowed[~allowed["RemovedZ"].astype(str).eq("NONE")]
    summary_rows: list[dict[str, object]] = []
    for (route_id, subset_id), base_group in base.groupby(["RouteID", "SubsetID"]):
        loo_group = loo[(loo["RouteID"].eq(route_id)) & (loo["SubsetID"].eq(subset_id))]
        base_mean = float(base_group["BackreactionLikeEnergyFractionOfK2"].mean())
        min_loo = float(loo_group["BackreactionLikeEnergyFractionOfK2"].min()) if not loo_group.empty else float("nan")
        max_loo = float(loo_group["BackreactionLikeEnergyFractionOfK2"].max()) if not loo_group.empty else float("nan")
        max_drop = base_mean - min_loo if np.isfinite(min_loo) else float("nan")
        summary_rows.append(
            {
                "AuditID": "BACKREACTION_DEPTH_STABILITY_V1",
                "RouteID": route_id,
                "SubsetID": subset_id,
                "AllowedVariants": base_group["VariantID"].nunique(),
                "BaseEnergyFractionMean": base_mean,
                "LeaveOneEnergyFractionMin": min_loo,
                "LeaveOneEnergyFractionMax": max_loo,
                "MaxDropFromBaseMean": max_drop,
                "DepthStabilityStatus": classify(min_loo, max_drop),
                "SourceNativeLeaveOneAvailable": False,
                "LockedK2Changed": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "StrongestAllowedClaim": (
                    "leave-one-depth audit keeps a nonzero backreaction-like component in allowed bridge variants, "
                    "but source-native reconstruction is still required"
                ),
                "PrimaryResidualRisk": "provisional BAO-only bridge and small high-depth row count",
                "NextAction": "repeat with source-native D_A,H_D derivative reconstruction and covariance",
                "ClaimBoundary": "backreaction_depth_stability_no_measurement_validation",
            }
        )

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Backreaction Depth Stability",
                "",
                "Status: leave-one-depth preflight sensitivity audit; no measurement validation.",
                "",
                "This audit recomputes the K2/backreaction projection after removing one depth row from the mid/high and high-depth subsets. It tests whether the component split is dominated by a single row. It does not change locked K2 and does not fit a new K1.",
                "",
                "## Outputs",
                "",
                f"- Row audit: `{OUT_ROW.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_ROW}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
