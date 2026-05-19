#!/usr/bin/env python3
"""Diagnose which rows drive null-model dominance under diagonal proxy scoring."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.benchmark import bool_series, mapping_set, model_predictions

PACKET = ROOT / "evidence" / "diagnostic_point_audit.csv"
BASELINE = ROOT / "frozen" / "k1_baseline_v1.csv"
AUDIT_OUT = ROOT / "evidence" / "null_dominance_audit.csv"
SUMMARY_OUT = ROOT / "evidence" / "null_dominance_summary.csv"


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
        for model in model_predictions(x_values, k1, target):
            pred = np.asarray(model["Prediction"], dtype=float)
            residual = target - pred
            residual_over_sigma = residual / sigma
            chi2_contribution = residual_over_sigma**2
            order = np.argsort(-chi2_contribution)
            rank = np.empty_like(order)
            rank[order] = np.arange(1, len(order) + 1)
            inside = (pred >= lower) & (pred <= upper)
            sign_violation = stable & (np.sign(pred) != np.sign(target))
            for i in range(len(packet)):
                rows.append(
                    {
                        "Dataset": "SN_BAO_NO_DEGREE4_CURRENT",
                        "MappingID": mapping_id,
                        "ModelID": model["Model"],
                        "z": f"{z[i]:.6f}",
                        "x": f"{x_values[i]:.12g}",
                        "target_median": f"{target[i]:.12g}",
                        "target_p16": f"{lower[i]:.12g}",
                        "target_p84": f"{upper[i]:.12g}",
                        "sigma_diag": f"{sigma[i]:.12g}",
                        "prediction": f"{pred[i]:.12g}",
                        "residual": f"{residual[i]:.12g}",
                        "residual_over_sigma": f"{residual_over_sigma[i]:.12g}",
                        "chi2_contribution": f"{chi2_contribution[i]:.12g}",
                        "inside_envelope": bool(inside[i]),
                        "sign_stable": bool(stable[i]),
                        "sign_violation": bool(sign_violation[i]),
                        "ContributionRank": int(rank[i]),
                        "Notes": model["Notes"],
                    }
                )

    audit = pd.DataFrame(rows)
    audit.to_csv(AUDIT_OUT, index=False)

    summary = (
        audit.assign(chi2_contribution=lambda df: df["chi2_contribution"].astype(float))
        .groupby(["MappingID", "ModelID"], sort=False)
        .agg(
            Chi2DiagProxy=("chi2_contribution", "sum"),
            MaxContribution=("chi2_contribution", "max"),
            TopContributionZ=("z", lambda s: s.iloc[audit.loc[s.index, "chi2_contribution"].astype(float).argmax()]),
            EnvelopeBreaches=("inside_envelope", lambda s: int((~s.astype(bool)).sum())),
            SignViolations=("sign_violation", lambda s: int(s.astype(bool).sum())),
        )
        .reset_index()
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    print(f"Wrote {AUDIT_OUT}")
    print(f"Wrote {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
