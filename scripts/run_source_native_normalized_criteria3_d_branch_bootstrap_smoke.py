#!/usr/bin/env python3
"""Run a normalized criteria-set-3 bootstrap smoke for the D branch.

The SN input has many rows, so this smoke pass first creates a deterministic
redshift-binned distance proxy over the BAO-overlap range. The PySR selector is
the pre-registered normalized criteria-set-3 rule. This is not a full
source-native reproduction and does not authorize measurement validation.
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

SN_INPUT = DATA / "source_native_training_sn_distance_proxy.csv"
H_VECTOR = DATA / "source_native_normalized_criteria3_bootstrap_smoke_reconstruction_vector.csv"

OUT_BINNED = DATA / "source_native_normalized_criteria3_d_branch_binned_training.csv"
OUT_SELECTIONS = DATA / "source_native_normalized_criteria3_d_branch_bootstrap_smoke_selection_metadata.csv"
OUT_SAMPLES = DATA / "source_native_normalized_criteria3_d_branch_bootstrap_smoke_samples.csv"
OUT_VECTOR = DATA / "source_native_normalized_criteria3_d_branch_bootstrap_smoke_reconstruction_vector.csv"
OUT_COV = DATA / "source_native_normalized_criteria3_d_branch_bootstrap_smoke_covariance.csv"
OUT_SUMMARY = EVIDENCE / "source_native_normalized_criteria3_d_branch_bootstrap_smoke_summary.csv"
OUT_DOC = DOCS / "source_native_normalized_criteria3_d_branch_bootstrap_smoke.md"

CLAIM_BOUNDARY = "source_native_normalized_criteria3_d_branch_bootstrap_smoke_no_measurement_validation"


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


def select_normalized(hof: pd.DataFrame, n_eff: int) -> pd.Series:
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

    bootstrap_runs = 12
    rng = np.random.default_rng(20260519)
    selection_rows: list[dict[str, object]] = []
    sample_rows: list[dict[str, object]] = []

    for run_idx in range(bootstrap_runs):
        idx = rng.integers(0, len(binned), size=len(binned))
        z_train = z_bin[idx]
        y_train = y_bin[idx]
        sigma_train = sigma_bin[idx]
        order = np.argsort(z_train)
        z_train = z_train[order]
        y_train = y_train[order]
        sigma_train = sigma_train[order]

        hof = fit_hof(z_train, y_train, sigma_train, seed=301 + run_idx)
        selected = select_normalized(hof, n_eff=len(z_train))
        expr, fn = unscaled_callable(selected)
        D = fn(z_grid)
        Dp, Dpp = finite_derivatives(fn, z_grid)
        finite = bool(np.all(np.isfinite(D)) and np.all(np.isfinite(Dp)) and np.all(np.isfinite(Dpp)))

        selection_rows.append(
            {
                "RouteID": "SOURCE_NATIVE_NORMALIZED_CRITERIA3_D_BRANCH_BOOTSTRAP_SMOKE_V1",
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
                    "RouteID": "SOURCE_NATIVE_NORMALIZED_CRITERIA3_D_BRANCH_BOOTSTRAP_SMOKE_V1",
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
    vector["BootstrapSamples"] = bootstrap_runs
    vector["Source"] = str(OUT_BINNED.relative_to(ROOT))
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
                "AuditID": "SOURCE_NATIVE_NORMALIZED_CRITERIA3_D_BRANCH_BOOTSTRAP_SMOKE_V1",
                "SNInputRows": int(len(sn)),
                "BinnedTrainingRows": int(len(binned)),
                "BootstrapRuns": bootstrap_runs,
                "FiniteRuns": finite_runs,
                "NonconstantSelectedRuns": nonconstant_runs,
                "UniqueSelectedEquations": int(selections["SelectedEquation"].nunique()),
                "GridRows": int(len(z_grid)),
                "MedianSelectedComplexity": float(selections["SelectedComplexity"].median()),
                "MedianNormalizedCriteria3Score": float(selections["NormalizedCriteria3Score"].median()),
                "SmokeCovarianceReady": bool(np.isfinite(cov).all()),
                "FullBootstrapScale": False,
                "RequiredBootstrapScale": 200,
                "SourceNativeCovarianceReady": False,
                "K2KernelChanged": False,
                "RhoGreaterThan4Allowed": False,
                "K1Refit": False,
                "TargetSignGateUsed": False,
                "AmplitudeFitUsed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "NORMALIZED_CRITERIA3_D_BRANCH_BOOTSTRAP_SMOKE_EXECUTED_NOT_FULL_SCALE",
                "StrongestAllowedClaim": (
                    "the normalized criteria-set-3 selector can export D,D_prime,D_double_prime across D-branch smoke resamples"
                ),
                "PrimaryResidualRisk": (
                    "SN input is binned for smoke runtime and this is not the registered full source-native bootstrap"
                ),
                "NextAction": (
                    "combine D-branch and H_D-branch normalized PySR smoke exports through the backreaction formula"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Normalized Criteria-Set-3 D-Branch Bootstrap Smoke",
                "",
                "Status: NORMALIZED_CRITERIA3_D_BRANCH_BOOTSTRAP_SMOKE_EXECUTED_NOT_FULL_SCALE.",
                "",
                "This smoke run applies the pre-registered normalized selector to a deterministic redshift-binned SN distance proxy and exports D, D_prime, and D_double_prime on the H_D smoke grid.",
                "",
                "## Result",
                "",
                f"- Binned training rows: {len(binned)}",
                f"- Bootstrap runs: {bootstrap_runs}",
                f"- Finite runs: {finite_runs}",
                f"- Nonconstant selected runs: {nonconstant_runs}",
                f"- Smoke covariance ready: {bool(np.isfinite(cov).all())}",
                "",
                "## Boundary",
                "",
                "This is not the full source-native bootstrap, does not change K2, does not refit K1, and does not authorize measurement validation.",
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
