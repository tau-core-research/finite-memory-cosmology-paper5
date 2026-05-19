#!/usr/bin/env python3
"""Diagnose sensitivity in the full normalized-PySR smoke null."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

RECON = DATA / "full_normalized_pysr_backreaction_smoke_reconstruction_vector.csv"
OMEGA = DATA / "full_normalized_pysr_backreaction_smoke_omega_vector.csv"
ROW_AUDIT = EVIDENCE / "full_normalized_pysr_backreaction_smoke_bridge_row_audit.csv"

OUT_ROW = EVIDENCE / "full_normalized_pysr_backreaction_sensitivity_row.csv"
OUT_SUMMARY = EVIDENCE / "full_normalized_pysr_backreaction_sensitivity_summary.csv"
OUT_DOC = DOCS / "full_normalized_pysr_backreaction_sensitivity.md"

CLAIM_BOUNDARY = "full_normalized_pysr_backreaction_sensitivity_no_measurement_validation"


def zone(z: float) -> str:
    if z < 0.8:
        return "low_depth"
    if z < 1.5:
        return "mid_depth"
    return "high_depth"


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    recon = pd.read_csv(RECON)
    omega = pd.read_csv(OMEGA)
    rows = recon.merge(omega[["z", "Omega_R_plus_3Omega_Q"]], on="z", how="left")
    rows["DepthZone"] = rows["z"].map(zone)
    rows["AbsOmega"] = rows["Omega_R_plus_3Omega_Q"].abs()
    rows["AbsDSecond"] = rows["D_double_prime"].abs()
    rows["AbsDPrime"] = rows["D_prime"].abs()
    rows["DSecondOverDPrime"] = rows["AbsDSecond"] / np.maximum(rows["AbsDPrime"], 1.0e-12)
    rows["OmegaSign"] = np.sign(rows["Omega_R_plus_3Omega_Q"])
    rows["SensitivityFlag"] = np.where(
        rows["AbsOmega"] > rows["AbsOmega"].median() * 5.0,
        "HIGH_OMEGA_MAGNITUDE",
        "nominal_smoke_range",
    )
    rows["MeasurementValidationAllowed"] = False
    rows["ClaimBoundary"] = CLAIM_BOUNDARY
    rows.to_csv(OUT_ROW, index=False)

    row_audit = pd.read_csv(ROW_AUDIT)
    low = rows[rows["DepthZone"].eq("low_depth")]
    midhigh = rows[~rows["DepthZone"].eq("low_depth")]
    summary = pd.DataFrame(
        [
            {
                "AuditID": "FULL_NORMALIZED_PYSR_BACKREACTION_SENSITIVITY_V1",
                "Rows": int(len(rows)),
                "LowDepthRows": int(len(low)),
                "MidHighRows": int(len(midhigh)),
                "OmegaAbsMax": float(rows["AbsOmega"].max()),
                "LowDepthOmegaAbsMax": float(low["AbsOmega"].max()) if not low.empty else np.nan,
                "MidHighOmegaAbsMax": float(midhigh["AbsOmega"].max()) if not midhigh.empty else np.nan,
                "MedianDSecondOverDPrimeLowDepth": float(low["DSecondOverDPrime"].median()) if not low.empty else np.nan,
                "MedianDSecondOverDPrimeMidHigh": float(midhigh["DSecondOverDPrime"].median()) if not midhigh.empty else np.nan,
                "HighOmegaMagnitudeRows": int(rows["SensitivityFlag"].eq("HIGH_OMEGA_MAGNITUDE").sum()),
                "StableSignMatchesTargetRows": int(row_audit[row_audit["SignStable"].astype(bool)]["SignMatchesTarget"].astype(bool).sum()),
                "StableRows": int(row_audit["SignStable"].astype(bool).sum()),
                "K2KernelChanged": False,
                "K1Refit": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "FULL_NORMALIZED_PYSR_BACKREACTION_LOW_DEPTH_DERIVATIVE_SENSITIVITY_WARNING",
                "StrongestAllowedClaim": (
                    "the full normalized-PySR smoke null is scoreable, but its low-depth D-derivative sensitivity is high"
                ),
                "PrimaryResidualRisk": (
                    "low-depth D_second terms dominate the smoke Omega amplitude and prevent physical-null promotion"
                ),
                "NextAction": (
                    "add derivative regularity constraints or source-native D-branch governance before scaling to 200 bootstraps"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Full Normalized PySR Backreaction Sensitivity",
                "",
                "Status: FULL_NORMALIZED_PYSR_BACKREACTION_LOW_DEPTH_DERIVATIVE_SENSITIVITY_WARNING.",
                "",
                "The full D+H smoke null is scoreable, but low-depth D-branch second derivatives create a large Omega amplitude. This blocks physical-null promotion until derivative regularity is governed.",
                "",
                "## Key Numbers",
                "",
                f"- Omega abs max: {float(rows['AbsOmega'].max())}",
                f"- Low-depth Omega abs max: {float(low['AbsOmega'].max()) if not low.empty else 'nan'}",
                f"- Mid/high Omega abs max: {float(midhigh['AbsOmega'].max()) if not midhigh.empty else 'nan'}",
                "",
                "## Boundary",
                "",
                "No K2 change, no K1 refit, no scale fit, and no measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_ROW.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
