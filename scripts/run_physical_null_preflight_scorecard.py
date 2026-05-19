#!/usr/bin/env python3
"""Run a preflight scorecard for physical-null proxy templates.

The scorecard is intentionally restricted:

- it uses only predeclared unit-norm physical-null templates;
- it reports every allowed bounded-grid amplitude;
- it does not select a best physical-null amplitude for interpretation;
- it does not create a measurement-validation claim.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.likelihood import aic, bic, chi2
from fmc.operators import w_k2_locked

EVIDENCE = ROOT / "evidence"
DATA_K1 = ROOT / "data" / "k1"

TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
EXTERNAL_K1 = DATA_K1 / "source_split_external_k1_response.csv"
TEMPLATES = EVIDENCE / "physical_null_proxy_templates.csv"
AMPLITUDE_POLICY = EVIDENCE / "physical_null_amplitude_policy.csv"
BRANCH_SCATTER = EVIDENCE / "source_split_likelihood_native_branch_scatter_covariance.csv"

OUT = EVIDENCE / "physical_null_preflight_scorecard.csv"
OUT_SUMMARY = EVIDENCE / "physical_null_preflight_summary.csv"


def sign_stable_violations(pred: np.ndarray, target: np.ndarray, stable: np.ndarray) -> int:
    if not np.any(stable):
        return 0
    return int(np.sum(np.sign(pred[stable]) != np.sign(target[stable])))


def load_base_frame() -> pd.DataFrame:
    target = pd.read_csv(TARGET)
    target = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    k1 = pd.read_csv(EXTERNAL_K1)
    scatter = pd.read_csv(BRANCH_SCATTER)
    return (
        target.merge(k1[["GridIndex", "K1Response"]], on="GridIndex", how="inner")
        .merge(scatter[["GridIndex", "SigmaMaxNativeScatter"]], on="GridIndex", how="inner")
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )


def allowed_amplitudes(policy: pd.DataFrame) -> list[tuple[str, float, str]]:
    rows: list[tuple[str, float, str]] = []
    unit = policy[policy["PolicyID"].eq("PHYSNULL_AMP_UNIT_ONLY_V1")]
    if not unit.empty and unit["CanSupportScoringPreflight"].astype(str).str.lower().eq("true").all():
        rows.append(("PHYSNULL_AMP_UNIT_ONLY_V1", 1.0, "primary_sanity_preflight"))

    grid = policy[policy["PolicyID"].eq("PHYSNULL_AMP_BOUNDED_GRID_V1")]
    if not grid.empty and grid["CanSupportScoringPreflight"].astype(str).str.lower().eq("true").all():
        for amp in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            rows.append(("PHYSNULL_AMP_BOUNDED_GRID_V1", amp, "secondary_sensitivity_preflight_report_all"))
    return rows


def add_model(
    rows: list[dict[str, object]],
    *,
    model_id: str,
    model_class: str,
    prediction: np.ndarray,
    y: np.ndarray,
    cov: np.ndarray,
    stable: np.ndarray,
    parameter_count: int,
    amplitude_policy_id: str = "not_applicable",
    amplitude: float | str = "not_applicable",
    amplitude_selection_allowed: bool = False,
    claim_boundary: str = "physical_null_preflight_no_measurement_validation",
) -> None:
    c2 = chi2(y, prediction, cov)
    rows.append(
        {
            "Dataset": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_PHYSICAL_NULL_PREFLIGHT",
            "ModelID": model_id,
            "ModelClass": model_class,
            "Rows": len(y),
            "ParameterCount": parameter_count,
            "AmplitudePolicyID": amplitude_policy_id,
            "Amplitude": amplitude,
            "AmplitudeSelectionAllowed": amplitude_selection_allowed,
            "Chi2": c2,
            "AIC": aic(c2, parameter_count),
            "BIC": bic(c2, parameter_count, len(y)),
            "SignStableViolations": sign_stable_violations(prediction, y, stable),
            "MeanAbsResidual": float(np.mean(np.abs(y - prediction))),
            "CovarianceClass": "branch_scatter_preflight_not_public_full_covariance",
            "Status": "PREFLIGHT_SCORE_NOT_MEASUREMENT_VALIDATION",
            "ClaimBoundary": claim_boundary,
        }
    )


def main() -> None:
    base = load_base_frame()
    templates = pd.read_csv(TEMPLATES)
    policy = pd.read_csv(AMPLITUDE_POLICY)

    y = base["SourceSplitResponse"].to_numpy(float)
    x = base["x_coordinate"].to_numpy(float)
    k1 = base["K1Response"].to_numpy(float)
    sigma = base["SigmaMaxNativeScatter"].to_numpy(float)
    sigma = np.where(sigma <= 0, np.nan, sigma)
    if np.isnan(sigma).any():
        raise ValueError("Non-positive or missing branch-scatter sigma in physical-null preflight.")
    cov = np.diag(sigma * sigma)
    stable = base["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    rows: list[dict[str, object]] = []

    add_model(
        rows,
        model_id="K1_NO_MEMORY_CONTEXT",
        model_class="fair_null_context",
        prediction=k1,
        y=y,
        cov=cov,
        stable=stable,
        parameter_count=0,
    )
    add_model(
        rows,
        model_id="K2_LOCKED_RHO4_CONTEXT",
        model_class="locked_prediction_context",
        prediction=w_k2_locked(x, rho=4.0) * k1,
        y=y,
        cov=cov,
        stable=stable,
        parameter_count=0,
    )
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        add_model(
            rows,
            model_id=f"POLY_DEG{degree}_CONTEXT",
            model_class="overfit_risk_context",
            prediction=np.polyval(coeff, x),
            y=y,
            cov=cov,
            stable=stable,
            parameter_count=degree + 1,
            claim_boundary="polynomial_context_no_physical_explanation",
        )

    amplitudes = allowed_amplitudes(policy)
    for template_id, group in templates.groupby("TemplateID"):
        ordered = base[["GridIndex"]].merge(
            group[["GridIndex", "NullID", "ProxyValue"]], on="GridIndex", how="left"
        )
        if ordered["ProxyValue"].isna().any():
            raise ValueError(f"Template {template_id} is not aligned to the target rows.")
        shape = ordered["ProxyValue"].to_numpy(float)
        null_id = str(ordered["NullID"].iloc[0])
        for policy_id, amp, policy_role in amplitudes:
            model_id = f"{null_id}_{template_id}_A{amp:+.1f}_{policy_id}"
            add_model(
                rows,
                model_id=model_id,
                model_class="physical_null_preflight_sanity"
                if policy_id == "PHYSNULL_AMP_UNIT_ONLY_V1"
                else "physical_null_preflight_sensitivity",
                prediction=amp * shape,
                y=y,
                cov=cov,
                stable=stable,
                parameter_count=0,
                amplitude_policy_id=policy_id,
                amplitude=amp,
                amplitude_selection_allowed=False,
                claim_boundary=f"{policy_role}_no_measurement_validation",
            )

    scorecard = pd.DataFrame(rows)
    scorecard.to_csv(OUT, index=False)

    k2_aic = float(scorecard.loc[scorecard["ModelID"].eq("K2_LOCKED_RHO4_CONTEXT"), "AIC"].iloc[0])
    k1_aic = float(scorecard.loc[scorecard["ModelID"].eq("K1_NO_MEMORY_CONTEXT"), "AIC"].iloc[0])
    physical = scorecard[scorecard["ModelClass"].str.startswith("physical_null")]
    best_physical = physical.loc[physical["AIC"].idxmin()]
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "PHYSICAL_NULL_PREFLIGHT_SCORECARD_SUMMARY",
                "Rows": len(base),
                "PhysicalNullRows": len(physical),
                "AmplitudePoliciesReported": ";".join(sorted(physical["AmplitudePolicyID"].unique())),
                "BestPhysicalNullModelForDiagnosticsOnly": best_physical["ModelID"],
                "BestPhysicalNullAIC": float(best_physical["AIC"]),
                "K1AIC": k1_aic,
                "K2AIC": k2_aic,
                "DeltaAIC_K2_minus_K1": k2_aic - k1_aic,
                "DeltaAIC_K2_minus_BestPhysicalNull": k2_aic - float(best_physical["AIC"]),
                "AnyAmplitudeSelectedForInterpretation": False,
                "MeasurementValidationAllowed": False,
                "PrimaryBlockingIssue": "physical_null_amplitudes_not_physically_calibrated",
                "Interpretation": (
                    "physical nulls are reported as sanity/sensitivity preflight controls only; "
                    "best physical-null row is diagnostic bookkeeping, not an amplitude selection"
                ),
                "ClaimBoundary": "physical_null_preflight_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
