#!/usr/bin/env python3
"""Build readiness packet for diagonal-orthogonal P-TauCov candidate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "evidence/p_taucov_diagonal_orthogonal_candidate_summary.csv"
FAMILY = ROOT / "evidence/p_taucov_family_balance_policy_summary.csv"
NULLS = ROOT / "evidence/p_taucov_signed_response_null_policy_summary.csv"
AGG = ROOT / "evidence/p_taucov_signed_response_aggregation_policy_summary.csv"
STAT = ROOT / "evidence/p_taucov_signed_response_statistic_summary.csv"
OUT = ROOT / "evidence/p_taucov_diagonal_orthogonal_readiness.csv"
SUMMARY = ROOT / "evidence/p_taucov_diagonal_orthogonal_readiness_summary.csv"
DOC = ROOT / "docs/p_taucov_diagonal_orthogonal_readiness.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
READINESS_ID = "P_TAUCOV_DIAGONAL_ORTHOGONAL_READINESS_v1"
CLAIM_BOUNDARY = "diagonal_orthogonal_readiness_no_scoring"


def status(path: Path) -> str:
    return str(pd.read_csv(path).iloc[0]["Status"]) if path.exists() else "MISSING"


def main() -> int:
    checks = [
        ("READY-01_CANDIDATE", CANDIDATE, "P_TAUCOV_DIAGONAL_ORTHOGONAL_CANDIDATE_SPEC_PASS_NO_SCORING"),
        ("READY-02_FAMILY_BALANCE", FAMILY, "P_TAUCOV_FAMILY_BALANCE_POLICY_FROZEN_NO_SCORING"),
        ("READY-03_SIGNED_NULLS", NULLS, "P_TAUCOV_SIGNED_RESPONSE_NULL_POLICY_FROZEN_NO_SCORING"),
        ("READY-04_SIGNED_AGGREGATION", AGG, "P_TAUCOV_SIGNED_RESPONSE_AGGREGATION_POLICY_FROZEN_NO_SCORING"),
        ("READY-05_SIGNED_STATISTIC", STAT, "P_TAUCOV_SIGNED_RESPONSE_STATISTIC_FROZEN_NO_SCORING"),
    ]
    rows = []
    for check_id, path, expected in checks:
        observed = status(path)
        rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "ReadinessID": READINESS_ID,
                "CheckID": check_id,
                "ExpectedStatus": expected,
                "ObservedStatus": observed,
                "Passed": observed == expected,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(OUT, index=False)
    ready = bool(table["Passed"].all())
    status_text = (
        "P_TAUCOV_DIAGONAL_ORTHOGONAL_READY_FOR_MANIFEST_NO_SCORING"
        if ready
        else "P_TAUCOV_DIAGONAL_ORTHOGONAL_READINESS_BLOCKED_NO_SCORING"
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "ReadinessID": READINESS_ID,
                "Status": status_text,
                "ChecksPassed": int(table["Passed"].sum()),
                "ChecksTotal": len(table),
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Diagonal-Orthogonal Readiness",
                "",
                f"Status: `{status_text}`.",
                "",
                "This packet checks whether the diagonal-orthogonal signed candidate",
                "has all pre-scoring protections required after the previous negative",
                "results.",
                "",
                f"- checks passed: `{int(table['Passed'].sum())}/{len(table)}`",
                "",
                "It does not authorize scoring. A separate final manifest is still",
                "required.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
