#!/usr/bin/env python3
"""Run the normalized criteria-set-3 H_D branch at 200 bootstraps."""

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

OUT_SELECTIONS = DATA / "h_branch_normalized_criteria3_bootstrap_200_selection_metadata.csv"
OUT_SAMPLES = DATA / "h_branch_normalized_criteria3_bootstrap_200_samples.csv"
OUT_VECTOR = DATA / "h_branch_normalized_criteria3_bootstrap_200_reconstruction_vector.csv"
OUT_COV = DATA / "h_branch_normalized_criteria3_bootstrap_200_covariance.csv"
OUT_SUMMARY = EVIDENCE / "h_branch_normalized_criteria3_bootstrap_200_summary.csv"
OUT_DOC = DOCS / "h_branch_normalized_criteria3_bootstrap_200.md"

CLAIM_BOUNDARY = "h_branch_normalized_criteria3_bootstrap_200_no_measurement_validation"
BOOTSTRAP_RUNS = 200


def expression_callable(sympy_expr: object):
    x0 = sp.Symbol("x0")
    expr = sp.sympify(sympy_expr)
    fn = sp.lambdify(x0, expr, modules=["numpy"])

    def wrapped(z: np.ndarray) -> np.ndarray:
        return np.asarray(fn(np.asarray(z, dtype=float)), dtype=float)

    return expr, wrapped


