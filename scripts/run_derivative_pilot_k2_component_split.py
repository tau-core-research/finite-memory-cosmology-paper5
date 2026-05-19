#!/usr/bin/env python3
"""Project locked K2 onto the public derivative-pilot backreaction route.

This is a diagnostic component split. The derivative pilot is not a
source-native symbolic-regression export, the projection scale is not a fitted
physical model, and the result does not authorize measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"

OMEGA = DATA / "source_native_derivative_pilot_omega_curve.csv"

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

OUT_ROW = EVIDENCE / "derivative_pilot_k2_component_split_row.csv"
OUT_ZONE = EVIDENCE / "derivative_pilot_k2_component_split_zone.csv"
OUT_SUMMARY = EVIDENCE / "derivative_pilot_k2_component_split_summary.csv"
OUT_DOC = DOCS / "derivative_pilot_k2_component_split.md"

CLAIM_BOUNDARY = "derivative_pilot_k2_component_split_no_measurement_validation"


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


def chi2(residual: np.ndarray) -> float:
    return float(residual @ residual)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or float(np.std(a)) == 0.0 or float(np.std(b)) == 0.0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def projection_scale(source: np.ndarray, basis: np.ndarray) -> float:
    denom = float(basis @ basis)
    if denom <= 0.0:
        return float("nan")
    return float((basis @ source) / denom)


def summarize(route_id: str, subset_id: str, df: pd.DataFrame) -> tuple[dict[str, object], pd.DataFrame]:
    target = df["WhitenedTarget"].to_numpy(float)
    k1 = df["K1Whitened"].to_numpy(float)
    k2 = df["K2LockedWhitened"].to_numpy(float)
    pilot = df["PilotBackreactionWhitened"].to_numpy(float)

    scale = projection_scale(k2, pilot)
    component = scale * pilot
    residual = k2 - component

    k2_energy = float(k2 @ k2)
    component_energy = float(component @ component)
    residual_energy = float(residual @ residual)

    out = df.copy()
    out["SubsetID"] = subset_id
    out["K2ProjectedPilotScale"] = scale
    out["PilotLikeK2Component"] = component
    out["K2ResidualAfterPilotComponent"] = residual
    out["PilotComponentAbsFractionOfK2"] = np.divide(np.abs(component), np.maximum(np.abs(k2), 1e-12))
    out["ResidualAbsFractionOfK2"] = np.divide(np.abs(residual), np.maximum(np.abs(k2), 1e-12))
    out["PilotComponentSignMatchesK2"] = np.sign(component) == np.sign(k2)
    out["ResidualSignMatchesTarget"] = np.sign(residual) == np.sign(target)
    out["MeasurementValidationAllowed"] = False
    out["ClaimBoundary"] = CLAIM_BOUNDARY

    summary = {
        "DiagnosisID": "DERIVATIVE_PILOT_K2_COMPONENT_SPLIT_V1",
        "RouteID": route_id,
        "SubsetID": subset_id,
        "Rows": len(df),
        "K2ProjectedPilotScale": scale,
        "K2Energy": k2_energy,
        "PilotLikeComponentEnergy": component_energy,
        "K2ResidualEnergy": residual_energy,
        "PilotLikeEnergyFractionOfK2": component_energy / k2_energy if k2_energy > 0.0 else float("nan"),
        "ResidualEnergyFractionOfK2": residual_energy / k2_energy if k2_energy > 0.0 else float("nan"),
        "CorrelationPilotComponentWithK2": corr(component, k2),
        "CorrelationPilotComponentWithTarget": corr(component, target),
        "CorrelationResidualWithTarget": corr(residual, target),
        "K2Chi2ToTarget": chi2(target - k2),
        "PilotComponentChi2ToTarget": chi2(target - component),
        "K2ResidualChi2ToTarget": chi2(target - residual),
        "K1PlusLockedK2Chi2ToTarget": chi2(target - (k1 + k2)),
        "K1PlusResidualOnlyChi2ToTarget": chi2(target - (k1 + residual)),
        "ScaleFitAllowed": False,
        "LockedK2Changed": False,
        "MeasurementValidationAllowed": False,
        "CurrentStatus": "DERIVATIVE_PILOT_COMPONENT_DIAGNOSTIC_ONLY",
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    return summary, out


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    omega = pd.read_csv(OMEGA)
    omega_z = omega["z"].to_numpy(float)
    omega_val = omega["Omega_R_plus_3Omega_Q"].to_numpy(float)

    all_rows = []
    summaries = []
    for route in ROUTES:
        vector = pd.read_csv(Path(str(route["Vector"])))
        grid_indices = vector["GridIndex"].astype(int).to_list()
        whitening = load_whitening(route, grid_indices)
        z = vector["z_grid"].to_numpy(float)
        in_range = (z >= float(np.min(omega_z))) & (z <= float(np.max(omega_z)))
        omega_interp = np.interp(z, omega_z, omega_val)
        pilot_white = whitening @ omega_interp

        row = pd.DataFrame(
            {
                "AuditID": "DERIVATIVE_PILOT_K2_COMPONENT_SPLIT_V1",
                "RouteID": route["RouteID"],
                "ComponentIndex": np.arange(len(vector), dtype=int),
                "GridIndex": vector["GridIndex"].astype(int),
                "z_grid": z,
                "DepthZone": [depth_zone(v) for v in z],
                "PilotOmegaInterpolated": omega_interp,
                "PilotOmegaInInterpolationRange": in_range,
                "PilotBackreactionWhitened": pilot_white,
                "WhitenedTarget": vector["WhitenedTarget"].to_numpy(float),
                "K1Whitened": vector["K1Whitened"].to_numpy(float),
                "K2LockedWhitened": vector["K2LockedWhitened"].to_numpy(float),
                "SignStable": vector["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy(),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

        for subset_id, subset in [
            ("all_depth", row),
            ("mid_high_depth", row[row["DepthZone"].ne("low_depth")]),
            ("high_depth", row[row["DepthZone"].eq("high_depth")]),
            ("mid_depth", row[row["DepthZone"].eq("mid_depth")]),
            ("low_depth", row[row["DepthZone"].eq("low_depth")]),
        ]:
            if subset.empty:
                continue
            summary, subset_rows = summarize(str(route["RouteID"]), subset_id, subset)
            summaries.append(summary)
            all_rows.append(subset_rows)

    row_out = pd.concat(all_rows, ignore_index=True)
    zone = pd.DataFrame(summaries)
    row_out.to_csv(OUT_ROW, index=False)
    zone.to_csv(OUT_ZONE, index=False)

    mid_high = zone[zone["SubsetID"].eq("mid_high_depth")]
    high = zone[zone["SubsetID"].eq("high_depth")]
    low = zone[zone["SubsetID"].eq("low_depth")]
    summary = pd.DataFrame(
        [
            {
                "DiagnosisID": "DERIVATIVE_PILOT_K2_COMPONENT_SPLIT_V1",
                "Routes": zone["RouteID"].nunique(),
                "Subsets": len(zone),
                "MidHighPilotEnergyFractionMean": float(mid_high["PilotLikeEnergyFractionOfK2"].mean()),
                "HighPilotEnergyFractionMean": float(high["PilotLikeEnergyFractionOfK2"].mean()),
                "LowPilotEnergyFractionMean": float(low["PilotLikeEnergyFractionOfK2"].mean()),
                "MidHighResidualEnergyFractionMean": float(mid_high["ResidualEnergyFractionOfK2"].mean()),
                "HighResidualEnergyFractionMean": float(high["ResidualEnergyFractionOfK2"].mean()),
                "MidHighPilotTargetCorrelationMean": float(mid_high["CorrelationPilotComponentWithTarget"].mean()),
                "MidHighResidualTargetCorrelationMean": float(mid_high["CorrelationResidualWithTarget"].mean()),
                "LockedK2Changed": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "DERIVATIVE_PILOT_K2_COMPONENT_SPLIT_COMPLETED_DIAGNOSTIC_ONLY",
                "StrongestAllowedClaim": (
                    "the public derivative pilot can be projected into the locked K2 route space as a diagnostic component split"
                ),
                "PrimaryResidualRisk": (
                    "pilot derivatives are fixed-polynomial public-data proxies, not source-native symbolic-regression exports"
                ),
                "NextAction": "compare this pilot split to the provisional BAO-only split and then prioritize source-native derivative/covariance export",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Derivative Pilot K2 Component Split",
                "",
                "Status: diagnostic split only; locked K2 unchanged.",
                "",
                "This audit projects locked K2 onto the public SN/BAO derivative-pilot backreaction curve in the same whitened route spaces used by the provisional backreaction audit. It is not a fitted model and does not replace source-native reconstruction.",
                "",
                "## Outputs",
                "",
                f"- Row split: `{OUT_ROW.relative_to(ROOT)}`",
                f"- Zone split: `{OUT_ZONE.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_ROW}")
    print(f"Wrote {OUT_ZONE}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
