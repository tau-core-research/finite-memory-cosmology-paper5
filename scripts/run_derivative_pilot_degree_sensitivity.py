#!/usr/bin/env python3
"""Audit derivative-pilot K2 component sensitivity to polynomial degrees.

The locked derivative pilot remains D5/H3. This script tests nearby fixed
degree choices as a reconstruction-sensitivity diagnostic only. It does not fit
K2/K1, select a new locked pilot, or authorize measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fmc.backreaction import omega_r_plus_3omega_q

ROOT = Path(__file__).resolve().parents[1]
BR = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SN_INPUT = BR / "source_native_training_sn_distance_proxy.csv"
BAO_INPUT = BR / "source_native_training_bao_hd_proxy.csv"
LOCKED_VECTOR = BR / "source_native_derivative_pilot_reconstruction_vector.csv"

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

OUT_GRID = EVIDENCE / "derivative_pilot_degree_sensitivity_grid.csv"
OUT_SUMMARY = EVIDENCE / "derivative_pilot_degree_sensitivity_summary.csv"
OUT_DOC = DOCS / "derivative_pilot_degree_sensitivity.md"

CLAIM_BOUNDARY = "derivative_pilot_degree_sensitivity_no_measurement_validation"


def weighted_polyfit(x: np.ndarray, y: np.ndarray, sigma: np.ndarray, degree: int) -> np.poly1d:
    mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(sigma) & (sigma > 0)
    if int(mask.sum()) <= degree:
        raise ValueError(f"not enough finite points for degree {degree}: {int(mask.sum())}")
    return np.poly1d(np.polyfit(x[mask], y[mask], degree, w=1.0 / sigma[mask]))


def weighted_mean_by_z(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for z_value, group in df.groupby("z", sort=True):
        y = group["Hrs_over_c_proxy"].to_numpy(float)
        sigma = group["Hrs_over_c_sigma_proxy"].to_numpy(float)
        mask = np.isfinite(y) & np.isfinite(sigma) & (sigma > 0)
        if not mask.any():
            continue
        weights = 1.0 / (sigma[mask] ** 2)
        rows.append(
            {
                "z": float(z_value),
                "Hrs_over_c_proxy": float(np.sum(weights * y[mask]) / np.sum(weights)),
                "Hrs_over_c_sigma_proxy": float(np.sqrt(1.0 / np.sum(weights))),
            }
        )
    return pd.DataFrame(rows)


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


def depth_zone(z: float) -> str:
    if z < 0.9:
        return "low_depth"
    if z < 1.6:
        return "mid_depth"
    return "high_depth"


def projection_scale(source: np.ndarray, basis: np.ndarray) -> float:
    denom = float(basis @ basis)
    if denom <= 0.0:
        return float("nan")
    return float((basis @ source) / denom)


def component_fraction(k2: np.ndarray, bridge: np.ndarray) -> tuple[float, float]:
    scale = projection_scale(k2, bridge)
    component = scale * bridge
    denom = float(k2 @ k2)
    if denom <= 0.0:
        return scale, float("nan")
    return scale, float((component @ component) / denom)


def build_omega(
    d_degree: int,
    h_degree: int,
    grid: np.ndarray,
    sn: pd.DataFrame,
    bao: pd.DataFrame,
) -> np.ndarray:
    d_poly = weighted_polyfit(
        sn["z"].to_numpy(float),
        sn["D_proxy_Mpc"].to_numpy(float),
        sn["D_proxy_sigma_diag_Mpc"].to_numpy(float),
        d_degree,
    )
    h_poly = weighted_polyfit(
        bao["z"].to_numpy(float),
        bao["Hrs_over_c_proxy"].to_numpy(float),
        bao["Hrs_over_c_sigma_proxy"].to_numpy(float),
        h_degree,
    )
    return omega_r_plus_3omega_q(
        grid,
        d_poly(grid),
        np.polyder(d_poly, 1)(grid),
        np.polyder(d_poly, 2)(grid),
        h_poly(grid),
        np.polyder(h_poly, 1)(grid),
    )


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    sn = pd.read_csv(SN_INPUT)
    bao = weighted_mean_by_z(pd.read_csv(BAO_INPUT))
    locked = pd.read_csv(LOCKED_VECTOR)
    grid = locked["z"].to_numpy(float)

    route_payloads = []
    for route in ROUTES:
        route_vector = pd.read_csv(Path(str(route["Vector"])))
        route_vector["DepthZone"] = route_vector["z_grid"].map(depth_zone)
        whitening = load_whitening(route, route_vector["GridIndex"].astype(int).to_list())
        route_payloads.append((route["RouteID"], route_vector, whitening))

    rows = []
    for d_degree in [3, 4, 5, 6]:
        for h_degree in [2, 3, 4]:
            omega = build_omega(d_degree, h_degree, grid, sn, bao)
            if not np.isfinite(omega).all():
                continue
            for route_id, route_vector, whitening in route_payloads:
                z_grid = route_vector["z_grid"].to_numpy(float)
                bridge = whitening @ np.interp(z_grid, grid, omega)
                working = route_vector.copy()
                working["BridgeWhite"] = bridge
                for subset_id, subset in [
                    ("mid_high_depth", working[working["DepthZone"].ne("low_depth")]),
                    ("high_depth", working[working["DepthZone"].eq("high_depth")]),
                    ("low_depth", working[working["DepthZone"].eq("low_depth")]),
                ]:
                    if subset.empty:
                        continue
                    scale, frac = component_fraction(
                        subset["K2LockedWhitened"].to_numpy(float),
                        subset["BridgeWhite"].to_numpy(float),
                    )
                    rows.append(
                        {
                            "AuditID": "DERIVATIVE_PILOT_DEGREE_SENSITIVITY_V1",
                            "DDegree": d_degree,
                            "HDDegree": h_degree,
                            "IsLockedPilotDegree": d_degree == 5 and h_degree == 3,
                            "RouteID": route_id,
                            "SubsetID": subset_id,
                            "ProjectedScale": scale,
                            "PilotLikeEnergyFractionOfK2": frac,
                            "LockedK2Changed": False,
                            "ScaleFitAllowed": False,
                            "MeasurementValidationAllowed": False,
                            "ClaimBoundary": CLAIM_BOUNDARY,
                        }
                    )

    grid_df = pd.DataFrame(rows)
    grid_df.to_csv(OUT_GRID, index=False)

    subset_summary = (
        grid_df.groupby(["SubsetID"], as_index=False)
        .agg(
            ComponentFractionMin=("PilotLikeEnergyFractionOfK2", "min"),
            ComponentFractionP50=("PilotLikeEnergyFractionOfK2", "median"),
            ComponentFractionMax=("PilotLikeEnergyFractionOfK2", "max"),
            LockedDegreeRows=("IsLockedPilotDegree", "sum"),
        )
    )
    low = subset_summary[subset_summary["SubsetID"].eq("low_depth")].iloc[0]
    mid_high = subset_summary[subset_summary["SubsetID"].eq("mid_high_depth")].iloc[0]
    high = subset_summary[subset_summary["SubsetID"].eq("high_depth")].iloc[0]
    locked_rows = grid_df[grid_df["IsLockedPilotDegree"].map(bool)]
    locked_low = float(locked_rows[locked_rows["SubsetID"].eq("low_depth")]["PilotLikeEnergyFractionOfK2"].mean())
    alternatives_low_median = float(
        grid_df[(~grid_df["IsLockedPilotDegree"].map(bool)) & grid_df["SubsetID"].eq("low_depth")][
            "PilotLikeEnergyFractionOfK2"
        ].median()
    )
    summary = pd.DataFrame(
        [
            {
                "AuditID": "DERIVATIVE_PILOT_DEGREE_SENSITIVITY_V1",
                "DegreePairs": int(grid_df[["DDegree", "HDDegree"]].drop_duplicates().shape[0]),
                "Routes": grid_df["RouteID"].nunique(),
                "MidHighComponentFractionMin": float(mid_high["ComponentFractionMin"]),
                "MidHighComponentFractionP50": float(mid_high["ComponentFractionP50"]),
                "MidHighComponentFractionMax": float(mid_high["ComponentFractionMax"]),
                "HighComponentFractionP50": float(high["ComponentFractionP50"]),
                "LowComponentFractionP50": float(low["ComponentFractionP50"]),
                "LockedPilotLowFractionMean": locked_low,
                "AlternativeDegreeLowFractionMedian": alternatives_low_median,
                "LowDepthDegreeSensitive": abs(locked_low - alternatives_low_median) > 0.10,
                "LockedK2Changed": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "DERIVATIVE_PILOT_DEGREE_SENSITIVITY_COMPLETED_DIAGNOSTIC_ONLY",
                "StrongestAllowedClaim": (
                    "nearby fixed polynomial degrees preserve nonzero mid/high K2 component but expose reconstruction sensitivity"
                ),
                "PrimaryResidualRisk": (
                    "degree scan is a reconstruction stress test and cannot replace source-native symbolic-regression selection"
                ),
                "NextAction": "use source-native expression families or registered smoothing/regularization before making low-depth suppression claims",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Derivative Pilot Degree Sensitivity",
                "",
                "Status: reconstruction-sensitivity diagnostic; locked pilot unchanged.",
                "",
                "This scans nearby fixed polynomial degrees around the locked D5/H3 derivative pilot. It does not select a new model and does not fit K2 or K1.",
                "",
                "## Outputs",
                "",
                f"- Grid: `{OUT_GRID.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_GRID}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
