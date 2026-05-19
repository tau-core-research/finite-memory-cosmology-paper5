#!/usr/bin/env python3
"""Run model scorecards on all/sign/depth subsets."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.benchmark import bool_series, depth_masks, mapping_set, model_predictions
from fmc.gates import classify_gate, envelope_fraction, sign_stable_violations
from fmc.likelihood import aic, bic, chi2, diag_covariance_from_sigma

PACKET = ROOT / "evidence" / "diagnostic_point_audit.csv"
BASELINE = ROOT / "frozen" / "k1_baseline_v1.csv"
OUT = ROOT / "evidence" / "subset_model_scorecard.csv"


def subset_masks(stable: np.ndarray, x_values: np.ndarray) -> dict[str, np.ndarray]:
    masks = {
        "all_points": np.ones_like(stable, dtype=bool),
        "sign_stable_only": stable,
        "sign_unstable_only": ~stable,
    }
    masks.update(depth_masks(x_values))
    return masks


def main() -> None:
    packet = pd.read_csv(PACKET)
    baseline = pd.read_csv(BASELINE)
    z = packet["z"].to_numpy(float)
    packet_x = packet["x"].to_numpy(float)
    target = packet["target_median"].to_numpy(float)
    lower = packet["target_p16"].to_numpy(float)
    upper = packet["target_p84"].to_numpy(float)
    stable = bool_series(packet["sign_stable"])
    k1 = baseline["K1"].to_numpy(float)
    sigma = (upper - lower) / 2.0

    rows = []
    for mapping_id, x_values in mapping_set(z, packet_x).items():
        for subset_id, mask in subset_masks(stable, x_values).items():
            if int(mask.sum()) < 2:
                continue
            y_s = target[mask]
            lo_s = lower[mask]
            hi_s = upper[mask]
            stable_s = stable[mask]
            cov_s = diag_covariance_from_sigma(sigma[mask])
            for model in model_predictions(x_values, k1, target):
                pred_s = np.asarray(model["Prediction"], dtype=float)[mask]
                diag_residual = np.abs((y_s - pred_s) / sigma[mask])
                c2 = chi2(y_s, pred_s, cov_s)
                env = envelope_fraction(pred_s, lo_s, hi_s)
                violations = sign_stable_violations(pred_s, y_s, stable_s)
                k = int(model["ParameterCount"])
                rows.append(
                    {
                        "Dataset": "SN_BAO_NO_DEGREE4_CURRENT",
                        "Mapping": mapping_id,
                        "Subset": subset_id,
                        "N": int(mask.sum()),
                        "Model": model["Model"],
                        "ParameterCount": k,
                        "Chi2DiagProxy": f"{c2:.12g}",
                        "AIC": f"{aic(c2, k):.12g}",
                        "BIC": f"{bic(c2, k, int(mask.sum())):.12g}",
                        "MaxAbsDiagResidual": f"{float(np.max(diag_residual)):.12g}",
                        "EnvelopeFraction": f"{env:.10f}",
                        "SignStableViolations": violations,
                        "Status": classify_gate(env, violations, max_abs_residual=float(np.max(diag_residual)), rho=model["rho"]),
                    }
                )

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
