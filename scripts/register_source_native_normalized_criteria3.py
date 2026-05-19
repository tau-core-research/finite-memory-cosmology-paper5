#!/usr/bin/env python3
"""Register a source-native normalized criteria-set-3 selector.

This is a governance artifact. It does not replace the upstream raw rule, and
it does not score A2/K2. It defines a scale-aware selector that can be used in a
future bootstrap only after pre-registration.

Registered normalized score:

    score = loss / loss_constant + lambda * (complexity - 1) / n_eff

with lambda=1.0 by default.

Rationale:
- loss / loss_constant makes the loss dimensionless and invariant to target
  scaling;
- (complexity - 1) / n_eff treats each added symbolic unit as a per-observation
  complexity cost;
- no K2 target, K1 refit, rho change, or target-sign gate is used.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
FROZEN = ROOT / "frozen"

HOF = EVIDENCE / "pysr_criteria3_structured_hall_of_fame.csv"
PENALTY_SUMMARY = EVIDENCE / "pysr_penalty_normalization_summary.csv"

OUT_CONFIG = FROZEN / "source_native_normalized_criteria3_selector_v1.yaml"
OUT_SELECTOR_AUDIT = EVIDENCE / "source_native_normalized_criteria3_selector_audit.csv"
OUT_POLICY = EVIDENCE / "source_native_normalized_criteria3_selector_policy.csv"
OUT_SUMMARY = EVIDENCE / "source_native_normalized_criteria3_selector_summary.csv"
OUT_DOC = DOCS / "source_native_normalized_criteria3_selector.md"

CLAIM_BOUNDARY = "source_native_normalized_criteria3_selector_no_measurement_validation"


def write_yaml_like(path: Path, content: dict[str, object]) -> None:
    lines: list[str] = []
    for key, value in content.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for sub_key, sub_value in value.items():
                lines.append(f"  {sub_key}: {sub_value}")
        elif isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    FROZEN.mkdir(parents=True, exist_ok=True)

    hof = pd.read_csv(HOF)
    penalty_summary = pd.read_csv(PENALTY_SUMMARY).iloc[0]
    finite = hof[hof["FinitePrediction"].astype(bool)].copy()
    finite["IsConstant"] = finite["IsConstant"].astype(bool)
    if finite.empty:
        raise ValueError("empty finite hall of fame")

    constants = finite[finite["IsConstant"]].sort_values(["loss", "complexity"])
    if constants.empty:
        raise ValueError("no constant baseline available for normalized selector")

    n_eff = 21
    lambda_complexity = 1.0
    constant = constants.iloc[0]
    loss_constant = float(constant["loss"])
    if loss_constant <= 0:
        raise ValueError("constant loss must be positive")

    finite["NormalizedLossRatio"] = finite["loss"].astype(float) / loss_constant
    finite["NormalizedComplexityCost"] = (finite["complexity"].astype(float) - 1.0) / n_eff
    finite["NormalizedCriteria3Score"] = (
        finite["NormalizedLossRatio"] + lambda_complexity * finite["NormalizedComplexityCost"]
    )
    finite["SelectorID"] = "SOURCE_NATIVE_NORMALIZED_CRITERIA3_V1"
    finite["N_eff"] = n_eff
    finite["LambdaComplexity"] = lambda_complexity
    finite["LossConstantBaseline"] = loss_constant
    finite["ClaimBoundary"] = CLAIM_BOUNDARY
    finite.to_csv(OUT_SELECTOR_AUDIT, index=False)

    selected = finite.sort_values(
        ["NormalizedCriteria3Score", "NormalizedLossRatio", "complexity"]
    ).iloc[0]
    strict_constant = bool(penalty_summary["StrictPenaltyOneSelectedIsConstant"])
    selected_is_constant = bool(selected["IsConstant"])
    selector_changes_raw_penalty_result = selected_is_constant != strict_constant

    config = {
        "selector_id": "SOURCE_NATIVE_NORMALIZED_CRITERIA3_V1",
        "status": "pre_registered_not_measurement_active",
        "score": "loss / loss_constant + lambda_complexity * (complexity - 1) / n_eff",
        "loss_constant": "best finite constant expression loss in the same PySR hall of fame",
        "n_eff": "number of source-native training points used by that route",
        "lambda_complexity": lambda_complexity,
        "measurement_validation_allowed": "false",
        "locked_tau_core_flags": {
            "change_k2_kernel_allowed": "false",
            "rho_greater_than_4_allowed": "false",
            "k1_refit_allowed": "false",
            "target_sign_gate_allowed": "false",
            "amplitude_fit_allowed": "false",
        },
        "activation_rule": "allowed only for a future pre-registered bootstrap rerun, not retroactive measurement scoring",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_yaml_like(OUT_CONFIG, config)

    policy = pd.DataFrame(
        [
            {
                "PolicyID": "SOURCE_NATIVE_NORMALIZED_CRITERIA3_V1",
                "Formula": "loss / loss_constant + lambda_complexity * (complexity - 1) / n_eff",
                "LambdaComplexity": lambda_complexity,
                "N_eff_Source": "route training row count",
                "LossNormalization": "best finite constant expression loss from same hall of fame",
                "AllowedForFutureBootstrap": True,
                "AllowedForRetroactiveMeasurementScoring": False,
                "AllowedForCurrentMeasurementValidation": False,
                "UsesK2Target": False,
                "UsesK1Refit": False,
                "AllowsRhoGreaterThan4": False,
                "UsesTargetSignGate": False,
                "RequiredNextCheck": (
                    "rerun bootstrap-scale PySR with this selector frozen before source-native scoring"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    policy.to_csv(OUT_POLICY, index=False)

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_NORMALIZED_CRITERIA3_SELECTOR_V1",
                "HallOfFameRowsAudited": int(len(finite)),
                "N_eff": n_eff,
                "LambdaComplexity": lambda_complexity,
                "LossConstantBaseline": loss_constant,
                "RawPenaltyOneSelectedIsConstant": strict_constant,
                "NormalizedSelectorSelectedEquation": selected["equation"],
                "NormalizedSelectorSelectedComplexity": int(selected["complexity"]),
                "NormalizedSelectorSelectedLoss": float(selected["loss"]),
                "NormalizedSelectorSelectedIsConstant": selected_is_constant,
                "NormalizedSelectorScore": float(selected["NormalizedCriteria3Score"]),
                "NormalizedSelectorWeightedMSEOriginal": float(selected["WeightedMSEOriginal"]),
                "SelectorChangesRawPenaltyResult": selector_changes_raw_penalty_result,
                "SelectorPreRegistered": True,
                "AllowedForFutureBootstrap": True,
                "AllowedForRetroactiveMeasurementScoring": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_NORMALIZED_CRITERIA3_PRE_REGISTERED_NOT_MEASUREMENT_ACTIVE",
                "StrongestAllowedClaim": (
                    "a scale-aware criteria-set-3 selector is pre-registered for future source-native bootstrap reruns"
                ),
                "PrimaryResidualRisk": (
                    "the selector has not yet been used in a full bootstrap and cannot replace source-native covariance"
                ),
                "NextAction": (
                    "run a bootstrap-scale PySR reproduction with this selector frozen and export derivative covariance"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Normalized Criteria-Set-3 Selector",
                "",
                "Status: SOURCE_NATIVE_NORMALIZED_CRITERIA3_PRE_REGISTERED_NOT_MEASUREMENT_ACTIVE.",
                "",
                "This document freezes a scale-aware selector for future source-native PySR bootstrap reruns. It is not retroactive measurement scoring.",
                "",
                "## Formula",
                "",
                "`score = loss / loss_constant + lambda_complexity * (complexity - 1) / n_eff`",
                "",
                "where `loss_constant` is the best finite constant expression loss in the same hall of fame, `n_eff` is the route training row count, and `lambda_complexity = 1.0`.",
                "",
                "## Smoke Audit",
                "",
                f"- Raw penalty-one selected constant: {strict_constant}",
                f"- Normalized selector selected constant: {selected_is_constant}",
                f"- Selected equation: `{selected['equation']}`",
                f"- Selected score: {float(selected['NormalizedCriteria3Score'])}",
                f"- Selected original weighted MSE: {float(selected['WeightedMSEOriginal'])}",
                "",
                "## Boundary",
                "",
                "The selector does not change K2, does not refit K1, does not allow rho > 4, and does not authorize measurement validation. It may only be used after a frozen bootstrap rerun.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_SELECTOR_AUDIT.relative_to(ROOT)}")
    print(f"Wrote {OUT_POLICY.relative_to(ROOT)}")
    print(f"Wrote {OUT_CONFIG.relative_to(ROOT)}")
    print(f"Wrote {OUT_DOC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
