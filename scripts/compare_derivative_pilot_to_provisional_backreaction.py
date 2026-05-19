#!/usr/bin/env python3
"""Compare the public derivative pilot to the provisional BAO backreaction curve.

This is a shape/route diagnostic only. It does not select between models,
fit K2, fit K1, or authorize measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BR = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PILOT = BR / "source_native_derivative_pilot_omega_curve.csv"
PROVISIONAL = BR / "provisional_bao_backreaction_omega_curve.csv"

OUT_ROW = EVIDENCE / "source_native_derivative_pilot_bridge_comparison.csv"
OUT_SUMMARY = EVIDENCE / "source_native_derivative_pilot_bridge_comparison_summary.csv"
OUT_DOC = DOCS / "source_native_derivative_pilot_bridge_comparison.md"

CLAIM_BOUNDARY = "source_native_derivative_pilot_bridge_comparison_no_measurement_validation"


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or float(np.std(a)) == 0.0 or float(np.std(b)) == 0.0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def best_scale(y: np.ndarray, x: np.ndarray) -> float:
    denom = float(x @ x)
    if denom <= 0.0:
        return float("nan")
    return float((x @ y) / denom)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    pilot = pd.read_csv(PILOT).sort_values("z")
    provisional = pd.read_csv(PROVISIONAL).sort_values("z")

    pz = pilot["z"].to_numpy(float)
    po = pilot["Omega_R_plus_3Omega_Q"].to_numpy(float)
    z = provisional["z"].to_numpy(float)
    omega = provisional["Omega_R_plus_3Omega_Q"].to_numpy(float)

    mask = (z >= float(np.min(pz))) & (z <= float(np.max(pz)))
    compare = provisional[mask].copy()
    compare["PilotOmegaInterpolated"] = np.interp(compare["z"].to_numpy(float), pz, po)
    compare["RawDifferencePilotMinusProvisional"] = (
        compare["PilotOmegaInterpolated"].to_numpy(float) - compare["Omega_R_plus_3Omega_Q"].to_numpy(float)
    )
    compare["AbsDifference"] = compare["RawDifferencePilotMinusProvisional"].abs()
    compare["SignMatchesProvisional"] = (
        np.sign(compare["PilotOmegaInterpolated"].to_numpy(float))
        == np.sign(compare["Omega_R_plus_3Omega_Q"].to_numpy(float))
    )
    compare["WithinProvisionalOneSigma"] = (
        compare["AbsDifference"].to_numpy(float) <= compare["OmegaSigma"].to_numpy(float)
    )
    compare["AllowedForMeasurementValidation"] = False
    compare["ClaimBoundary"] = CLAIM_BOUNDARY
    compare.to_csv(OUT_ROW, index=False)

    pilot_on_grid = compare["PilotOmegaInterpolated"].to_numpy(float)
    provisional_on_grid = compare["Omega_R_plus_3Omega_Q"].to_numpy(float)
    sigma = compare["OmegaSigma"].to_numpy(float)
    diff = pilot_on_grid - provisional_on_grid
    chi2_diag = float(np.sum((diff / sigma) ** 2))
    scale = best_scale(provisional_on_grid, pilot_on_grid)
    scaled_diff = scale * pilot_on_grid - provisional_on_grid
    scaled_chi2_diag = float(np.sum((scaled_diff / sigma) ** 2))
    sign_matches = int(compare["SignMatchesProvisional"].map(bool).sum())
    one_sigma = int(compare["WithinProvisionalOneSigma"].map(bool).sum())
    rows = len(compare)

    if sign_matches == rows and one_sigma == rows:
        status = "PILOT_SHAPE_COMPATIBLE_WITH_PROVISIONAL_WITHIN_DIAGONAL_SIGMA"
    elif sign_matches >= max(1, rows // 2):
        status = "PILOT_PARTIAL_SHAPE_OVERLAP_WITH_PROVISIONAL"
    else:
        status = "PILOT_DIVERGES_FROM_PROVISIONAL_ROUTE"

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_DERIVATIVE_PILOT_BRIDGE_COMPARISON_V1",
                "RowsCompared": rows,
                "SignMatchesProvisional": sign_matches,
                "WithinProvisionalOneSigmaRows": one_sigma,
                "CorrelationPilotProvisional": corr(pilot_on_grid, provisional_on_grid),
                "DiagChi2PilotVsProvisional": chi2_diag,
                "ForbiddenBestScalePilotToProvisional": scale,
                "ScaledDiagChi2DiagnosticOnly": scaled_chi2_diag,
                "ScaleFitAllowed": False,
                "K2FitPerformed": False,
                "K1RefitPerformed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": status,
                "StrongestAllowedClaim": (
                    "the public derivative pilot can be compared against the provisional BAO backreaction route as a shape diagnostic"
                ),
                "PrimaryResidualRisk": (
                    "pilot route uses fixed polynomials and mixed SN/BAO proxy units, while provisional route uses BAO-only polynomial reconstruction"
                ),
                "NextAction": "use this divergence/overlap diagnosis to prioritize source-native symbolic-regression exports before any physical null claim",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Derivative Pilot vs Provisional Backreaction",
                "",
                "Status: route comparison diagnostic only.",
                "",
                "This compares the fixed public SN/BAO derivative pilot against the earlier provisional BAO-only backreaction curve. It is not a model-selection result and does not fit K2 or K1.",
                "",
                "## Outputs",
                "",
                f"- Row comparison: `{OUT_ROW.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
                "## Claim Boundary",
                "",
                "The comparison may reveal route sensitivity, but cannot validate or falsify the finite-memory projection hypothesis without source-native derivative families and covariance.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_ROW}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
