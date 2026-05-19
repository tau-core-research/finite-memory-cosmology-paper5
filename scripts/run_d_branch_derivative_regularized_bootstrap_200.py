#!/usr/bin/env python3
"""Run the registered derivative-regularized D-branch selector at 200 bootstraps."""

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

SN_INPUT = DATA / "source_native_training_sn_distance_proxy.csv"
H_VECTOR = DATA / "source_native_normalized_criteria3_bootstrap_smoke_reconstruction_vector.csv"

OUT_BINNED = DATA / "d_branch_derivative_regularized_bootstrap_200_binned_training.csv"
OUT_SELECTIONS = DATA / "d_branch_derivative_regularized_bootstrap_200_selection_metadata.csv"
OUT_SAMPLES = DATA / "d_branch_derivative_regularized_bootstrap_200_samples.csv"
OUT_VECTOR = DATA / "d_branch_derivative_regularized_bootstrap_200_reconstruction_vector.csv"
OUT_COV = DATA / "d_branch_derivative_regularized_bootstrap_200_covariance.csv"
OUT_SUMMARY = EVIDENCE / "d_branch_derivative_regularized_bootstrap_200_summary.csv"
OUT_DOC = DOCS / "d_branch_derivative_regularized_bootstrap_200.md"

CLAIM_BOUNDARY = "d_branch_derivative_regularized_bootstrap_200_no_measurement_validation"

LOW_DEPTH_Z_MAX = 0.8
CURVATURE_BUDGET = 1.0
LAMBDA_REGULARIZATION = 1.0
EPSILON = 1.0e-12
BOOTSTRAP_RUNS = 200


