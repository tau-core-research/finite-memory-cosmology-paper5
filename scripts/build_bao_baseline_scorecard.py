#!/usr/bin/env python3
"""Build a compact scorecard for BAO baseline preflight exports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "bao_baseline_scorecard.csv"


def _row(label: str, source_class: str, chi2: float, rows: int, mean_abs: float, max_abs: float, eligible: bool, issue: str) -> dict:
    return {
        "BaselineLabel": label,
        "SourceClass": source_class,
        "Rows": rows,
        "BAOChi2": chi2,
        "Chi2PerRow": chi2 / rows,
        "MeanAbsLogResidual": mean_abs,
        "MaxAbsLogResidual": max_abs,
        "AllowedForMeasurementGate": eligible,
        "BlockingIssue": issue,
    }


def main() -> None:
    rows = []

    audit = pd.read_csv(ROOT / "evidence" / "bao_residual_transform_summary.csv")
    audit_dr2 = audit[audit["ProductID"] == "DESI_DR2_BAO_ALL_GAUSSIAN"].iloc[0]
    null = pd.read_csv(ROOT / "evidence" / "bao_residual_null_benchmark.csv")
    audit_zero = null[
        (null["ProductID"] == "DESI_DR2_BAO_ALL_GAUSSIAN")
        & (null["MappingID"] == "x_z_normalized")
        & (null["ModelID"] == "ZERO_RESIDUAL_AUDIT_BASELINE")
    ].iloc[0]
    rows.append(
        _row(
            "AUDIT_FLAT_LCDM_BAO_V0",
            "audit_plumbing_baseline",
            float(audit_zero["Chi2FullCov"]),
            int(audit_dr2["Rows"]),
            float(audit_dr2["MeanAbsLogResidual"]),
            float(audit_dr2["MaxAbsLogResidual"]),
            False,
            "not_likelihood_native;not_coordinate_native",
        )
    )

    rd = pd.read_csv(ROOT / "evidence" / "bao_rd_offset_sensitivity_summary.csv")
    rd_dr2 = rd[rd["ProductID"] == "DESI_DR2_BAO_ALL_GAUSSIAN"].iloc[0]
    rows.append(
        _row(
            "AUDIT_RD_OFFSET_ABSORBED_V0",
            "same_data_scale_sensitivity",
            float(rd_dr2["Chi2ZeroResidual"]),
            int(rd_dr2["Rows"]),
            float(rd_dr2["MeanAbsLogResidual"]),
            float(rd_dr2["MaxAbsLogResidual"]),
            False,
            "rd_absorbed_from_same_data_offset",
        )
    )

    desi = pd.read_csv(ROOT / "evidence" / "desi_bestfit_bao_baseline_summary.csv").iloc[0]
    rows.append(
        _row(
            "DESI_DR2_BASE_DESI_BAO_ALL_IMINUIT_BESTFIT_V0",
            "same_data_public_bestfit",
            float(desi["RecomputedChi2BAO"]),
            int(desi["Rows"]),
            float(desi["MeanAbsLogResidual"]),
            float(desi["MaxAbsLogResidual"]),
            False,
            "same_data_posterior_maximum;k2_protocol_not_registered",
        )
    )

    cmb = pd.read_csv(ROOT / "evidence" / "cmb_only_bao_baseline_summary.csv").iloc[0]
    rows.append(
        _row(
            "CMB_ONLY_BASE_PLANCK_ACT_LENSING_IMINUIT_BESTFIT_V0",
            "independent_cmb_only_public_bestfit",
            float(cmb["PredictedBAOChi2"]),
            int(cmb["Rows"]),
            float(cmb["MeanAbsLogResidual"]),
            float(cmb["MaxAbsLogResidual"]),
            False,
            "k1_policy_not_registered;k2_protocol_not_registered",
        )
    )

    df = pd.DataFrame(rows).sort_values("BAOChi2")
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