def finite_derivatives(fn, z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    z = np.asarray(z, dtype=float)
    span = float(np.max(z) - np.min(z))
    eps = max(span * 1.0e-4, 1.0e-5)
    z_minus = np.maximum(z - eps, 1.0e-8)
    y_plus = np.asarray(fn(z + eps), dtype=float)
    y = np.asarray(fn(z), dtype=float)
    y_minus = np.asarray(fn(z_minus), dtype=float)
    if y_plus.ndim == 0:
        y_plus = np.full_like(z, float(y_plus))
    if y.ndim == 0:
        y = np.full_like(z, float(y))
    if y_minus.ndim == 0:
        y_minus = np.full_like(z, float(y_minus))
    first = (y_plus - y_minus) / ((z + eps) - z_minus)
    second = (y_plus - 2.0 * y + y_minus) / (eps**2)
    return first, second


def fit_hof(z_train: np.ndarray, y_train: np.ndarray, sigma_train: np.ndarray, seed: int) -> pd.DataFrame:
    y_mean = float(np.mean(y_train))
    y_scale = float(np.std(y_train))
    if y_scale <= 0:
        y_scale = 1.0
    y_std = (y_train - y_mean) / y_scale
    weights = 1.0 / np.maximum(sigma_train / y_scale, 1.0e-12)

    model = PySRRegressor(
        niterations=32,
        populations=6,
        population_size=20,
        maxsize=16,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["square", "sqrt", "log", "exp"],
        constraints={"sqrt": 6, "log": 6, "exp": 6, "/": (-1, 6)},
        nested_constraints={"exp": {"exp": 0}, "log": {"log": 0}, "sqrt": {"sqrt": 0}},
        model_selection="accuracy",
        random_state=seed,
        deterministic=True,
        parallelism="serial",
        verbosity=0,
        progress=False,
        temp_equation_file=True,
    )
    model.fit(z_train.reshape(-1, 1), y_std, weights=weights)
    hof = model.equations_.copy()
    hof["y_mean"] = y_mean
    hof["y_scale"] = y_scale
    return hof


def select_normalized(hof: pd.DataFrame, n_eff: int) -> pd.Series:
    if hof.empty:
        raise RuntimeError("empty hall of fame")
    tmp = hof.copy()
    tmp["IsConstant"] = tmp["complexity"].astype(int).le(1)
    constants = tmp[tmp["IsConstant"]].sort_values(["loss", "complexity"])
    constant_loss = float(constants.iloc[0]["loss"]) if not constants.empty else float(tmp["loss"].max())
    if constant_loss <= 0:
        constant_loss = float(tmp["loss"].max() or 1.0)
    tmp["NormalizedLossRatio"] = tmp["loss"].astype(float) / constant_loss
    tmp["NormalizedComplexityCost"] = (tmp["complexity"].astype(float) - 1.0) / float(n_eff)
    tmp["NormalizedCriteria3Score"] = tmp["NormalizedLossRatio"] + tmp["NormalizedComplexityCost"]
    tmp["LossConstantBaseline"] = constant_loss
    return tmp.sort_values(["NormalizedCriteria3Score", "NormalizedLossRatio", "complexity"]).iloc[0]


def unscaled_callable(row: pd.Series):
    expr, fn_std = expression_callable(row["sympy_format"])
    y_mean = float(row["y_mean"])
    y_scale = float(row["y_scale"])

    def fn(values: np.ndarray) -> np.ndarray:
        return y_mean + y_scale * fn_std(values)

    return expr, fn


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(BAO_INPUT).sort_values("z").reset_index(drop=True)
    z_grid = np.sort(df["z"].unique().astype(float))
    z_all = df["z"].to_numpy(dtype=float)
    y_all = df["Hrs_over_c_proxy"].to_numpy(dtype=float)
    sigma_all = df["Hrs_over_c_sigma_proxy"].to_numpy(dtype=float)

    rng = np.random.default_rng(20260522)
    selection_rows: list[dict[str, object]] = []
    sample_rows: list[dict[str, object]] = []

    for run_idx in range(BOOTSTRAP_RUNS):
        indices = rng.integers(0, len(df), size=len(df))
        order = np.argsort(z_all[indices])
        z_train = z_all[indices][order]
        y_train = y_all[indices][order]
        sigma_train = sigma_all[indices][order]

        hof = fit_hof(z_train, y_train, sigma_train, seed=701 + run_idx)
        selected = select_normalized(hof, n_eff=len(z_train))
        expr, fn = unscaled_callable(selected)
        pred = np.asarray(fn(z_grid), dtype=float)
        if pred.ndim == 0:
            pred = np.full_like(z_grid, float(pred))
        first, second = finite_derivatives(fn, z_grid)
        finite_pred = bool(np.all(np.isfinite(pred)) and np.all(np.isfinite(first)) and np.all(np.isfinite(second)))

        selection_rows.append(
            {
                "RouteID": "H_BRANCH_NORMALIZED_CRITERIA3_BOOTSTRAP_200_V1",
                "BootstrapIndex": run_idx,
                "SelectedEquation": selected["equation"],
                "SelectedSympyExpression": str(expr),
                "SelectedComplexity": int(selected["complexity"]),
                "SelectedLoss": float(selected["loss"]),
                "SelectedIsConstant": bool(selected["complexity"] <= 1),
                "NormalizedCriteria3Score": float(selected["NormalizedCriteria3Score"]),
                "NormalizedLossRatio": float(selected["NormalizedLossRatio"]),
                "NormalizedComplexityCost": float(selected["NormalizedComplexityCost"]),
                "LossConstantBaseline": float(selected["LossConstantBaseline"]),
                "FinitePrediction": finite_pred,
                "K2KernelChanged": False,
                "RhoGreaterThan4Allowed": False,
                "K1Refit": False,
                "TargetSignGateUsed": False,
                "AmplitudeFitUsed": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

        for z, value, d1, d2 in zip(z_grid, pred, first, second):
            sample_rows.append(
                {
                    "RouteID": "H_BRANCH_NORMALIZED_CRITERIA3_BOOTSTRAP_200_V1",
                    "BootstrapIndex": run_idx,
                    "z": float(z),
                    "H_D_proxy": float(value),
                    "H_D_prime_proxy": float(d1),
                    "H_D_double_prime_proxy": float(d2),
                    "FinitePrediction": finite_pred,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )

    selections = pd.DataFrame(selection_rows)
    samples = pd.DataFrame(sample_rows)
    selections.to_csv(OUT_SELECTIONS, index=False)
    samples.to_csv(OUT_SAMPLES, index=False)

    vector = samples.groupby("z", as_index=False).agg(
        H_D_proxy_median=("H_D_proxy", "median"),
        H_D_proxy_p16=("H_D_proxy", lambda s: float(np.percentile(s, 16))),
        H_D_proxy_p84=("H_D_proxy", lambda s: float(np.percentile(s, 84))),
        H_D_prime_proxy_median=("H_D_prime_proxy", "median"),
        H_D_double_prime_proxy_median=("H_D_double_prime_proxy", "median"),
        FiniteSamples=("FinitePrediction", "sum"),
    )
    vector["BootstrapSamples"] = BOOTSTRAP_RUNS
    vector["Source"] = str(BAO_INPUT.relative_to(ROOT))
    vector["ClaimBoundary"] = CLAIM_BOUNDARY
    vector.to_csv(OUT_VECTOR, index=False)

    pivot = samples.pivot_table(index="BootstrapIndex", columns="z", values="H_D_proxy", aggfunc="first")
    cov = np.cov(pivot.to_numpy(dtype=float), rowvar=False)
    cov_df = pd.DataFrame(cov, columns=[f"z_{z:.6g}" for z in pivot.columns])
    cov_df.insert(0, "CovRow", [f"z_{z:.6g}" for z in pivot.columns])
    cov_df["ClaimBoundary"] = CLAIM_BOUNDARY
    cov_df.to_csv(OUT_COV, index=False)

    finite_runs = int(selections["FinitePrediction"].astype(bool).sum())
    nonconstant_runs = int((~selections["SelectedIsConstant"].astype(bool)).sum())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "H_BRANCH_NORMALIZED_CRITERIA3_BOOTSTRAP_200_V1",
                "BootstrapRuns": BOOTSTRAP_RUNS,
                "FiniteRuns": finite_runs,
                "NonconstantSelectedRuns": nonconstant_runs,
                "UniqueSelectedEquations": int(selections["SelectedEquation"].nunique()),
                "GridRows": int(len(z_grid)),
                "MedianSelectedComplexity": float(selections["SelectedComplexity"].median()),
                "MedianNormalizedCriteria3Score": float(selections["NormalizedCriteria3Score"].median()),
                "MedianHDBandWidth": float((vector["H_D_proxy_p84"] - vector["H_D_proxy_p16"]).median()),
                "CovarianceReady": bool(cov.shape[0] == len(z_grid) and np.all(np.isfinite(cov))),
                "FullBootstrapScale": True,
                "RequiredBootstrapScale": 200,
                "SourceNativeCovarianceReady": False,
                "K2KernelChanged": False,
                "RhoGreaterThan4Allowed": False,
                "K1Refit": False,
                "TargetSignGateUsed": False,
                "AmplitudeFitUsed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "H_BRANCH_NORMALIZED_CRITERIA3_BOOTSTRAP_200_EXECUTED",
                "StrongestAllowedClaim": (
                    "the normalized criteria-set-3 H_D branch is stable at 200 bootstrap preflight scale"
                ),
                "PrimaryResidualRisk": (
                    "this is a preflight proxy export and does not replace source-native BAO covariance"
                ),
                "NextAction": (
                    "combine the 200-bootstrap H_D branch with the 200-bootstrap regularized D branch"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# H-Branch Normalized Criteria-Set-3 Bootstrap 200",
                "",
                "Status: H_BRANCH_NORMALIZED_CRITERIA3_BOOTSTRAP_200_EXECUTED.",
                "",
                "This run scales the normalized criteria-set-3 H_D branch to 200 bootstrap samples. It does not use K2, K1, target signs, amplitude fitting, or measurement-validation language.",
                "",
                "## Result",
                "",
                f"- Bootstrap runs: {BOOTSTRAP_RUNS}",
                f"- Finite runs: {finite_runs}",
                f"- Nonconstant selected runs: {nonconstant_runs}",
                f"- Covariance ready: {bool(cov.shape[0] == len(z_grid) and np.all(np.isfinite(cov)))}",
                "",
                "## Boundary",
                "",
                "This is a preflight H_D branch scale-up only. It is not measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_VECTOR.relative_to(ROOT)}")
    print(f"Wrote {OUT_COV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
