#!/usr/bin/env python3
"""Validate the P-TauCov minimal nonzero route freeze."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_minimal_nonzero_route_freeze.md"
CSV = ROOT / "evidence/p_taucov_minimal_nonzero_route_freeze.csv"
SUMMARY = ROOT / "evidence/p_taucov_minimal_nonzero_route_freeze_summary.csv"
PRESCORE = ROOT / "evidence/p_taucov_linear_specificity_prescore_summary.csv"
OUT = ROOT / "evidence/p_taucov_minimal_nonzero_route_freeze_validation.csv"


def bool_from_csv(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_MINIMAL_NONZERO_ROUTE_FREEZE_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [DOC, CSV, SUMMARY, PRESCORE]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if not all(path.exists() for path in [DOC, CSV, SUMMARY, PRESCORE]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_MINIMAL_NONZERO_ROUTE_FREEZE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)
    prescore = pd.read_csv(PRESCORE)

    add("prescore_failed_strict_linear", prescore["Status"].iloc[0] == "FAIL_STRICT_LINEAR_REJECTED")
    add(
        "primary_route_is_epsilon_p",
        summary["FrozenPrimaryRoute"].iloc[0] == "EPSILON_P_PROJECTION_RESPONSE_PRIMARY",
    )
    add("lambda_route_reserved", summary["ReservedRoute"].iloc[0] == "LAMBDA_B_BRANCH_BACKREACTION_RESERVED")
    add("projection_operator_not_ready", not bool_from_csv(summary["ProjectionOperatorPacketReady"].iloc[0]))
    add("linear_candidate_not_frozen", not bool_from_csv(summary["LinearCandidateFrozen"].iloc[0]))
    add("scoring_not_authorized_summary", not bool_from_csv(summary["PTauCovScoringAuthorized"].iloc[0]))
    add("two_routes_declared", set(df["RouteID"]) == {"EPSILON_P_PROJECTION_RESPONSE_PRIMARY", "LAMBDA_B_BRANCH_BACKREACTION_RESERVED"})
    add("no_outcome_used", not df["OutcomeInformationUsed"].map(bool_from_csv).any())
    add("no_residual_used", not df["ResidualInformationUsed"].map(bool_from_csv).any())
    add("no_score_used", not df["ScoreInformationUsed"].map(bool_from_csv).any())
    add("no_p5c_v3_used", not df["P5CV3OutcomeUsed"].map(bool_from_csv).any())
    add("scoring_not_authorized_rows", not df["PTauCovScoringAuthorized"].map(bool_from_csv).any())

    for phrase in [
        "T_tau = A_Phi + A_B L0_B^+ R_B = 0",
        "epsilon_P projection-response perturbation",
        "lambda_B branch-backreaction perturbation",
        "P1_projection_response_operator",
        "use target residuals",
        "Forbidden statement",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_MINIMAL_NONZERO_ROUTE_FREEZE_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_MINIMAL_NONZERO_ROUTE_FREEZE_VALID_EPSILON_P_FIRST_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
