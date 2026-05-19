#!/usr/bin/env python3
"""Run bridge-variant stability tests for the K2/backreaction split."""

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

OUT_ZONE = EVIDENCE / "backreaction_bridge_variant_stability_zone.csv"
OUT_SUMMARY = EVIDENCE / "backreaction_bridge_variant_stability_summary.csv"
OUT_DOC = DOCS / "backreaction_bridge_variant_stability.md"


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


def chi2(a: np.ndarray) -> float:
    return float(a @ a)


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


def summarize(route_id: str, variant_id: str, variant_class: str, forbidden: bool, subset_id: str, df: pd.DataFrame, br_white: np.ndarray) -> dict[str, object]:
    target = df["WhitenedTarget"].to_numpy(float)
    k2 = df["K2LockedWhitened"].to_numpy(float)
    scale = projection_scale(k2, br_white)
    component = scale * br_white
    residual = k2 - component
    k2_energy = float(k2 @ k2)
    component_energy = float(component @ component)
    residual_energy = float(residual @ residual)
    return {
        "AuditID": "BACKREACTION_BRIDGE_VARIANT_STABILITY_V1",
        "RouteID": route_id,
        "VariantID": variant_id,
        "VariantClass": variant_class,
        "ForbiddenForClaims": forbidden,
        "SubsetID": subset_id,
        "Rows": len(df),
        "ProjectedScale": scale,
        "BackreactionLikeEnergyFractionOfK2": component_energy / k2_energy if k2_energy > 0 else float("nan"),
        "ResidualEnergyFractionOfK2": residual_energy / k2_energy if k2_energy > 0 else float("nan"),
        "CorrelationComponentWithTarget": corr(component, target),
        "CorrelationResidualWithTarget": corr(residual, target),
        "CorrelationComponentWithK2": corr(component, k2),
        "K2Chi2ToTarget": chi2(target - k2),
        "ComponentChi2ToTarget": chi2(target - component),
        "ResidualChi2ToTarget": chi2(target - residual),
        "ScaleFitAllowed": False,
        "LockedK2Changed": False,
        "MeasurementValidationAllowed": False,
        "ClaimBoundary": "backreaction_bridge_variant_stability_no_measurement_validation",
    }


def main() -> None:
    omega = pd.read_csv(OMEGA)
    omega_z = omega["z"].to_numpy(float)
    omega_val = omega["Omega_R_plus_3Omega_Q"].to_numpy(float)
    zone_rows = []

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
                ("all_depth", working),
                ("mid_high_depth", working[working["DepthZone"].ne("low_depth")]),
                ("high_depth", working[working["DepthZone"].eq("high_depth")]),
                ("mid_depth", working[working["DepthZone"].eq("mid_depth")]),
                ("low_depth", working[working["DepthZone"].eq("low_depth")]),
            ]:
                if subset.empty:
                    continue
                zone_rows.append(
                    summarize(
                        str(route["RouteID"]),
                        variant_id,
                        variant_class,
                        forbidden,
                        subset_id,
                        subset,
                        subset["BridgeWhite"].to_numpy(float),
                    )
                )

    zone = pd.DataFrame(zone_rows)
    zone.to_csv(OUT_ZONE, index=False)

    allowed = zone[~zone["ForbiddenForClaims"].astype(bool)]
    mid_high = allowed[allowed["SubsetID"].eq("mid_high_depth")]
    high = allowed[allowed["SubsetID"].eq("high_depth")]
    summary = pd.DataFrame(
        [
            {
                "AuditID": "BACKREACTION_BRIDGE_VARIANT_STABILITY_V1",
                "Routes": zone["RouteID"].nunique(),
                "Variants": zone["VariantID"].nunique(),
                "AllowedVariants": allowed["VariantID"].nunique(),
                "ForbiddenVariants": zone[zone["ForbiddenForClaims"].astype(bool)]["VariantID"].nunique(),
                "MidHighAllowedEnergyFractionMean": float(mid_high["BackreactionLikeEnergyFractionOfK2"].mean()),
                "MidHighAllowedEnergyFractionMin": float(mid_high["BackreactionLikeEnergyFractionOfK2"].min()),
                "MidHighAllowedEnergyFractionMax": float(mid_high["BackreactionLikeEnergyFractionOfK2"].max()),
                "HighAllowedEnergyFractionMean": float(high["BackreactionLikeEnergyFractionOfK2"].mean()),
                "HighAllowedEnergyFractionMin": float(high["BackreactionLikeEnergyFractionOfK2"].min()),
                "HighAllowedEnergyFractionMax": float(high["BackreactionLikeEnergyFractionOfK2"].max()),
                "LockedK2Changed": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "TWO_COMPONENT_PICTURE_VARIANT_SENSITIVE_BUT_PERSISTENT",
                "StrongestAllowedClaim": (
                    "allowed bridge variants keep a nonzero backreaction-like component and a nonzero residual component, "
                    "but component fractions are bridge-sensitive"
                ),
                "PrimaryResidualRisk": "bridge variant choice changes component fractions; source-native observable bridge is still required",
                "NextAction": "run depth stability and source-native reconstruction upgrade before using this in paper-level claims",
                "ClaimBoundary": "backreaction_bridge_variant_stability_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DOC.write_text(
        "\n".join(
            [
                "# Backreaction Bridge Variant Stability",
                "",
                "Status: diagnostic stability audit; locked K2 unchanged.",
                "",
                "This audit repeats the K2/backreaction component split under several bridge variants. Sign inversion is reported only as a forbidden diagnostic.",
                "",
                "## Outputs",
                "",
                f"- Zone audit: `{OUT_ZONE.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_ZONE}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
