#!/usr/bin/env python3
"""Build a DESI DR2 BAO baseline from the public iminuit best-fit file."""

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

BESTFIT = ROOT / "data" / "public_ingest" / "desi_dr2_bestfit" / "base_desi_bao_all" / "bestfit.minimum.txt"
MEAN = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
COV = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"

OUT_ROWS = ROOT / "evidence" / "desi_bestfit_bao_baseline_export.csv"
OUT_SUMMARY = ROOT / "evidence" / "desi_bestfit_bao_baseline_summary.csv"


def _load_bestfit(path: Path) -> dict[str, float]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    header = lines[0].lstrip("#").split()
    values = lines[1].split()
    parsed = dict(zip(header, map(float, values)))
    h0 = parsed["H0rdrag"] / parsed["rdrag"]
    return {
        "baseline_id": "DESI_DR2_BASE_DESI_BAO_ALL_IMINUIT_BESTFIT_V0",
        "H0": h0,
        "omega_m": parsed["omegam"],
        "rd_mpc": parsed["rdrag"],
        "chi2_bao_reported": parsed["chi2__BAO"],
        "minuslogpost": parsed["minuslogpost"],
    }


def main() -> None:
    baseline = _load_bestfit(BESTFIT)
    mean = load_bao_mean(MEAN)
    cov = load_square_covariance(COV)
    rows, residual_cov = bao_log_residual_transform(mean, cov, "DESI_DR2_BAO_ALL_GAUSSIAN", baseline=baseline)
    rows["TransformStatus"] = "PUBLIC_BESTFIT_BASELINE_PREFLIGHT_NOT_K2_SCORE"
    rows["ClaimBoundary"] = "public_bestfit_baseline_export_not_finite_memory_validation"
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
                "ReportedChi2BAO": baseline["chi2_bao_reported"],
                "RecomputedChi2BAO": c2,
                "Chi2Difference": c2 - baseline["chi2_bao_reported"],
                "AICZeroResidual": aic(c2, 0),
                "BICZeroResidual": bic(c2, 0, len(rows)),
                "MeanAbsLogResidual": float(np.mean(np.abs(y))),
                "MaxAbsLogResidual": float(np.max(np.abs(y))),
                "AllowedForMeasurementGate": False,
                "BlockingIssue": "baseline_export_available_but_k1_and_k2_null_benchmark_not_registered",
                "Interpretation": "public_bestfit_baseline_export_preflight",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_ROWS}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
