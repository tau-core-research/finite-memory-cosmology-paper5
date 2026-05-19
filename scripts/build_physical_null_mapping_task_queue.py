#!/usr/bin/env python3
"""Build the next task queue for physical-null mapping work."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

READINESS = EVIDENCE / "physical_null_mapping_readiness.csv"
OUT = EVIDENCE / "physical_null_mapping_task_queue.csv"
OUT_SUMMARY = EVIDENCE / "physical_null_mapping_task_queue_summary.csv"


def main() -> None:
    readiness = pd.read_csv(READINESS)
    ranked = readiness.sort_values(
        ["UsableCoverageFraction", "HasSourceUncertainty", "HasNumericValue"],
        ascending=False,
    ).reset_index(drop=True)

    tasks: list[dict[str, object]] = []
    for rank, (_, row) in enumerate(ranked.iterrows(), start=1):
        if row["NullID"] == "BACKREACTION_ONLY":
            task_type = "backreaction_numeric_route"
            next_action = "obtain numeric Omega_R_plus_3Omega_Q envelope or reconstruction table before mapping"
        elif row["Quantity"] == "alpha_smoothness":
            task_type = "optical_alpha_transform"
            next_action = "define alpha_to_source_split_response transform and propagate uncertainty"
        else:
            task_type = "control_quantity_transform"
            next_action = "keep as optical consistency control unless a primary-null transform is declared"

        priority = rank
        if row["Status"] == "MAPPING_PRECHECK_PARTIAL_READY":
            priority = rank - 100

        tasks.append(
            {
                "TaskID": f"PNMAP_{rank:02d}",
                "ExtractionID": row["ExtractionID"],
                "NullID": row["NullID"],
                "Quantity": row["Quantity"],
                "TaskType": task_type,
                "UsableCoverageFraction": row["UsableCoverageFraction"],
                "HasNumericValue": row["HasNumericValue"],
                "HasSourceUncertainty": row["HasSourceUncertainty"],
                "CurrentStatus": row["Status"],
                "PriorityScore": priority,
                "NextAction": next_action,
                "CanOpenBenchmarkGate": False,
                "BlockingIssue": row["BlockingIssue"],
                "ClaimBoundary": "mapping_task_queue_no_measurement_validation",
            }
        )

    output = pd.DataFrame(tasks).sort_values(["PriorityScore", "TaskID"])
    output.to_csv(OUT, index=False)

    first = output.iloc[0]
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "PHYSICAL_NULL_MAPPING_TASK_QUEUE_SUMMARY",
                "Tasks": len(output),
                "PartialReadyTasks": int(output["CurrentStatus"].eq("MAPPING_PRECHECK_PARTIAL_READY").sum()),
                "BenchmarkGateOpenTasks": int(output["CanOpenBenchmarkGate"].sum()),
                "RecommendedFirstTask": first["TaskID"],
                "RecommendedFirstExtractionID": first["ExtractionID"],
                "RecommendedFirstAction": first["NextAction"],
                "PrimaryBlockingIssue": "transform_and_covariance_missing",
                "Interpretation": "joint optical alpha rows are first mapping candidates, but no task opens measurement scoring",
                "ClaimBoundary": "mapping_task_queue_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
