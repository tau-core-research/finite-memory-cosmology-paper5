#!/usr/bin/env python3
"""Build a compact BAO branch decision matrix.

This script records the current BAO preflight state as a protocol decision:
the public BAO data path is useful for plumbing and baseline audits, but K2
measurement-gate scoring remains closed until a locked, competitive K1 response
target exists.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT = EVIDENCE / "bao_branch_decision_matrix.csv"


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(EVIDENCE / name)


def first_value(df: pd.DataFrame, column: str, default: str = "") -> str:
    if column not in df.columns or df.empty:
        return default
    return str(df.iloc[0][column])


def main() -> None:
    public_inputs = read_csv("public_input_inventory.csv")
    transform_ready = read_csv("diagnostic_transform_readiness.csv")
    baseline_scorecard = read_csv("bao_baseline_scorecard.csv")
    k2_ready = read_csv("bao_k2_protocol_readiness.csv")
    k1_ready = read_csv("bao_k1_locked_response_readiness.csv")
    k1_candidate_score = read_csv("bao_k1_candidate_null_scorecard.csv")

    available_products = ";".join(public_inputs["ProductID"].astype(str).tolist())
    allowed_baselines = baseline_scorecard[
        baseline_scorecard["AllowedForMeasurementGate"].astype(str).str.lower().eq("true")
    ]
    zero_row = k1_candidate_score[k1_candidate_score["ModelID"].eq("ZERO_RESPONSE")]
    candidate_best = k1_candidate_score.sort_values("AIC", ascending=True).iloc[0]

    rows = [
        {
            "DecisionID": "BAO_D1_PUBLIC_INPUTS",
            "Question": "Are public BAO/SN inputs locally available for preflight?",
            "Evidence": available_products,
            "Status": "SATISFIED_PREFLIGHT",
            "Decision": "Data availability is no longer the blocking issue.",
            "NextAction": "Use only through registered diagnostic transforms.",
        },
        {
            "DecisionID": "BAO_D2_TRANSFORM_CONTRACT",
            "Question": "Is a BAO transform available and eligible for K2 scoring?",
            "Evidence": ";".join(transform_ready["TransformID"].astype(str).tolist()),
            "Status": "PREFLIGHT_ONLY",
            "Decision": "T1 BAO residual transform is useful for plumbing but not measurement-gate scoring.",
            "NextAction": "Require likelihood-native or coordinate-native diagnostic transform.",
        },
        {
            "DecisionID": "BAO_D3_BASELINE_ELIGIBILITY",
            "Question": "Is there an eligible BAO baseline for primary K2 scoring?",
            "Evidence": f"eligible_baselines={len(allowed_baselines)}; best_preflight={baseline_scorecard.iloc[0]['BaselineLabel']}",
            "Status": "BLOCKED",
            "Decision": "Same-data baselines fit best but cannot be primary K2 baselines; CMB-only is independent but BAO-tensioned.",
            "NextAction": "Keep same-data baselines as controls and seek an independent coordinate-native K1 target.",
        },
        {
            "DecisionID": "BAO_D4_LOCKED_K1_TARGET",
            "Question": "Is a locked BAO K1 response target available?",
            "Evidence": first_value(k1_ready, "BlockingIssue", "missing_locked_k1_target"),
            "Status": "BLOCKED",
            "Decision": "No selected locked no-memory response target is allowed for K2 scoring.",
            "NextAction": "Do not run BAO K2 scoring until a response target is registered and selected.",
        },
        {
            "DecisionID": "BAO_D5_K1_CANDIDATE_SCORE",
            "Question": "Does the CMB-only unit-covariance K1 candidate beat simple nulls?",
            "Evidence": f"best_model={candidate_best['ModelID']}; best_AIC={candidate_best['AIC']}; zero_AIC={zero_row.iloc[0]['AIC'] if not zero_row.empty else 'NA'}",
            "Status": "WEAKENING_PREFLIGHT",
            "Decision": "The zero-response null is AIC-preferred, so the candidate is not selected.",
            "NextAction": "Treat BAO K1 candidate as a negative/weakening preflight result.",
        },
        {
            "DecisionID": "BAO_D6_K2_SCORING_AUTHORIZATION",
            "Question": "Is BAO K2 measurement-gate scoring authorized?",
            "Evidence": f"ready={first_value(k2_ready, 'ReadyForK2Scoring', 'False')}; issue={first_value(k2_ready, 'BlockingIssue', 'protocol_not_ready')}",
            "Status": "CLOSED",
            "Decision": "BAO K2 scoring remains closed under the current protocol.",
            "NextAction": "Pivot the empirical search to SN+BAO/source-split or coordinate-native public benchmark work.",
        },
        {
            "DecisionID": "BAO_D7_BRANCH_DECISION",
            "Question": "What should happen to the BAO branch now?",
            "Evidence": "public inputs solved; transform preflight solved; K1 target not selected; K2 scoring closed",
            "Status": "PIVOT_RECOMMENDED",
            "Decision": "Freeze BAO as a documented preflight branch, not as the next primary measurement route.",
            "NextAction": "Use BAO outputs as controls while the next branch targets SN+BAO/source-split response structure.",
        },
    ]

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
