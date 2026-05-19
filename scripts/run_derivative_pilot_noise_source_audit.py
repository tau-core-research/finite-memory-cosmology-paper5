#!/usr/bin/env python3
"""Diagnose which public-input noise source drives derivative-pilot split spread.

Modes:
- SN_ONLY: perturb SN D-proxy input, keep BAO H_D-proxy fixed.
- BAO_ONLY: keep SN D-proxy fixed, perturb BAO H_D-proxy input.
- SN_PLUS_BAO: perturb both.

This is a diagnostic stress test only. It is not a source-native bootstrap and
does not authorize measurement validation.
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
PILOT_VECTOR = BR / "source_native_derivative_pilot_reconstruction_vector.csv"

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

OUT_SAMPLES = EVIDENCE / "derivative_pilot_noise_source_samples.csv"
OUT_SUMMARY = EVIDENCE / "derivative_pilot_noise_source_summary.csv"
OUT_DOC = DOCS / "derivative_pilot_noise_source_audit.md"

CLAIM_BOUNDARY = "derivative_pilot_noise_source_audit_no_measurement_validation"


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


def omega_draw(
    mode: str,
    rng: np.random.Generator,
    grid: np.ndarray,
    sn_z: np.ndarray,
    sn_d: np.ndarray,
    sn_sigma: np.ndarray,
    bao_z: np.ndarray,
    bao_h: np.ndarray,
    bao_sigma: np.ndarray,
) -> np.ndarray:
    d_draw = rng.normal(sn_d, sn_sigma) if mode in {"SN_ONLY", "SN_PLUS_BAO"} else sn_d
    h_draw = rng.normal(bao_h, bao_sigma) if mode in {"BAO_ONLY", "SN_PLUS_BAO"} else bao_h
    d_poly = weighted_polyfit(sn_z, d_draw, sn_sigma, 5)
    h_poly = weighted_polyfit(bao_z, h_draw, bao_sigma, 3)
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
    vector = pd.read_csv(PILOT_VECTOR)
    grid = vector["z"].to_numpy(float)

    sn_z = sn["z"].to_numpy(float)
    sn_d = sn["D_proxy_Mpc"].to_numpy(float)
    sn_sigma = sn["D_proxy_sigma_diag_Mpc"].to_numpy(float)
    bao_z = bao["z"].to_numpy(float)
    bao_h = bao["Hrs_over_c_proxy"].to_numpy(float)
    bao_sigma = bao["Hrs_over_c_sigma_proxy"].to_numpy(float)

    route_payloads = []
    for route in ROUTES:
        route_vector = pd.read_csv(Path(str(route["Vector"])))
        route_vector["DepthZone"] = route_vector["z_grid"].map(depth_zone)
        whitening = load_whitening(route, route_vector["GridIndex"].astype(int).to_list())
        route_payloads.append((route["RouteID"], route_vector, whitening))

    rng = np.random.default_rng(20260519)
    sample_count = 96
    rows = []
    for mode in ["SN_ONLY", "BAO_ONLY", "SN_PLUS_BAO"]:
        for sample_id in range(sample_count):
            omega = omega_draw(mode, rng, grid, sn_z, sn_d, sn_sigma, bao_z, bao_h, bao_sigma)
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
                            "AuditID": "DERIVATIVE_PILOT_NOISE_SOURCE_AUDIT_V1",
                            "NoiseMode": mode,
                            "RouteID": route_id,
                            "SampleID": sample_id,
                            "SubsetID": subset_id,
                            "ProjectedScale": scale,
                            "PilotLikeEnergyFractionOfK2": frac,
                            "LockedK2Changed": False,
                            "ScaleFitAllowed": False,
                            "MeasurementValidationAllowed": False,
                            "ClaimBoundary": CLAIM_BOUNDARY,
                        }
                    )

    samples = pd.DataFrame(rows)
    samples.to_csv(OUT_SAMPLES, index=False)

    summary_rows = []
    for (mode, subset_id), group in samples.groupby(["NoiseMode", "SubsetID"], sort=True):
        vals = group["PilotLikeEnergyFractionOfK2"].to_numpy(float)
        summary_rows.append(
            {
                "AuditID": "DERIVATIVE_PILOT_NOISE_SOURCE_AUDIT_V1",
                "NoiseMode": mode,
                "SubsetID": subset_id,
                "Rows": len(group),
                "ComponentFractionP16": float(np.percentile(vals, 16)),
                "ComponentFractionP50": float(np.percentile(vals, 50)),
                "ComponentFractionP84": float(np.percentile(vals, 84)),
                "ComponentFractionStd": float(np.std(vals, ddof=1)),
                "LockedK2Changed": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    summary = pd.DataFrame(summary_rows)

    low = summary[summary["SubsetID"].eq("low_depth")].copy()
    driver = low.sort_values("ComponentFractionStd", ascending=False).iloc[0]
    mid_high = summary[summary["SubsetID"].eq("mid_high_depth")]
    status_row = {
        "AuditID": "DERIVATIVE_PILOT_NOISE_SOURCE_AUDIT_SUMMARY_V1",
        "NoiseMode": "OVERALL",
        "SubsetID": "summary",
        "Rows": len(samples),
        "ComponentFractionP16": float(mid_high["ComponentFractionP16"].min()),
        "ComponentFractionP50": float(mid_high["ComponentFractionP50"].median()),
        "ComponentFractionP84": float(mid_high["ComponentFractionP84"].max()),
        "ComponentFractionStd": float(mid_high["ComponentFractionStd"].median()),
        "DominantLowDepthSpreadMode": str(driver["NoiseMode"]),
        "DominantLowDepthStd": float(driver["ComponentFractionStd"]),
        "LockedK2Changed": False,
        "ScaleFitAllowed": False,
        "MeasurementValidationAllowed": False,
        "CurrentStatus": "LOW_DEPTH_SPREAD_SOURCE_DIAGNOSED_DIAGNOSTIC_ONLY",
        "StrongestAllowedClaim": (
            "the derivative-pilot component uncertainty can be decomposed by public SN and BAO input-noise modes"
        ),
        "PrimaryResidualRisk": "noise-source decomposition still uses fixed polynomial pilot and diagonal public errors",
        "NextAction": "repeat with source-native bootstrap/covariance before using low-depth suppression as a strong claim",
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    summary = pd.concat([summary, pd.DataFrame([status_row])], ignore_index=True)
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Derivative Pilot Noise Source Audit",
                "",
                "Status: diagnostic noise-source decomposition; no measurement-validation claim.",
                "",
                "This audit separates SN-only, BAO-only, and combined public-input perturbations to diagnose which mode drives uncertainty in the derivative-pilot K2 component split.",
                "",
                "## Outputs",
                "",
                f"- Samples: `{OUT_SAMPLES.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SAMPLES}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
