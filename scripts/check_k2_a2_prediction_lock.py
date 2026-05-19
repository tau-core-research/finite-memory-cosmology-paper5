#!/usr/bin/env python3
"""Check the locked K2_SOURCE_SPLIT_A2_PRIOR_V1 prediction contract."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "frozen" / "k2_source_split_a2_prior_v1.yaml"
PRED = ROOT / "data" / "predictions" / "k2_source_split_a2_prior_v1.csv"
OUT = ROOT / "evidence" / "k2_a2_prediction_lock_readiness.csv"


def yes_no(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def main() -> None:
    cfg_text = FROZEN.read_text()
    pred = pd.read_csv(PRED)

    checks: list[dict[str, object]] = []

    def add(check_id: str, ok: bool, observed: object, requirement: str, blocking: str = "") -> None:
        checks.append(
            {
                "CheckID": check_id,
                "Status": yes_no(ok),
                "Observed": observed,
                "Requirement": requirement,
                "BlockingIssue": "" if ok else blocking,
                "ClaimBoundary": "locked_prediction_candidate_no_measurement_validation",
            }
        )

    add("prediction_id_locked", 'prediction_id: "K2_SOURCE_SPLIT_A2_PRIOR_V1"' in cfg_text, "K2_SOURCE_SPLIT_A2_PRIOR_V1" if 'prediction_id: "K2_SOURCE_SPLIT_A2_PRIOR_V1"' in cfg_text else "missing", "K2_SOURCE_SPLIT_A2_PRIOR_V1", "prediction_id_mismatch")
    add("kernel_p_locked", "p: 3" in cfg_text and set(pred["P"]) == {3}, f"pred={set(pred['P'])}", "p=3", "p_not_locked")
    add("rho_locked", "rho: 4.0" in cfg_text and set(pred["Rho"]) == {4.0}, f"pred={set(pred['Rho'])}", "rho=4", "rho_not_locked")
    add("rho_bound_respected", 'rho_bound: "rho <= 4"' in cfg_text, "rho <= 4", "rho<=4", "rho_bound_exceeded")
    add("kernel_unchanged", "kernel_changed: false" in cfg_text and set(pred["KernelChanged"]) == {False}, f"pred={set(pred['KernelChanged'])}", "kernel_changed=false", "kernel_changed")
    add("a_tau_locked", "A_tau: 2.0" in cfg_text and set(pred["A_tau"]) == {2.0}, f"pred={set(pred['A_tau'])}", "A_tau=2", "a_tau_not_locked")
    add("a_tau_not_fitted", "fitted_in_this_note: false" in cfg_text and set(pred["FittedInThisNote"]) == {False}, f"pred={set(pred['FittedInThisNote'])}", "fitted_in_this_note=false", "a_tau_or_prediction_fitted")
    add("pointwise_gain_forbidden", "pointwise_gain_allowed: false" in cfg_text, "pointwise_gain_allowed=false", "pointwise_gain_allowed=false", "pointwise_gain_allowed")
    add("k1_refit_forbidden", "refit_allowed: false" in cfg_text, "refit_allowed=false", "K1 refit forbidden", "k1_refit_allowed")
    add("target_regime_declared", pred["TargetRegime"].notna().all(), sorted(pred["TargetRegime"].unique()), "target regime declared for every row", "target_regime_missing")
    add("claim_boundary_safe", "no_measurement_validation" in cfg_text and pred["ClaimBoundary"].str.contains("no_measurement_validation").all(), "no_measurement_validation", "no measurement validation claim", "claim_boundary_not_safe")

    all_pass = all(row["Status"] == "PASS" for row in checks)
    checks.append(
        {
            "CheckID": "overall_lock_status",
            "Status": yes_no(all_pass),
            "Observed": f"{sum(row['Status'] == 'PASS' for row in checks)}/{len(checks)} checks passed before overall",
            "Requirement": "all lock checks pass",
            "BlockingIssue": "" if all_pass else "one_or_more_lock_checks_failed",
            "ClaimBoundary": "locked_prediction_candidate_no_measurement_validation",
        }
    )

    pd.DataFrame(checks).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
