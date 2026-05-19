#!/usr/bin/env python3
"""Run a structured PySR criteria-set-3 smoke diagnosis.

This is the second smoke layer after the basic runtime check. It keeps the
registered criteria-set-3 rule intact, but also audits whether the constant
winner is a real shape result or a complexity-penalty artifact.

No output from this script may be used as measurement validation.
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

OUT_HOF = EVIDENCE / "pysr_criteria3_structured_hall_of_fame.csv"
OUT_PENALTY = EVIDENCE / "pysr_criteria3_structured_penalty_sensitivity.csv"
OUT_SUMMARY = EVIDENCE / "pysr_criteria3_structured_smoke_summary.csv"
OUT_SELECTED = DATA / "pysr_criteria3_structured_selection_metadata.csv"
OUT_RECON_STRICT = DATA / "pysr_criteria3_structured_strict_reconstruction_vector.csv"
OUT_RECON_NONCONST = DATA / "pysr_criteria3_structured_nonconstant_diagnostic_vector.csv"
OUT_DOC = DOCS / "pysr_criteria3_structured_smoke.md"

CLAIM_BOUNDARY = "pysr_criteria3_structured_smoke_no_measurement_validation"


def finite_derivatives(fn, z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    z = np.asarray(z, dtype=float)
    span = float(np.max(z) - np.min(z))
    eps = max(span * 1.0e-4, 1.0e-5)
    z_minus = np.maximum(z - eps, 1.0e-8)
    y_plus = fn(z + eps)
    y = fn(z)
    y_minus = fn(z_minus)
    first = (y_plus - y_minus) / ((z + eps) - z_minus)
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


def score_expression(row: pd.Series, z: np.ndarray, y: np.ndarray, sigma: np.ndarray, y_mean: float, y_scale: float) -> dict:
    expr, fn_std = expression_callable(row["sympy_format"])

    def fn_unscaled(values: np.ndarray) -> np.ndarray:
        return y_mean + y_scale * fn_std(values)

    pred = fn_unscaled(z)
    finite = bool(np.all(np.isfinite(pred)))
    if not finite:
        return {
            "FinitePrediction": False,
            "WeightedMSEOriginal": np.inf,
            "RMSEOriginal": np.inf,
            "MeanAbsResidualOverSigma": np.inf,
            "PredictionStd": np.nan,
            "SympyExpression": str(expr),
        }
    residual = y - pred
    return {
        "FinitePrediction": True,
        "WeightedMSEOriginal": float(np.mean((residual / np.maximum(sigma, 1.0e-12)) ** 2)),
        "RMSEOriginal": float(np.sqrt(np.mean(residual**2))),
        "MeanAbsResidualOverSigma": float(np.mean(np.abs(residual / np.maximum(sigma, 1.0e-12)))),
        "PredictionStd": float(np.std(pred)),
        "SympyExpression": str(expr),
    }


def export_reconstruction(
    row: pd.Series,
    route_id: str,
    out_path: Path,
    z: np.ndarray,
    y: np.ndarray,
    sigma: np.ndarray,
    y_mean: float,
    y_scale: float,
) -> None:
    _, fn_std = expression_callable(row["sympy_format"])

    def fn_unscaled(values: np.ndarray) -> np.ndarray:
        return y_mean + y_scale * fn_std(values)

    pred = fn_unscaled(z)
    first, second = finite_derivatives(fn_unscaled, z)
    residual = y - pred
    pd.DataFrame(
        {
            "RouteID": route_id,
            "z": z,
            "H_D_proxy": pred,
            "H_D_prime_proxy": first,
            "H_D_double_prime_proxy": second,
            "TrainingTarget_Hrs_over_c_proxy": y,
            "TrainingSigma": sigma,
            "Residual": residual,
            "ResidualOverSigma": residual / np.maximum(sigma, 1.0e-12),
            "SelectionRole": row["SelectionRole"],
            "Source": str(BAO_INPUT.relative_to(ROOT)),
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    ).to_csv(out_path, index=False)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(BAO_INPUT).sort_values("z").reset_index(drop=True)
    z = df["z"].to_numpy(dtype=float)
    y = df["Hrs_over_c_proxy"].to_numpy(dtype=float)
    sigma = df["Hrs_over_c_sigma_proxy"].to_numpy(dtype=float)

    y_mean = float(np.mean(y))
    y_scale = float(np.std(y))
    if y_scale <= 0:
        raise ValueError("non-positive target scale")
    y_std = (y - y_mean) / y_scale
    weights = 1.0 / np.maximum(sigma / y_scale, 1.0e-12)

    model = PySRRegressor(
        niterations=48,
        populations=8,
        population_size=24,
        maxsize=18,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["square", "sqrt", "log", "exp"],
        constraints={"sqrt": 6, "log": 6, "exp": 6, "/": (-1, 6)},
        nested_constraints={"exp": {"exp": 0}, "log": {"log": 0}, "sqrt": {"sqrt": 0}},
        model_selection="accuracy",
        random_state=11,
        deterministic=True,
        parallelism="serial",
        verbosity=0,
        progress=False,
        temp_equation_file=True,
    )
    model.fit(z.reshape(-1, 1), y_std, weights=weights)

    hof = model.equations_.copy()
    if hof.empty:
        raise RuntimeError("PySR returned an empty hall of fame")
    hof["criteria3_penalty"] = 1.0
    hof["criteria3_score"] = hof["loss"].astype(float) + hof["complexity"].astype(float)
    hof["IsConstant"] = hof["complexity"].astype(int).le(1)
    metrics = [
        score_expression(row, z, y, sigma, y_mean, y_scale)
        for _, row in hof.iterrows()
    ]
    hof = pd.concat([hof.reset_index(drop=True), pd.DataFrame(metrics)], axis=1)
    hof["ClaimBoundary"] = CLAIM_BOUNDARY
    hof.to_csv(OUT_HOF, index=False)

    finite_hof = hof[hof["FinitePrediction"].astype(bool)].copy()
    strict = finite_hof.sort_values(["criteria3_score", "loss", "complexity"]).iloc[0].copy()
    nonconst_candidates = finite_hof[~finite_hof["IsConstant"].astype(bool)]
    if nonconst_candidates.empty:
        best_nonconst = strict.copy()
    else:
        best_nonconst = nonconst_candidates.sort_values(["loss", "complexity"]).iloc[0].copy()

    strict["SelectionRole"] = "STRICT_CRITERIA3_LOSS_PLUS_COMPLEXITY"
    best_nonconst["SelectionRole"] = "BEST_NONCONSTANT_DIAGNOSTIC_NOT_A_LOCKED_SELECTION"
    export_reconstruction(
        strict,
        "PYSR_CRITERIA_SET_3_STRUCTURED_STRICT_V1",
        OUT_RECON_STRICT,
        z,
        y,
        sigma,
        y_mean,
        y_scale,
    )
    export_reconstruction(
        best_nonconst,
        "PYSR_CRITERIA_SET_3_STRUCTURED_NONCONSTANT_DIAGNOSTIC_V1",
        OUT_RECON_NONCONST,
        z,
        y,
        sigma,
        y_mean,
        y_scale,
    )

    penalty_rows = []
    for penalty in [0.0, 0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0]:
        tmp = finite_hof.copy()
        tmp["Penalty"] = penalty
        tmp["PenaltyScore"] = tmp["loss"].astype(float) + penalty * tmp["complexity"].astype(float)
        selected = tmp.sort_values(["PenaltyScore", "loss", "complexity"]).iloc[0]
        penalty_rows.append(
            {
                "Penalty": penalty,
                "SelectedEquation": selected["equation"],
                "SelectedLoss": float(selected["loss"]),
                "SelectedComplexity": int(selected["complexity"]),
                "SelectedIsConstant": bool(selected["IsConstant"]),
                "SelectedWeightedMSEOriginal": float(selected["WeightedMSEOriginal"]),
                "SelectedPredictionStd": float(selected["PredictionStd"]),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    pd.DataFrame(penalty_rows).to_csv(OUT_PENALTY, index=False)

    loss_improvement = float(strict["loss"] - best_nonconst["loss"])
    weighted_mse_improvement = float(strict["WeightedMSEOriginal"] - best_nonconst["WeightedMSEOriginal"])
    constant_selected_by_strict = bool(strict["IsConstant"])
    nonconstant_available = not nonconst_candidates.empty
    structured_status = (
        "STRICT_CRITERIA3_SELECTS_CONSTANT_NONCONSTANT_SHAPE_AVAILABLE"
        if constant_selected_by_strict and nonconstant_available
        else "STRICT_CRITERIA3_STRUCTURED_SMOKE_EXECUTED"
    )
    summary = pd.DataFrame(
        [
            {
                "RouteID": "PYSR_CRITERIA_SET_3_STRUCTURED_SMOKE_V1",
                "HallOfFameRows": int(len(hof)),
                "FiniteRows": int(len(finite_hof)),
                "NonconstantRows": int(len(nonconst_candidates)),
                "StrictSelectedEquation": str(strict["equation"]),
                "StrictSelectedComplexity": int(strict["complexity"]),
                "StrictSelectedLoss": float(strict["loss"]),
                "StrictSelectedIsConstant": constant_selected_by_strict,
                "StrictWeightedMSEOriginal": float(strict["WeightedMSEOriginal"]),
                "BestNonconstantEquation": str(best_nonconst["equation"]),
                "BestNonconstantComplexity": int(best_nonconst["complexity"]),
                "BestNonconstantLoss": float(best_nonconst["loss"]),
                "BestNonconstantWeightedMSEOriginal": float(best_nonconst["WeightedMSEOriginal"]),
                "LossImprovementNonconstantVsStrict": loss_improvement,
                "WeightedMSEImprovementNonconstantVsStrict": weighted_mse_improvement,
                "PenaltyOneSelectsConstant": constant_selected_by_strict,
                "NonconstantShapeAvailable": nonconstant_available,
                "K2KernelChanged": False,
                "RhoGreaterThan4Allowed": False,
                "K1Refit": False,
                "TargetSignGateUsed": False,
                "AmplitudeFitUsed": False,
                "BootstrapScale": False,
                "SourceNativeCovarianceReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": structured_status,
                "StrongestAllowedClaim": (
                    "the structured PySR smoke route executed and separated the strict criteria-set-3 selection from nonconstant diagnostic candidates"
                ),
                "PrimaryResidualRisk": (
                    "strict penalty-one criteria selects a constant in this smoke run, so source-native shape reconstruction still requires registered bootstrap-scale execution or criteria governance"
                ),
                "NextAction": (
                    "run registered bootstrap-scale criteria-set-3 and decide whether the upstream penalty convention needs source-native normalization before scoring"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    selected_rows = pd.DataFrame([strict, best_nonconst])
    selected_rows.to_csv(OUT_SELECTED, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# PySR Criteria-Set-3 Structured Smoke",
                "",
                f"Status: {structured_status}.",
                "",
                "This run keeps the strict criteria-set-3 rule intact while separately auditing nonconstant candidates. It is a shape-diagnosis smoke run, not measurement validation.",
                "",
                "## Strict Selection",
                "",
                f"- Equation: `{strict['equation']}`",
                f"- Complexity: {int(strict['complexity'])}",
                f"- Loss: {float(strict['loss'])}",
                f"- Original weighted MSE: {float(strict['WeightedMSEOriginal'])}",
                "",
                "## Best Nonconstant Diagnostic Candidate",
                "",
                f"- Equation: `{best_nonconst['equation']}`",
                f"- Complexity: {int(best_nonconst['complexity'])}",
                f"- Loss: {float(best_nonconst['loss'])}",
                f"- Original weighted MSE: {float(best_nonconst['WeightedMSEOriginal'])}",
                "",
                "## Interpretation Boundary",
                "",
                "The nonconstant candidate is diagnostic only. It is not a replacement for the strict criteria-set-3 selection and does not authorize measurement language.",
                "",
                "## Next Action",
                "",
                "Run bootstrap-scale criteria-set-3 or resolve whether the upstream penalty convention must be normalized before source-native scoring.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_HOF.relative_to(ROOT)}")
    print(f"Wrote {OUT_PENALTY.relative_to(ROOT)}")
    print(f"Wrote {OUT_RECON_STRICT.relative_to(ROOT)}")
    print(f"Wrote {OUT_RECON_NONCONST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
