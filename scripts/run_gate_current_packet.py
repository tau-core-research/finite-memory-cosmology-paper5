#!/usr/bin/env python3
"""Run the current finite-memory diagnostic gate packet.

This is an MVP harness. It reproduces the current reconstruction-level
diagnostic status from the public packet and adds first null comparators. The
score is a diagonal covariance proxy, not a full covariance likelihood.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.gates import classify_gate, envelope_fraction, sign_stable_violations
from fmc.likelihood import aic, bic, chi2, diag_covariance_from_sigma
from fmc.nulls import null_no_memory, polynomial_fit
from fmc.operators import k2_from_k1

PACKET = ROOT / "evidence" / "diagnostic_point_audit.csv"
BASELINE = ROOT / "frozen" / "k1_baseline_v1.csv"
OUT = ROOT / "evidence" / "gate_results_current.csv"


def bool_series(values: pd.Series) -> np.ndarray:
    """Parse permissive boolean strings from CSV."""
    return values.astype(str).str.lower().isin(["true", "1", "yes", "y"]).to_numpy()


def main() -> None:
    packet = pd.read_csv(PACKET)
    baseline = pd.read_csv(BASELINE)

    x = packet["x"].to_numpy(float)
    y = packet["target_median"].to_numpy(float)
    lo = packet["target_p16"].to_numpy(float)
    hi = packet["target_p84"].to_numpy(float)
    k2_current = packet["k2_prediction"].to_numpy(float)
    stable = bool_series(packet["sign_stable"])
    k1 = baseline["K1"].to_numpy(float)

    sigma = (hi - lo) / 2.0
    if np.any(sigma <= 0):
        raise ValueError("diagnostic envelope produced non-positive sigma proxy")
    covariance = diag_covariance_from_sigma(sigma)

    models: list[dict[str, object]] = [
        {
            "Model": "K2_LOCKED_CURRENT",
            "Prediction": k2_from_k1(x, k1, rho=4.0),
            "K": 0,
            "Rho": 4.0,
            "Notes": "locked_prediction_reconstructed_from_frozen_k1",
        },
        {
            "Model": "NO_MEMORY_PROXY",
            "Prediction": null_no_memory(k1),
            "K": 0,
            "Rho": np.nan,
            "Notes": "no_memory_frozen_k1_comparator",
        },
    ]

    # Sanity check: the frozen K1 reconstruction should reproduce the packet K2.
    if not np.allclose(models[0]["Prediction"], k2_current, rtol=0.0, atol=1e-8):
        raise ValueError("frozen K1 baseline no longer reproduces the packet K2 prediction")

    for degree in [2, 3]:
        models.append(
            {
                "Model": f"POLY_DEG{degree}",
                "Prediction": polynomial_fit(x, y, degree=degree),
                "K": degree + 1,
                "Rho": np.nan,
                "Notes": "fixed_degree_median_fit_null",
            }
        )

    rows = []
    for model in models:
        prediction = np.asarray(model["Prediction"], dtype=float)
        diag_residual = np.abs((y - prediction) / sigma)
        max_abs_residual = float(np.max(diag_residual))
        c2 = chi2(y, prediction, covariance)
        env = envelope_fraction(prediction, lo, hi)
        violations = sign_stable_violations(prediction, y, stable)
        rho = model["Rho"]
        status = classify_gate(
            env,
            violations,
            max_abs_residual=max_abs_residual,
            rho=None if np.isnan(rho) else float(rho),
        )
        rows.append(
            {
                "GateID": "G2_SN_BAO_SIGN_STABILITY",
                "Dataset": "SN_BAO_NO_DEGREE4_CURRENT",
                "Mapping": "z_normalized_current_packet",
                "Model": model["Model"],
                "K": model["K"],
                "Rho": "" if np.isnan(rho) else f"{float(rho):.6f}",
                "Chi2DiagProxy": f"{c2:.12g}",
                "AIC": f"{aic(c2, int(model['K'])):.12g}",
                "BIC": f"{bic(c2, int(model['K']), len(y)):.12g}",
                "MaxAbsDiagResidual": f"{max_abs_residual:.12g}",
                "EnvelopeFraction": f"{env:.10f}",
                "SignStableViolations": violations,
                "CovarianceStatus": "diagonal_proxy_from_p16_p84",
                "Status": status,
                "Notes": model["Notes"],
            }
        )

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
