#!/usr/bin/env python3
"""Run a small normalized criteria-set-3 bootstrap smoke.

This script is the first bootstrap rehearsal for the source-native
backreaction route. It uses the pre-registered normalized criteria-set-3
selector and the radial BAO H_D proxy input. It is intentionally small and
does not authorize measurement validation.
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

OUT_SELECTIONS = DATA / "source_native_normalized_criteria3_bootstrap_smoke_selection_metadata.csv"
OUT_SAMPLES = DATA / "source_native_normalized_criteria3_bootstrap_smoke_samples.csv"
OUT_VECTOR = DATA / "source_native_normalized_criteria3_bootstrap_smoke_reconstruction_vector.csv"
OUT_COV = DATA / "source_native_normalized_criteria3_bootstrap_smoke_covariance.csv"
OUT_SUMMARY = EVIDENCE / "source_native_normalized_criteria3_bootstrap_smoke_summary.csv"
OUT_DOC = DOCS / "source_native_normalized_criteria3_bootstrap_smoke.md"

CLAIM_BOUNDARY = "source_native_normalized_criteria3_bootstrap_smoke_no_measurement_validation"


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
    y_plus = fn(z + eps)
    y = fn(z)
    y_minus = fn(z_minus)
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
    if constants.empty:
        constant_loss = float(tmp["loss"].max())
    else:
        constant_loss = float(constants.iloc[0]["loss"])
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

    bootstrap_runs = 12
    rng = np.random.default_rng(20260518)
    selection_rows: list[dict[str, object]] = []
    sample_rows: list[dict[str, object]] = []

    for run_idx in range(bootstrap_runs):
        indices = rng.integers(0, len(df), size=len(df))
        z_train = z_all[indices]
        y_train = y_all[indices]
        sigma_train = sigma_all[indices]
        order = np.argsort(z_train)
        z_train = z_train[order]
        y_train = y_train[order]
        sigma_train = sigma_train[order]

        hof = fit_hof(z_train, y_train, sigma_train, seed=101 + run_idx)
        selected = select_normalized(hof, n_eff=len(z_train))
        expr, fn = unscaled_callable(selected)
        pred = fn(z_grid)
        first, second = finite_derivatives(fn, z_grid)
        finite_pred = bool(np.all(np.isfinite(pred)) and np.all(np.isfinite(first)) and np.all(np.isfinite(second)))

        selection_rows.append(
            {
                "RouteID": "SOURCE_NATIVE_NORMALIZED_CRITERIA3_BOOTSTRAP_SMOKE_V1",
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
                    "RouteID": "SOURCE_NATIVE_NORMALIZED_CRITERIA3_BOOTSTRAP_SMOKE_V1",
                    "BootstrapIndex": run_idx,
                    "z": z,
                    "H_D_proxy": value,
                    "H_D_prime_proxy": d1,
                    "H_D_double_prime_proxy": d2,
                    "FinitePrediction": finite_pred,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )

    selections = pd.DataFrame(selection_rows)
    samples = pd.DataFrame(sample_rows)
    selections.to_csv(OUT_SELECTIONS, index=False)
    samples.to_csv(OUT_SAMPLES, index=False)

    grouped = samples.groupby("z", as_index=False)
    vector = grouped.agg(
        H_D_proxy_median=("H_D_proxy", "median"),
        H_D_proxy_p16=("H_D_proxy", lambda s: float(np.percentile(s, 16))),
        H_D_proxy_p84=("H_D_proxy", lambda s: float(np.percentile(s, 84))),
        H_D_prime_proxy_median=("H_D_prime_proxy", "median"),
        H_D_double_prime_proxy_median=("H_D_double_prime_proxy", "median"),
        FiniteSamples=("FinitePrediction", "sum"),
    )
    vector["BootstrapSamples"] = bootstrap_runs
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
    unique_equations = int(selections["SelectedEquation"].nunique())
    median_complexity = float(selections["SelectedComplexity"].median())
    median_score = float(selections["NormalizedCriteria3Score"].median())
    median_band_width = float((vector["H_D_proxy_p84"] - vector["H_D_proxy_p16"]).median())
    covariance_ready = bool(cov.shape[0] == len(z_grid) and np.all(np.isfinite(cov)))

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_NORMALIZED_CRITERIA3_BOOTSTRAP_SMOKE_V1",
                "BootstrapRuns": bootstrap_runs,
                "FiniteRuns": finite_runs,
                "NonconstantSelectedRuns": nonconstant_runs,
                "UniqueSelectedEquations": unique_equations,
                "GridRows": int(len(z_grid)),
                "MedianSelectedComplexity": median_complexity,
                "MedianNormalizedCriteria3Score": median_score,
                "MedianHDBandWidth": median_band_width,
                "SmokeCovarianceReady": covariance_ready,
                "FullBootstrapScale": False,
                "RequiredBootstrapScale": 200,
                "SourceNativeCovarianceReady": False,
                "K2KernelChanged": False,
                "RhoGreaterThan4Allowed": False,
                "K1Refit": False,
                "TargetSignGateUsed": False,
                "AmplitudeFitUsed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "NORMALIZED_CRITERIA3_BOOTSTRAP_SMOKE_EXECUTED_NOT_FULL_SCALE",
                "StrongestAllowedClaim": (
                    "the normalized criteria-set-3 selector can be run across bootstrap resamples and exported with a smoke covariance"
                ),
                "PrimaryResidualRisk": (
                    "12 smoke resamples are not the registered 200-expression source-native export and cannot serve as measurement scoring"
                ),
                "NextAction": (
                    "scale to 200 registered bootstrap expressions and propagate D_A,H_D derivatives into the backreaction null vector"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Normalized Criteria-Set-3 Bootstrap Smoke",
                "",
                "Status: NORMALIZED_CRITERIA3_BOOTSTRAP_SMOKE_EXECUTED_NOT_FULL_SCALE.",
                "",
                "This smoke run applies the pre-registered normalized criteria-set-3 selector across a small set of radial BAO bootstrap resamples. It tests execution stability only.",
                "",
                "## Result",
                "",
                f"- Bootstrap runs: {bootstrap_runs}",
                f"- Finite runs: {finite_runs}",
                f"- Nonconstant selected runs: {nonconstant_runs}",
                f"- Unique selected equations: {unique_equations}",
                f"- Median selected complexity: {median_complexity}",
                f"- Smoke covariance ready: {covariance_ready}",
                "",
                "## Boundary",
                "",
                "This is not the full 200-expression source-native reproduction, does not change K2, does not refit K1, and does not authorize measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_SELECTIONS.relative_to(ROOT)}")
    print(f"Wrote {OUT_SAMPLES.relative_to(ROOT)}")
    print(f"Wrote {OUT_VECTOR.relative_to(ROOT)}")
    print(f"Wrote {OUT_COV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
