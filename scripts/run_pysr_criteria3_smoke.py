#!/usr/bin/env python3
"""Run a small PySR criteria-set-3 smoke reproduction.

The smoke route targets the upstream radial BAO H_D proxy and selects a single
symbolic expression by the registered criteria-set-3 rule:

    selection_score = loss + 1.0 * complexity

This is deliberately not a bootstrap-scale source-native reproduction. It only
checks that the local PySR route can run, select an expression, and export a
derivative-ready reconstruction vector without changing K2, refitting K1, or
authorizing measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import sympy as sp
from pysr import PySRRegressor

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

BAO_INPUT = DATA / "source_native_training_bao_hd_proxy.csv"

OUT_METADATA = DATA / "pysr_criteria3_smoke_selection_metadata.csv"
OUT_RECON = DATA / "pysr_criteria3_smoke_reconstruction_vector.csv"
OUT_HOF = EVIDENCE / "pysr_criteria3_smoke_hall_of_fame.csv"
OUT_SUMMARY = EVIDENCE / "pysr_criteria3_smoke_summary.csv"
OUT_DOC = DOCS / "pysr_criteria3_smoke.md"

CLAIM_BOUNDARY = "pysr_criteria3_smoke_no_measurement_validation"


def finite_derivatives(fn, z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compute stable finite-difference derivatives on the z grid."""
    z = np.asarray(z, dtype=float)
    span = float(np.max(z) - np.min(z))
    eps = max(span * 1.0e-4, 1.0e-5)
    y_plus = fn(z + eps)
    y_minus = fn(np.maximum(z - eps, 1.0e-8))
    y = fn(z)
    first = (y_plus - y_minus) / ((z + eps) - np.maximum(z - eps, 1.0e-8))
    second = (y_plus - 2.0 * y + y_minus) / (eps**2)
    return first, second