def weighted_binned_sn(sn: pd.DataFrame, z_min: float, z_max: float, bins: int = 24) -> pd.DataFrame:
    sub = sn[(sn["z"] >= z_min) & (sn["z"] <= z_max)].copy()
    edges = np.linspace(z_min, z_max, bins + 1)
    rows = []
    for i in range(bins):
        lo, hi = edges[i], edges[i + 1]
        group = sub[(sub["z"] >= lo) & (sub["z"] < hi if i < bins - 1 else sub["z"] <= hi)]
        if group.empty:
            continue
        y = group["D_proxy_Mpc"].to_numpy(float)
        sigma = group["D_proxy_sigma_diag_Mpc"].to_numpy(float)
        z = group["z"].to_numpy(float)
        mask = np.isfinite(y) & np.isfinite(sigma) & np.isfinite(z) & (sigma > 0)
        if not mask.any():
            continue
        w = 1.0 / (sigma[mask] ** 2)
        rows.append(
            {
                "BinIndex": i,
                "z": float(np.sum(w * z[mask]) / np.sum(w)),
                "D_proxy_Mpc": float(np.sum(w * y[mask]) / np.sum(w)),
                "D_proxy_sigma_diag_Mpc": float(np.sqrt(1.0 / np.sum(w))),
                "Rows": int(mask.sum()),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    return pd.DataFrame(rows)


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
        unary_operators=["square"],
        constraints={"/": (-1, 6)},
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


def unscaled_callable(row: pd.Series):
    expr, fn_std = expression_callable(row["sympy_format"])
    y_mean = float(row["y_mean"])
    y_scale = float(row["y_scale"])

    def fn(values: np.ndarray) -> np.ndarray:
        return y_mean + y_scale * fn_std(values)

    return expr, fn


def candidate_regularized_scores(hof: pd.DataFrame, n_eff: int, z_grid: np.ndarray) -> pd.DataFrame:
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

    rows = []
    low_mask = z_grid < LOW_DEPTH_Z_MAX
    midhigh_mask = ~low_mask
    for idx, row in tmp.iterrows():
        try:
            expr, fn = unscaled_callable(row)
            D = np.asarray(fn(z_grid), dtype=float)
            if D.ndim == 0:
                D = np.full_like(z_grid, float(D))
            Dp, Dpp = finite_derivatives(fn, z_grid)
            finite = bool(np.all(np.isfinite(D)) and np.all(np.isfinite(Dp)) and np.all(np.isfinite(Dpp)))
            ratio = np.abs(Dpp) / np.maximum(np.abs(Dp), EPSILON)
            low_metric = float(np.median(ratio[low_mask])) if np.any(low_mask) and finite else float("inf")
            midhigh_metric = float(np.median(ratio[midhigh_mask])) if np.any(midhigh_mask) and finite else float("inf")
            low_excess = max(0.0, low_metric - CURVATURE_BUDGET) / CURVATURE_BUDGET
            regularized_score = float(row["NormalizedCriteria3Score"]) + LAMBDA_REGULARIZATION * low_excess
        except Exception:
            expr = ""
            finite = False
            low_metric = float("inf")
            midhigh_metric = float("inf")
            low_excess = float("inf")
            regularized_score = float("inf")
        rows.append(
            {
                "CandidateIndex": int(idx),
                "SelectedSympyExpression": str(expr),
                "FinitePrediction": finite,
                "LowDepthCurvatureMetric": low_metric,
                "MidHighCurvatureMetric": midhigh_metric,
                "CurvatureBudget": CURVATURE_BUDGET,
                "DerivativeRegularityPenalty": low_excess,
                "DerivativeRegularizedScore": regularized_score,
            }
        )
    return (
        tmp.reset_index(drop=False)
        .rename(columns={"index": "CandidateIndex"})
        .merge(pd.DataFrame(rows), on="CandidateIndex", how="left")
        .sort_values(
            [
                "DerivativeRegularizedScore",
                "DerivativeRegularityPenalty",
                "NormalizedCriteria3Score",
                "NormalizedLossRatio",
                "complexity",
            ]
        )
    )


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    sn = pd.read_csv(SN_INPUT)
    h_grid = pd.read_csv(H_VECTOR).sort_values("z")
    z_grid = h_grid["z"].to_numpy(float)
    z_min = max(float(z_grid.min()), float(sn["z"].min()))
    z_max = min(float(z_grid.max()), float(sn["z"].max()))
    binned = weighted_binned_sn(sn, z_min, z_max, bins=24)
    binned.to_csv(OUT_BINNED, index=False)

    z_bin = binned["z"].to_numpy(float)
    y_bin = binned["D_proxy_Mpc"].to_numpy(float)
    sigma_bin = binned["D_proxy_sigma_diag_Mpc"].to_numpy(float)

    rng = np.random.default_rng(20260521)
    selection_rows: list[dict[str, object]] = []
    sample_rows: list[dict[str, object]] = []

    for run_idx in range(BOOTSTRAP_RUNS):
        idx = rng.integers(0, len(binned), size=len(binned))
        order = np.argsort(z_bin[idx])
        z_train = z_bin[idx][order]
        y_train = y_bin[idx][order]
        sigma_train = sigma_bin[idx][order]

        hof = fit_hof(z_train, y_train, sigma_train, seed=501 + run_idx)
        scored = candidate_regularized_scores(hof, n_eff=len(z_train), z_grid=z_grid)
        selected = scored.iloc[0]
        expr, fn = unscaled_callable(selected)
        D = np.asarray(fn(z_grid), dtype=float)
        if D.ndim == 0:
            D = np.full_like(z_grid, float(D))
        Dp, Dpp = finite_derivatives(fn, z_grid)
        finite = bool(np.all(np.isfinite(D)) and np.all(np.isfinite(Dp)) and np.all(np.isfinite(Dpp)))

        selection_rows.append(
            {
                "RouteID": "D_BRANCH_DERIVATIVE_REGULARIZED_BOOTSTRAP_200_V1",
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
                "LowDepthCurvatureMetric": float(selected["LowDepthCurvatureMetric"]),
                "MidHighCurvatureMetric": float(selected["MidHighCurvatureMetric"]),
                "DerivativeRegularityPenalty": float(selected["DerivativeRegularityPenalty"]),
                "DerivativeRegularizedScore": float(selected["DerivativeRegularizedScore"]),
                "CurvatureBudget": CURVATURE_BUDGET,
                "LambdaRegularization": LAMBDA_REGULARIZATION,
                "FinitePrediction": finite,
                "K2KernelChanged": False,
                "RhoGreaterThan4Allowed": False,
                "K1Refit": False,
                "TargetSignGateUsed": False,
                "AmplitudeFitUsed": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
        for z, d, dp, dpp in zip(z_grid, D, Dp, Dpp):
            sample_rows.append(
                {
                    "RouteID": "D_BRANCH_DERIVATIVE_REGULARIZED_BOOTSTRAP_200_V1",
                    "BootstrapIndex": run_idx,
                    "z": float(z),
                    "D": float(d),
                    "D_prime": float(dp),
                    "D_double_prime": float(dpp),
                    "FinitePrediction": finite,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )

    selections = pd.DataFrame(selection_rows)
    samples = pd.DataFrame(sample_rows)
    selections.to_csv(OUT_SELECTIONS, index=False)
    samples.to_csv(OUT_SAMPLES, index=False)

    vector = samples.groupby("z", as_index=False).agg(
        D_median=("D", "median"),
        D_p16=("D", lambda s: float(np.percentile(s, 16))),
        D_p84=("D", lambda s: float(np.percentile(s, 84))),
        D_prime_median=("D_prime", "median"),
        D_double_prime_median=("D_double_prime", "median"),
        FiniteSamples=("FinitePrediction", "sum"),
    )
    vector["BootstrapSamples"] = BOOTSTRAP_RUNS
    vector["Source"] = str(OUT_BINNED.relative_to(ROOT))
    vector["SelectionRule"] = "derivative_regularized_normalized_criteria3_200_no_K2_fit"
    vector["ClaimBoundary"] = CLAIM_BOUNDARY
    vector.to_csv(OUT_VECTOR, index=False)

    pivot = samples.pivot_table(index="BootstrapIndex", columns="z", values="D", aggfunc="first")
    cov = np.cov(pivot.to_numpy(float), rowvar=False)
    cov_df = pd.DataFrame(cov, columns=[f"z_{z:.6g}" for z in pivot.columns])
    cov_df.insert(0, "CovRow", [f"z_{z:.6g}" for z in pivot.columns])
    cov_df["ClaimBoundary"] = CLAIM_BOUNDARY
    cov_df.to_csv(OUT_COV, index=False)

    finite_runs = int(selections["FinitePrediction"].astype(bool).sum())
    nonconstant_runs = int((~selections["SelectedIsConstant"].astype(bool)).sum())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "D_BRANCH_DERIVATIVE_REGULARIZED_BOOTSTRAP_200_V1",
                "SNInputRows": int(len(sn)),
                "BinnedTrainingRows": int(len(binned)),
                "BootstrapRuns": BOOTSTRAP_RUNS,
                "FiniteRuns": finite_runs,
                "NonconstantSelectedRuns": nonconstant_runs,
                "UniqueSelectedEquations": int(selections["SelectedEquation"].nunique()),
                "GridRows": int(len(z_grid)),
                "MedianSelectedComplexity": float(selections["SelectedComplexity"].median()),
                "MedianNormalizedCriteria3Score": float(selections["NormalizedCriteria3Score"].median()),
                "MedianDerivativeRegularizedScore": float(selections["DerivativeRegularizedScore"].median()),
                "MedianLowDepthCurvatureMetric": float(selections["LowDepthCurvatureMetric"].median()),
                "MedianMidHighCurvatureMetric": float(selections["MidHighCurvatureMetric"].median()),
                "P95LowDepthCurvatureMetric": float(np.percentile(selections["LowDepthCurvatureMetric"], 95)),
                "P95MidHighCurvatureMetric": float(np.percentile(selections["MidHighCurvatureMetric"], 95)),
                "CurvatureBudget": CURVATURE_BUDGET,
                "LambdaRegularization": LAMBDA_REGULARIZATION,
                "CovarianceReady": bool(np.isfinite(cov).all()),
                "FullBootstrapScale": True,
                "RequiredBootstrapScale": 200,
                "SourceNativeCovarianceReady": False,
                "K2KernelChanged": False,
                "RhoGreaterThan4Allowed": False,
                "K1Refit": False,
                "TargetSignGateUsed": False,
                "AmplitudeFitUsed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "D_BRANCH_DERIVATIVE_REGULARIZED_BOOTSTRAP_200_EXECUTED",
                "StrongestAllowedClaim": (
                    "the registered D-branch derivative-regularized selector is stable at 200 bootstrap preflight scale"
                ),
                "PrimaryResidualRisk": (
                    "H_D branch still needs matching 200-bootstrap export before full D+H covariance scoring"
                ),
                "NextAction": (
                    "run the H_D branch at matching 200-bootstrap scale and then rebuild the full regularized backreaction null"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# D-Branch Derivative-Regularized Bootstrap 200",
                "",
                "Status: D_BRANCH_DERIVATIVE_REGULARIZED_BOOTSTRAP_200_EXECUTED.",
                "",
                "This run scales the registered D-branch derivative-regularized selector to 200 bootstrap samples. It does not use K2, K1, target signs, amplitude fitting, or measurement-validation language.",
                "",
                "## Result",
                "",
                f"- Binned training rows: {len(binned)}",
                f"- Bootstrap runs: {BOOTSTRAP_RUNS}",
                f"- Finite runs: {finite_runs}",
                f"- Nonconstant selected runs: {nonconstant_runs}",
                f"- Median low-depth curvature metric: {float(selections['LowDepthCurvatureMetric'].median())}",
                f"- P95 low-depth curvature metric: {float(np.percentile(selections['LowDepthCurvatureMetric'], 95))}",
                f"- Covariance ready: {bool(np.isfinite(cov).all())}",
                "",
                "## Boundary",
                "",
                "This is a preflight D-branch scale-up only. Full D+H scoring still requires a matching H_D branch scale-up.",
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
