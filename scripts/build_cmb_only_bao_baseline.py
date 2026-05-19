#!/usr/bin/env python3
"""Build a BAO baseline from a public CMB-only DESI VAC best-fit."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.bao_transform import bao_log_residual_transform
from fmc.likelihood import aic, bic, chi2
from fmc.public_data import load_bao_mean, load_square_covariance

BESTFIT = ROOT / "data" / "public_ingest" / "desi_dr2_bestfit" / "base_cmb_only" / "bestfit.minimum.txt"
MEAN = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
COV = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"

OUT_ROWS = ROOT / "evidence" / "cmb_only_bao_baseline_export.csv"
OUT_SUMMARY = ROOT / "evidence" / "cmb_only_bao_baseline_summary.csv"


def _load_bestfit(path: Path) -> dict[str, float]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    header = lines[0].lstrip("#").split()
    values = lines[1].split()
    parsed = dict(zip(header, map(float, values)))
    return {
        "baseline_id": "CMB_ONLY_BASE_PLANCK_ACT_LENSING_IMINUIT_BESTFIT_V0",
        "H0": parsed["H0"],
        "omega_m": parsed["omegam"],
        "rd_mpc": parsed["rdrag"],
        "chi2_cmb_reported": parsed["chi2__CMB"],
        "minuslogpost": parsed["minuslogpost"],
    }


def main() -> None:
    baseline = _load_bestfit(BESTFIT)
    mean = load_bao_mean(MEAN)
    cov = load_square_covariance(COV)
    rows, residual_cov = bao_log_residual_transform(mean, cov, "DESI_DR2_BAO_ALL_GAUSSIAN", baseline=baseline)
    rows["TransformStatus"] = "PUBLIC_CMB_ONLY_BASELINE_PREFLIGHT_NOT_K2_SCORE"
    rows["ClaimBoundary"] = "cmb_only_baseline_export_not_finite_memory_validation"
    rows.to_csv(OUT_ROWS, index=False)

    y = rows["LogResidual"].to_numpy(float)
    zero = np.zeros_like(y)
    c2 = chi2(y, zero, residual_cov)
    summary = pd.DataFrame(
        [
            {
                "BaselineID": baseline["baseline_id"],
                "SourceFile": str(BESTFIT.relative_to(ROOT)),
                "ProductID": "DESI_DR2_BAO_ALL_GAUSSIAN",
                "Rows": len(rows),
                "H0": baseline["H0"],
                "OmegaM": baseline["omega_m"],
                "RdMpc": baseline["rd_mpc"],
                "ReportedChi2CMB": baseline["chi2_cmb_reported"],
                "PredictedBAOChi2": c2,
                "AICZeroResidual": aic(c2, 0),
                "BICZeroResidual": bic(c2, 0, len(rows)),
                "MeanAbsLogResidual": float(np.mean(np.abs(y))),
                "MaxAbsLogResidual": float(np.max(np.abs(y))),
                "AllowedForMeasurementGate": False,
                "BlockingIssue": "cmb_only_baseline_export_available_but_k1_and_k2_null_benchmark_not_registered",
                "Interpretation": "public_cmb_only_baseline_export_preflight",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_ROWS}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