def expression_callable(sympy_expr: object):
    x0 = sp.Symbol("x0")
    expr = sp.sympify(sympy_expr)
    fn = sp.lambdify(x0, expr, modules=["numpy"])

    def wrapped(z: np.ndarray) -> np.ndarray:
        values = fn(np.asarray(z, dtype=float))
        return np.asarray(values, dtype=float)

    return expr, wrapped


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(BAO_INPUT).sort_values("z").reset_index(drop=True)
    z = df["z"].to_numpy(dtype=float)
    y = df["Hrs_over_c_proxy"].to_numpy(dtype=float)
    sigma = df["Hrs_over_c_sigma_proxy"].to_numpy(dtype=float)

    # Standardize target for symbolic search, then map predictions back. This
    # improves smoke-run stability without changing the selected input data.
    y_mean = float(np.mean(y))
    y_scale = float(np.std(y))
    if y_scale <= 0:
        raise ValueError("non-positive target scale")
    y_std = (y - y_mean) / y_scale

    model = PySRRegressor(
        niterations=8,
        populations=4,
        population_size=16,
        maxsize=12,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["square", "sqrt", "log", "exp"],
        constraints={"sqrt": 5, "log": 5, "exp": 5, "/": (-1, 5)},
        nested_constraints={"exp": {"exp": 0}, "log": {"log": 0}, "sqrt": {"sqrt": 0}},
        model_selection="accuracy",
        random_state=3,
        deterministic=True,
        parallelism="serial",
        verbosity=0,
        progress=False,
        temp_equation_file=True,
    )
    model.fit(z.reshape(-1, 1), y_std, weights=1.0 / np.maximum(sigma / y_scale, 1.0e-12))

    hof = model.equations_.copy()
    if hof.empty:
        raise RuntimeError("PySR returned an empty hall of fame")
    hof["criteria3_penalty"] = 1.0
    hof["criteria3_score"] = hof["loss"].astype(float) + hof["complexity"].astype(float)
    hof["ClaimBoundary"] = CLAIM_BOUNDARY
    hof.to_csv(OUT_HOF, index=False)

    selected = hof.sort_values(["criteria3_score", "loss", "complexity"]).iloc[0]
    expr, fn_std = expression_callable(selected["sympy_format"])

    def fn_unscaled(values: np.ndarray) -> np.ndarray:
        return y_mean + y_scale * fn_std(values)

    pred = fn_unscaled(z)
    first, second = finite_derivatives(fn_unscaled, z)
    residual = y - pred
    weighted_mse = float(np.mean((residual / np.maximum(sigma, 1.0e-12)) ** 2))
    rmse = float(np.sqrt(np.mean(residual**2)))

    recon = pd.DataFrame(
        {
            "RouteID": "PYSR_CRITERIA_SET_3_SMOKE_V1",
            "z": z,
            "H_D_proxy": pred,
            "H_D_prime_proxy": first,
            "H_D_double_prime_proxy": second,
            "TrainingTarget_Hrs_over_c_proxy": y,
            "TrainingSigma": sigma,
            "Residual": residual,
            "ResidualOverSigma": residual / np.maximum(sigma, 1.0e-12),
            "Source": str(BAO_INPUT.relative_to(ROOT)),
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    recon.to_csv(OUT_RECON, index=False)

    metadata = pd.DataFrame(
        [
            {
                "RouteID": "PYSR_CRITERIA_SET_3_SMOKE_V1",
                "SelectedEquation": str(selected["equation"]),
                "SelectedSympyExpression": str(expr),
                "SelectedLoss": float(selected["loss"]),
                "SelectedComplexity": int(selected["complexity"]),
                "Criteria3Penalty": 1.0,
                "Criteria3Score": float(selected["criteria3_score"]),
                "TrainingRows": int(len(df)),
                "WeightedMSE": weighted_mse,
                "RMSE": rmse,
                "K2KernelChanged": False,
                "RhoGreaterThan4Allowed": False,
                "K1Refit": False,
                "TargetSignGateUsed": False,
                "AmplitudeFitUsed": False,
                "BootstrapScale": False,
                "SourceNativeCovarianceReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "PYSR_CRITERIA3_SMOKE_EXECUTED_NO_MEASUREMENT_VALIDATION",
                "StrongestAllowedClaim": (
                    "the criteria-set-3 PySR smoke route executed and exported a derivative-ready H_D proxy vector"
                ),
                "PrimaryResidualRisk": (
                    "smoke run is not the 200-expression source-native bootstrap and has no source-native covariance"
                ),
                "NextAction": (
                    "scale this route to registered bootstrap exports and then score only with source-native covariance"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    metadata.to_csv(OUT_METADATA, index=False)
    metadata.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# PySR Criteria-Set-3 Smoke Run",
                "",
                "Status: PYSR_CRITERIA3_SMOKE_EXECUTED_NO_MEASUREMENT_VALIDATION.",
                "",
                "The local criteria-set-3 route ran on the radial BAO H_D proxy input and exported a derivative-ready reconstruction vector. This is a smoke run, not the full source-native bootstrap.",
                "",
                "## Selected Expression",
                "",
                f"- Equation: `{selected['equation']}`",
                f"- Loss: {float(selected['loss'])}",
                f"- Complexity: {int(selected['complexity'])}",
                f"- Criteria-set-3 score: {float(selected['criteria3_score'])}",
                "",
                "## Claim Boundary",
                "",
                "- K2 kernel unchanged.",
                "- No rho > 4.",
                "- No K1 refit.",
                "- No target-sign gate.",
                "- No amplitude fit.",
                "- No measurement validation.",
                "",
                "## Next Action",
                "",
                "Scale this route to the registered bootstrap export and attach source-native covariance before using it in the measurement gate.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_METADATA.relative_to(ROOT)}")
    print(f"Wrote {OUT_RECON.relative_to(ROOT)}")
    print(f"Wrote {OUT_HOF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
