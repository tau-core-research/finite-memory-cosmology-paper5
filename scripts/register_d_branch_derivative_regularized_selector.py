#!/usr/bin/env python3
"""Register a D-branch derivative-regularized selector policy.

This is a governance layer for the D branch only. It does not use K2, K1,
target signs, amplitudes, or measurement-validation language.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "frozen"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT_YAML = FROZEN / "source_native_d_branch_derivative_regularized_selector_v1.yaml"
OUT_POLICY = EVIDENCE / "d_branch_derivative_regularized_selector_policy.csv"
OUT_SUMMARY = EVIDENCE / "d_branch_derivative_regularized_selector_summary.csv"
OUT_DOC = DOCS / "d_branch_derivative_regularized_selector.md"

CLAIM_BOUNDARY = "d_branch_derivative_regularized_selector_no_measurement_validation"


def main() -> None:
    FROZEN.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    selector = {
        "selector_id": "SOURCE_NATIVE_D_BRANCH_DERIVATIVE_REGULARIZED_SELECTOR_V1",
        "base_selector": "SOURCE_NATIVE_NORMALIZED_CRITERIA3_V1",
        "score": "normalized_criteria3_score + lambda_regularization * low_depth_curvature_excess",
        "low_depth_curvature_metric": "median_low_depth(abs(D_double_prime) / max(abs(D_prime), epsilon))",
        "low_depth_z_max": 0.8,
        "curvature_budget": 1.0,
        "lambda_regularization": 1.0,
        "epsilon": 1.0e-12,
        "uses_k2": False,
        "uses_k1": False,
        "uses_target_sign": False,
        "uses_amplitude_fit": False,
        "allows_rho_greater_than_4": False,
        "post_hoc_kernel_changes_allowed": False,
        "measurement_validation_allowed": False,
        "intended_use": "D-branch smoke governance before source-native full bootstrap",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    OUT_YAML.write_text(yaml.safe_dump(selector, sort_keys=False), encoding="utf-8")

    policy = pd.DataFrame(
        [
            {
                "PolicyID": selector["selector_id"],
                "Component": "BaseScore",
                "Definition": selector["base_selector"],
                "UsesK2": False,
                "UsesK1": False,
                "UsesTargetSign": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "PolicyID": selector["selector_id"],
                "Component": "DerivativeRegularity",
                "Definition": selector["low_depth_curvature_metric"],
                "UsesK2": False,
                "UsesK1": False,
                "UsesTargetSign": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
        ]
    )
    policy.to_csv(OUT_POLICY, index=False)

    summary = pd.DataFrame(
        [
            {
                "AuditID": selector["selector_id"],
                "SelectorRegistered": True,
                "BaseSelector": selector["base_selector"],
                "LowDepthZMax": selector["low_depth_z_max"],
                "CurvatureBudget": selector["curvature_budget"],
                "LambdaRegularization": selector["lambda_regularization"],
                "K2KernelChanged": False,
                "RhoGreaterThan4Allowed": False,
                "K1Refit": False,
                "TargetSignGateUsed": False,
                "AmplitudeFitUsed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "D_BRANCH_DERIVATIVE_REGULARIZED_SELECTOR_REGISTERED",
                "StrongestAllowedClaim": (
                    "a D-branch derivative-regularity policy is registered for smoke governance"
                ),
                "PrimaryResidualRisk": (
                    "the budget is a preflight regularity guard and not a source-native covariance result"
                ),
                "NextAction": "run a D-branch bootstrap smoke with the registered regularized selector",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# D-Branch Derivative-Regularized Selector",
                "",
                "Status: D_BRANCH_DERIVATIVE_REGULARIZED_SELECTOR_REGISTERED.",
                "",
                "This selector adds an internal D-branch curvature guard to the normalized criteria-set-3 smoke selector. It does not use K2, K1, target signs, amplitude fitting, or measurement-validation language.",
                "",
                "## Registered Rule",
                "",
                "- Base score: normalized criteria-set-3 score",
                "- Regularity metric: median low-depth |D''| / max(|D'|, epsilon)",
                "- Low-depth range: z < 0.8",
                "- Curvature budget: 1.0",
                "- Regularization weight: 1.0",
                "",
                "## Boundary",
                "",
                "No K2 change, no rho>4, no K1 refit, no target-sign gate, and no measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_YAML.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
