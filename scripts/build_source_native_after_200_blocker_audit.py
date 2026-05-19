#!/usr/bin/env python3
"""Summarize the remaining source-native blockers after the 200-bootstrap proxy runs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"

TASKS = EVIDENCE / "source_native_reproduction_task_queue.csv"
TASK_READINESS = EVIDENCE / "source_native_reproduction_task_readiness.csv"
EXPORT_VALIDATION = EVIDENCE / "source_native_backreaction_export_validation_summary.csv"
UNCERTAINTY_VALIDATION = EVIDENCE / "source_native_backreaction_uncertainty_validation_summary.csv"
PROTOCOL = EVIDENCE / "source_native_symbolic_protocol_extract_summary.csv"
D200 = EVIDENCE / "d_branch_derivative_regularized_bootstrap_200_summary.csv"
H200 = EVIDENCE / "h_branch_normalized_criteria3_bootstrap_200_summary.csv"
FULL200 = EVIDENCE / "regularized_full_pysr_backreaction_200_summary.csv"
DOMINANCE200 = EVIDENCE / "regularized_200_null_dominance_summary.csv"

OUT_AUDIT = EVIDENCE / "source_native_after_200_blocker_audit.csv"
OUT_SUMMARY = EVIDENCE / "source_native_after_200_blocker_summary.csv"
OUT_DOC = DOCS / "source_native_after_200_blocker_audit.md"
OUT_REQUEST = DATA / "source_native_after_200_request_packet.md"

CLAIM_BOUNDARY = "source_native_after_200_blocker_audit_no_measurement_validation"


def first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty file: {path}")
    return df.iloc[0]


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    tasks = pd.read_csv(TASKS)
    readiness = first(TASK_READINESS)
    export_validation = first(EXPORT_VALIDATION)
    uncertainty_validation = first(UNCERTAINTY_VALIDATION)
    protocol = first(PROTOCOL)
    d200 = first(D200)
    h200 = first(H200)
    full200 = first(FULL200)
    dominance = first(DOMINANCE200)

    required = tasks[tasks["Required"].map(truthy)]
    blocking = required[required["BlocksSourceNativeScoring"].map(truthy)]

    rows = []
    for _, row in required.iterrows():
        rows.append(
            {
                "AuditID": "SOURCE_NATIVE_AFTER_200_BLOCKER_AUDIT_V1",
                "TaskID": row["TaskID"],
                "Stage": row["Stage"],
                "CurrentlyAvailable": row["CurrentlyAvailable"],
                "BlocksSourceNativeScoring": row["BlocksSourceNativeScoring"],
                "BlockingIssue": row["BlockingIssue"],
                "NextAction": row["NextAction"],
                "ExpectedOutput": row["ExpectedOutput"],
                "After200Status": "still_blocking" if truthy(row["BlocksSourceNativeScoring"]) else "cleared_or_available",
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    rows.extend(
        [
            {
                "AuditID": "SOURCE_NATIVE_AFTER_200_BLOCKER_AUDIT_V1",
                "TaskID": "D_BRANCH_200_PROXY_EXPORT",
                "Stage": "proxy_preflight_scaleup",
                "CurrentlyAvailable": True,
                "BlocksSourceNativeScoring": False,
                "BlockingIssue": "none",
                "NextAction": "replace proxy D branch only with source-native symbolic family export when available",
                "ExpectedOutput": str(D200.relative_to(ROOT)),
                "After200Status": f"available: runs={d200['BootstrapRuns']}, finite={d200['FiniteRuns']}",
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "AuditID": "SOURCE_NATIVE_AFTER_200_BLOCKER_AUDIT_V1",
                "TaskID": "H_BRANCH_200_PROXY_EXPORT",
                "Stage": "proxy_preflight_scaleup",
                "CurrentlyAvailable": True,
                "BlocksSourceNativeScoring": False,
                "BlockingIssue": "none",
                "NextAction": "replace proxy H_D branch only with source-native symbolic family export when available",
                "ExpectedOutput": str(H200.relative_to(ROOT)),
                "After200Status": f"available: runs={h200['BootstrapRuns']}, finite={h200['FiniteRuns']}",
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "AuditID": "SOURCE_NATIVE_AFTER_200_BLOCKER_AUDIT_V1",
                "TaskID": "FULL_DH_200_PROXY_BACKREACTION",
                "Stage": "proxy_preflight_score",
                "CurrentlyAvailable": True,
                "BlocksSourceNativeScoring": False,
                "BlockingIssue": "none",
                "NextAction": "keep as preflight proxy benchmark; do not promote to source-native scoring",
                "ExpectedOutput": str(FULL200.relative_to(ROOT)),
                "After200Status": (
                    f"available: samples={full200['OmegaSamples']}, "
                    f"K2 beats proxy null={full200['K2BeatsSmokeBackreactionCases']}/{full200['RoutesScored']}"
                ),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
        ]
    )
    audit = pd.DataFrame(rows)
    audit.to_csv(OUT_AUDIT, index=False)

    source_native_ready = bool(
        truthy(export_validation["SourceNativeBackreactionExportsReady"])
        and truthy(uncertainty_validation["AnySourceNativeUncertaintyReady"])
    )
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_AFTER_200_BLOCKER_AUDIT_V1",
                "RequiredTasks": int(len(required)),
                "AvailableRequiredTasks": int((~required["BlocksSourceNativeScoring"].map(truthy)).sum()),
                "BlockingRequiredTasks": int(len(blocking)),
                "BlockingTaskIDs": ";".join(blocking["TaskID"].astype(str)),
                "DBranch200Ready": truthy(d200["FullBootstrapScale"]) and int(d200["FiniteRuns"]) == int(d200["BootstrapRuns"]),
                "HBranch200Ready": truthy(h200["FullBootstrapScale"]) and int(h200["FiniteRuns"]) == int(h200["BootstrapRuns"]),
                "FullProxy200Ready": truthy(full200["FullBootstrapScale"]) and int(full200["OmegaSamples"]) == 200,
                "K2DominatesProxy200": (
                    int(dominance["K2BeatsRegularizedNullRoutes"]) == int(dominance["RoutesScored"])
                    and int(dominance["K2BeatsRegularizedNullZones"]) == int(dominance["Zones"])
                ),
                "AuthorDerivativeVectorsAvailable": truthy(protocol["AuthorDerivativeVectorsAvailable"]),
                "SourceNativeExportsReady": truthy(export_validation["SourceNativeBackreactionExportsReady"]),
                "SourceNativeUncertaintyReady": truthy(uncertainty_validation["AnySourceNativeUncertaintyReady"]),
                "SourceNativeScoringReady": source_native_ready,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_BLOCKED_AFTER_200_PROXY_PREFLIGHT",
                "StrongestAllowedClaim": (
                    "the 200-bootstrap proxy benchmark is stable and favors locked K2, but source-native scoring remains blocked"
                ),
                "PrimaryResidualRisk": (
                    "missing author/reproduced symbolic family exports and source-native covariance prevent measurement validation"
                ),
                "NextAction": (
                    "obtain or reproduce source_native_reconstruction_vector.csv, source_native_selection_metadata.csv, "
                    "and source_native_backreaction_bootstrap_samples.csv or source_native_backreaction_covariance.csv"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    request_lines = [
        "# Source-Native Backreaction Request Packet After 200-Proxy Preflight",
        "",
        "The local 200-bootstrap proxy route is executable and favors locked K2 in the current preflight benchmark. It is still not source-native scoring.",
        "",
        "Please provide or reproduce these machine-readable objects:",
        "",
        "1. `source_native_reconstruction_vector.csv` with columns:",
        "   `FamilyID,SampleID,z,D,D_prime,D_double_prime,H_D,H_D_prime,Source,SelectionRule,ClaimBoundary`",
        "2. `source_native_selection_metadata.csv` with the symbolic-regression family metadata.",
        "3. Either `source_native_backreaction_bootstrap_samples.csv` or `source_native_backreaction_covariance.csv` for `Omega_R + 3Omega_Q` uncertainty.",
        "",
        "Do not use figure digitization for this source-native gate. Do not change locked K2.",
        "",
        "Current local proxy evidence:",
        f"- D branch 200 finite runs: {d200['FiniteRuns']}/{d200['BootstrapRuns']}",
        f"- H_D branch 200 finite runs: {h200['FiniteRuns']}/{h200['BootstrapRuns']}",
        f"- K2 beats proxy 200 null routes: {dominance['K2BeatsRegularizedNullRoutes']}/{dominance['RoutesScored']}",
        f"- K2 beats proxy 200 null zones: {dominance['K2BeatsRegularizedNullZones']}/{dominance['Zones']}",
        "",
        "Claim boundary: these files are required for a source-native benchmark. They do not by themselves authorize measurement validation.",
        "",
    ]
    OUT_REQUEST.write_text("\n".join(request_lines), encoding="utf-8")

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native After-200 Blocker Audit",
                "",
                "Status: SOURCE_NATIVE_BLOCKED_AFTER_200_PROXY_PREFLIGHT.",
                "",
                "The 200-bootstrap proxy route is now complete, but source-native scoring remains blocked because the author/reproduced symbolic family exports and their uncertainty are not available.",
                "",
                "## What Is Cleared",
                "",
                f"- D branch 200 ready: {summary.iloc[0]['DBranch200Ready']}",
                f"- H_D branch 200 ready: {summary.iloc[0]['HBranch200Ready']}",
                f"- Full proxy 200 ready: {summary.iloc[0]['FullProxy200Ready']}",
                f"- K2 dominates proxy 200: {summary.iloc[0]['K2DominatesProxy200']}",
                "",
                "## Remaining Required Objects",
                "",
                f"- Blocking required tasks: {summary.iloc[0]['BlockingTaskIDs']}",
                "",
                "## Boundary",
                "",
                "The proxy result is not source-native scoring, not measurement validation, and not a discovery claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_AUDIT.relative_to(ROOT)}")
    print(f"Wrote {OUT_REQUEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
