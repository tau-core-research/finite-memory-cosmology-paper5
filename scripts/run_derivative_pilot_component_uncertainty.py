#!/usr/bin/env python3
"""Propagate derivative-pilot bootstrap samples through the K2 component split."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"

BOOTSTRAP = DATA / "source_native_derivative_pilot_bootstrap_omega_samples.csv"

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

OUT_SAMPLES = EVIDENCE / "derivative_pilot_component_uncertainty_samples.csv"
OUT_SUMMARY = EVIDENCE / "derivative_pilot_component_uncertainty_summary.csv"
OUT_DOC = DOCS / "derivative_pilot_component_uncertainty.md"

CLAIM_BOUNDARY = "derivative_pilot_component_uncertainty_no_measurement_validation"


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


def projection_scale(source: np.ndarray, basis: np.ndarray) -> float:
    denom = float(basis @ basis)
    if denom <= 0.0:
        return float("nan")
    return float((basis @ source) / denom)


def component_fraction(k2: np.ndarray, bridge: np.ndarray) -> tuple[float, float, float]:
    scale = projection_scale(k2, bridge)
    component = scale * bridge
    k2_energy = float(k2 @ k2)
    comp_energy = float(component @ component)
    residual_energy = float((k2 - component) @ (k2 - component))
    return scale, comp_energy / k2_energy if k2_energy > 0 else float("nan"), residual_energy / k2_energy if k2_energy > 0 else float("nan")


def summarize(samples: pd.DataFrame, subset_id: str) -> dict[str, object]:
    vals = samples[samples["SubsetID"].eq(subset_id)]["PilotLikeEnergyFractionOfK2"].to_numpy(float)
    residual = samples[samples["SubsetID"].eq(subset_id)]["ResidualEnergyFractionOfK2"].to_numpy(float)
    return {
        f"{subset_id}_P16": float(np.percentile(vals, 16)),
        f"{subset_id}_P50": float(np.percentile(vals, 50)),
        f"{subset_id}_P84": float(np.percentile(vals, 84)),
        f"{subset_id}_ResidualP50": float(np.percentile(residual, 50)),
    }


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    boot = pd.read_csv(BOOTSTRAP)
    sample_rows = []
    for route in ROUTES:
        vector = pd.read_csv(Path(str(route["Vector"])))
        vector["DepthZone"] = vector["z_grid"].map(depth_zone)
        grid_indices = vector["GridIndex"].astype(int).to_list()
        whitening = load_whitening(route, grid_indices)
        z_grid = vector["z_grid"].to_numpy(float)

        for sample_id, group in boot.groupby("SampleID", sort=True):
            group = group.sort_values("z")
            omega_interp = np.interp(z_grid, group["z"].to_numpy(float), group["Omega_R_plus_3Omega_Q"].to_numpy(float))
            bridge_white = whitening @ omega_interp
            working = vector.copy()
            working["BridgeWhite"] = bridge_white
            for subset_id, subset in [
                ("all_depth", working),
                ("mid_high_depth", working[working["DepthZone"].ne("low_depth")]),
                ("high_depth", working[working["DepthZone"].eq("high_depth")]),
                ("mid_depth", working[working["DepthZone"].eq("mid_depth")]),
                ("low_depth", working[working["DepthZone"].eq("low_depth")]),
            ]:
                if subset.empty:
                    continue
                scale, frac, residual_frac = component_fraction(
                    subset["K2LockedWhitened"].to_numpy(float),
                    subset["BridgeWhite"].to_numpy(float),
                )
                sample_rows.append(
                    {
                        "AuditID": "DERIVATIVE_PILOT_COMPONENT_UNCERTAINTY_V1",
                        "RouteID": route["RouteID"],
                        "SampleID": int(sample_id),
                        "SubsetID": subset_id,
                        "Rows": len(subset),
                        "ProjectedScale": scale,
                        "PilotLikeEnergyFractionOfK2": frac,
                        "ResidualEnergyFractionOfK2": residual_frac,
                        "ScaleFitAllowed": False,
                        "LockedK2Changed": False,
                        "MeasurementValidationAllowed": False,
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )

    samples = pd.DataFrame(sample_rows)
    samples.to_csv(OUT_SAMPLES, index=False)

    summary_data: dict[str, object] = {
        "AuditID": "DERIVATIVE_PILOT_COMPONENT_UNCERTAINTY_V1",
        "Routes": samples["RouteID"].nunique(),
        "SamplesPerRoute": int(samples.groupby("RouteID")["SampleID"].nunique().min()),
        "TotalRows": len(samples),
        "LockedK2Changed": False,
        "ScaleFitAllowed": False,
        "MeasurementValidationAllowed": False,
        "CurrentStatus": "DERIVATIVE_PILOT_COMPONENT_UNCERTAINTY_READY_DIAGNOSTIC_ONLY",
        "StrongestAllowedClaim": (
            "the derivative-pilot K2 component split has a bootstrap uncertainty stress test"
        ),
        "PrimaryResidualRisk": (
            "component uncertainty is broad and based on diagonal public training-input errors, not source-native covariance"
        ),
        "NextAction": "replace pilot bootstrap with source-native symbolic-regression bootstrap/covariance before physical-null promotion",
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    for subset_id in ["mid_high_depth", "high_depth", "low_depth"]:
        summary_data.update(summarize(samples, subset_id))

    pd.DataFrame([summary_data]).to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Derivative Pilot Component Uncertainty",
                "",
                "Status: bootstrap split uncertainty; diagnostic only.",
                "",
                "This propagates derivative-pilot bootstrap samples through the K2 component split. It does not fit K2 or K1 and does not replace source-native covariance.",
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
