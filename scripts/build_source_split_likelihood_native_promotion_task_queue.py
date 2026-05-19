#!/usr/bin/env python3
"""Build a task queue for likelihood-native K1 promotion blockers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
PROMOTION_GATE = EVIDENCE / "source_split_likelihood_native_k1_promotion_gate.csv"
OUT = EVIDENCE / "source_split_likelihood_native_promotion_task_queue.csv"
SUMMARY = EVIDENCE / "source_split_likelihood_native_promotion_task_queue_summary.csv"

NUISANCE_POLICY = ROOT / "docs" / "source_split_likelihood_native_nuisance_policy.md"
COORDINATE_PROMOTION = ROOT / "docs" / "source_split_likelihood_native_coordinate_promotion.md"
COVARIANCE_PROMOTION = ROOT / "docs" / "source_split_likelihood_native_covariance_promotion.md"
NULL_SCORECARD = ROOT / "scripts" / "run_source_split_likelihood_native_null_scorecard.py"
EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"


TASKS = [
    {
        "TaskID": "LNPROMO_1_NUISANCE_POLICY",
        "DependsOn": "baseline_prediction_vector",
        "UnlocksCheck": "PROMO_BASELINE_VECTOR",
        "OutputTarget": "promoted baseline vector policy",
        "RequiredArtifact": "docs/source_split_likelihood_native_nuisance_policy.md",
        "DoneCriteria": "SN nuisance/offset treatment is declared before primary K1 export and not chosen from K2 residual performance",
        "Risk": "same-sample centering silently becomes a primary K1 amplitude fit",
        "CurrentStatus": "COMPLETED_POLICY" if NUISANCE_POLICY.exists() else "PENDING",
        "NextAction": "Write nuisance policy distinguishing raw baseline response from centered control.",
    },
    {
        "TaskID": "LNPROMO_2_COORDINATE_PROMOTION",
        "DependsOn": "LNPROMO_1_NUISANCE_POLICY;coordinate_map_preflight",
        "UnlocksCheck": "PROMO_COORDINATE_MAP",
        "OutputTarget": "promoted likelihood-native coordinate decision",
        "RequiredArtifact": "docs/source_split_likelihood_native_coordinate_promotion.md",
        "DoneCriteria": "coordinate map is declared as the K2 depth coordinate or explicitly left as preflight",
        "Risk": "using a convenient coordinate after inspecting K2 performance",
        "CurrentStatus": "COMPLETED_POLICY" if COORDINATE_PROMOTION.exists() else "PENDING",
        "NextAction": "Define whether CMB-chi coordinate is promoted or remains preflight.",
    },
    {
        "TaskID": "LNPROMO_3_COVARIANCE_PROMOTION",
        "DependsOn": "LNPROMO_1_NUISANCE_POLICY;LNPROMO_2_COORDINATE_PROMOTION",
        "UnlocksCheck": "PROMO_COVARIANCE_POLICY",
        "OutputTarget": "declared joint covariance policy for likelihood-native vector",
        "RequiredArtifact": "docs/source_split_likelihood_native_covariance_promotion.md",
        "DoneCriteria": "same covariance policy applies to K1, locked K2, and null comparators",
        "Risk": "treating shrinkage covariance as public full covariance",
        "CurrentStatus": "COMPLETED_POLICY" if COVARIANCE_PROMOTION.exists() else "PENDING",
        "NextAction": "Decide whether shrinkage covariance is promoted as declared benchmark or left preflight.",
    },
    {
        "TaskID": "LNPROMO_4_NULL_SCORECARD_SPEC",
        "DependsOn": "LNPROMO_3_COVARIANCE_PROMOTION",
        "UnlocksCheck": "PROMO_NULL_SCORECARD",
        "OutputTarget": "likelihood-native null scorecard script/spec",
        "RequiredArtifact": "scripts/run_source_split_likelihood_native_null_scorecard.py",
        "DoneCriteria": "K1, locked K2, and registered null comparators score on the same promoted vector",
        "Risk": "running K2/null scoring before primary K1 export is clean",
        "CurrentStatus": "GUARD_SCRIPT_AVAILABLE" if NULL_SCORECARD.exists() else "BLOCKED_BY_UPSTREAM_PROMOTION",
        "NextAction": "Use guard script now; produce model scores only after primary K1 export validates.",
    },
    {
        "TaskID": "LNPROMO_5_EXTERNAL_K1_EXPORT",
        "DependsOn": "LNPROMO_1_NUISANCE_POLICY;LNPROMO_2_COORDINATE_PROMOTION;LNPROMO_3_COVARIANCE_PROMOTION",
        "UnlocksCheck": "PROMO_EXTERNAL_K1_EXPORT",
        "OutputTarget": "data/k1/source_split_external_k1_response.csv",
        "RequiredArtifact": "data/k1/source_split_external_k1_response.csv",
        "DoneCriteria": "external K1 export validates as likelihood_native_baseline and primary K1 candidate",
        "Risk": "overwriting future-only family-mean K1 with an unpromoted preflight vector",
        "CurrentStatus": "EXPORT_AVAILABLE_REQUIRES_VALIDATION" if EXTERNAL_K1.exists() else "BLOCKED_BY_UPSTREAM_PROMOTION",
        "NextAction": "Generate only after promotion policies are clean and validator expectations are updated.",
    },
    {
        "TaskID": "LNPROMO_6_FINAL_GATE_RERUN",
        "DependsOn": "LNPROMO_4_NULL_SCORECARD_SPEC;LNPROMO_5_EXTERNAL_K1_EXPORT",
        "UnlocksCheck": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_K1_PROMOTION_V1",
        "OutputTarget": "clean promotion gate and readiness update",
        "RequiredArtifact": "evidence/source_split_likelihood_native_k1_promotion_summary.csv",
        "DoneCriteria": "PrimaryK1PromotionAllowed is true before any locked K2 result is interpreted",
        "Risk": "claiming measurement validation from preflight artifacts",
        "CurrentStatus": "BLOCKED_BY_UPSTREAM_PROMOTION",
        "NextAction": "Rerun promotion gate and readiness after upstream tasks complete.",
    },
]


def main() -> None:
    tasks = pd.DataFrame(TASKS)
    promotion_allowed = False
    if PROMOTION_GATE.exists():
        gate = pd.read_csv(PROMOTION_GATE)
        issues = gate["BlockingIssue"].fillna("").astype(str)
        blocked_checks = set(gate.loc[issues.str.len() > 0, "CheckID"].astype(str))
        summary_path = EVIDENCE / "source_split_likelihood_native_k1_promotion_summary.csv"
        if summary_path.exists():
            summary = pd.read_csv(summary_path)
            promotion_allowed = bool(
                not summary.empty
                and summary.get("PrimaryK1PromotionAllowed", pd.Series([False]))
                .astype(str)
                .str.lower()
                .eq("true")
                .all()
            )
        tasks["CurrentlyBlocksPromotion"] = tasks["UnlocksCheck"].isin(blocked_checks) | tasks[
            "UnlocksCheck"
        ].eq("SOURCE_SPLIT_LIKELIHOOD_NATIVE_K1_PROMOTION_V1") & (not promotion_allowed)
    else:
        tasks["CurrentlyBlocksPromotion"] = True
    tasks.to_csv(OUT, index=False)

    actionable = tasks[
        tasks["CurrentlyBlocksPromotion"].astype(bool)
        & ~tasks["CurrentStatus"].astype(str).str.startswith("COMPLETED")
    ]
    next_task = str(actionable["TaskID"].iloc[0]) if not actionable.empty else "NO_PROMOTION_TASKS_BLOCKED"
    summary = pd.DataFrame(
        [
            {
                "QueueID": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_PROMOTION_TASK_QUEUE_V1",
                "Tasks": len(tasks),
                "BlockingTasks": int(tasks["CurrentlyBlocksPromotion"].astype(bool).sum()),
                "NextTask": next_task,
                "K2ScoringStillBlocked": not promotion_allowed,
                "ClaimBoundary": "promotion_task_queue_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
