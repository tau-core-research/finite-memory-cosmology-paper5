#!/usr/bin/env python3
"""Run null-model benchmark MVP across current coordinate mappings."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.coordinates import x_chi_normalized, x_index_native, x_optical_depth_like, x_z_normalized
from fmc.gates import classify_gate, envelope_fraction, sign_stable_violations
from fmc.likelihood import aic, bic, chi2, diag_covariance_from_sigma
from fmc.nulls import coordinate_remap_control, null_no_memory, polynomial_fit, sign_randomized_control
from fmc.operators import k2_from_k1

PACKET = ROOT / "evidence" / "diagnostic_point_audit.csv"
BASELINE = ROOT / "frozen" / "k1_baseline_v1.csv"
OUT = ROOT / "evidence" / "null_comparison_results.csv"


def bool_series(values: pd.Series) -> np.ndarray:
    """Parse permissive boolean strings from CSV."""
    return values.astype(str).str.lower().isin(["true", "1", "yes", "y"]).to_numpy()


def mapping_set(z: np.ndarray, packet_x: np.ndarray) -> dict[str, np.ndarray]:
    """Return predeclared audit mappings."""
    return {
        "z_normalized_current_packet": packet_x,
        "z_normalized_recomputed": x_z_normalized(z),
        "chi_normalized_flat_lcdm_audit": x_chi_normalized(z),
        "optical_depth_like_uniform": x_optical_depth_like(z),
        "likelihood_native_index": x_index_native(len(z)),
    }


def score_model(prediction, y, lower, upper, stable, covariance, sigma, rho, parameter_count):
    """Compute all MVP score columns for one prediction."""
    pred = np.asarray(prediction, dtype=float)
    diag_residual = np.abs((y - pred) / sigma)
    max_abs_residual = float(np.max(diag_residual))
    env = envelope_fraction(pred, lower, upper)
    violations = sign_stable_violations(pred, y, stable)
    c2 = chi2(y, pred, covariance)
    status = classify_gate(
        env,
        violations,
        max_abs_residual=max_abs_residual,
        rho=None if rho is None else float(rho),
    )
    return {
        "Chi2DiagProxy": c2,
        "AIC": aic(c2, parameter_count),
        "BIC": bic(c2, parameter_count, len(y)),
        "MaxAbsDiagResidual": max_abs_residual,
        "EnvelopeFraction": env,
        "SignStableViolations": violations,
        "Status": status,
    }


def best_k2_grid(x_values, k1, y, lower, upper, stable, covariance, sigma):
    """Select the best bounded K2 grid point inside rho in [3, 4]."""
    best = None
    for rho in np.linspace(3.0, 4.0, 11):
        pred = k2_from_k1(x_values, k1, rho=float(rho))
        score = score_model(pred, y, lower, upper, stable, covariance, sigma, rho, 1)
        if best is None or score["Chi2DiagProxy"] < best["score"]["Chi2DiagProxy"]:
            best = {"rho": float(rho), "prediction": pred, "score": score}
    if best is None:
        raise RuntimeError("empty K2 rho grid")
    return best


def main() -> None:
    packet = pd.read_csv(PACKET)
    baseline = pd.read_csv(BASELINE)

    z = packet["z"].to_numpy(float)
    packet_x = packet["x"].to_numpy(float)
    y = packet["target_median"].to_numpy(float)
    lower = packet["target_p16"].to_numpy(float)
    upper = packet["target_p84"].to_numpy(float)
    stable = bool_series(packet["sign_stable"])
    k1 = baseline["K1"].to_numpy(float)
    sigma = (upper - lower) / 2.0
    covariance = diag_covariance_from_sigma(sigma)

    rows = []
    for mapping_name, x_values in mapping_set(z, packet_x).items():
        models = []
        models.append(
            {
                "Model": "K2_LOCKED_RHO4",
                "Prediction": k2_from_k1(x_values, k1, rho=4.0),
                "ParameterCount": 0,
                "rho": 4.0,
                "Notes": "fixed_rho4_locked_prediction",
            }
        )
        grid = best_k2_grid(x_values, k1, y, lower, upper, stable, covariance, sigma)
        models.append(
            {
                "Model": "K2_LOCKED_GRID_WITHIN_3_4",
                "Prediction": grid["prediction"],
                "ParameterCount": 1,
                "rho": grid["rho"],
                "Notes": "best_bounded_grid_point_no_rho_gt_4",
            }
        )
        models.extend(
            [
                {
                    "Model": "K1_NO_MEMORY",
                    "Prediction": null_no_memory(k1),
                    "ParameterCount": 0,
                    "rho": None,
                    "Notes": "frozen_k1_no_memory_control",
                },
                {
                    "Model": "POLY_DEG2",
                    "Prediction": polynomial_fit(x_values, y, degree=2),
                    "ParameterCount": 3,
                    "rho": None,
                    "Notes": "fixed_degree_polynomial_null",
                },
                {
                    "Model": "POLY_DEG3",
                    "Prediction": polynomial_fit(x_values, y, degree=3),
                    "ParameterCount": 4,
                    "rho": None,
                    "Notes": "fixed_degree_polynomial_null",
                },
                {
                    "Model": "SIGN_RANDOMIZED_CONTROL",
                    "Prediction": sign_randomized_control(y, seed=0),
                    "ParameterCount": 0,
                    "rho": None,
                    "Notes": "fixed_seed_sign_control",
                },
                {
                    "Model": "COORDINATE_REMAP_CONTROL",
                    "Prediction": coordinate_remap_control(x_values, k1, rho=4.0, alpha=1.2),
                    "ParameterCount": 1,
                    "rho": 4.0,
                    "Notes": "fixed_alpha_1p2_coordinate_remap_control",
                },
            ]
        )

        scored = []
        for model in models:
            score = score_model(
                model["Prediction"],
                y,
                lower,
                upper,
                stable,
                covariance,
                sigma,
                model["rho"],
                int(model["ParameterCount"]),
            )
            scored.append({**model, **score})

        k2_ref = next(item for item in scored if item["Model"] == "K2_LOCKED_RHO4")
        for item in scored:
            rows.append(
                {
                    "Dataset": "SN_BAO_NO_DEGREE4_CURRENT",
                    "Mapping": mapping_name,
                    "Model": item["Model"],
                    "ParameterCount": item["ParameterCount"],
                    "rho": "" if item["rho"] is None else f"{float(item['rho']):.6f}",
                    "p": 3 if item["Model"].startswith("K2") else "",
                    "EnvelopeFraction": f"{item['EnvelopeFraction']:.10f}",
                    "SignStableViolations": item["SignStableViolations"],
                    "Chi2DiagProxy": f"{item['Chi2DiagProxy']:.12g}",
                    "AIC": f"{item['AIC']:.12g}",
                    "BIC": f"{item['BIC']:.12g}",
                    "DeltaAIC_vs_K2": f"{(item['AIC'] - k2_ref['AIC']):.12g}",
                    "DeltaBIC_vs_K2": f"{(item['BIC'] - k2_ref['BIC']):.12g}",
                    "MaxAbsDiagResidual": f"{item['MaxAbsDiagResidual']:.12g}",
                    "Status": item["Status"],
                    "Notes": item["Notes"],
                }
            )

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
