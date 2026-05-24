#!/usr/bin/env python3
"""Validate compact spectral P-TauCov scorecard artifacts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "in_sample": ROOT / "evidence/p_taucov_compact_spectral_scorecard.csv",
    "oos": ROOT / "evidence/p_taucov_compact_spectral_oos_scorecard.csv",
    "nulls": ROOT / "evidence/p_taucov_compact_spectral_null_scorecard.csv",
    "gates": ROOT / "evidence/p_taucov_compact_spectral_survival_gates.csv",
    "summary": ROOT / "evidence/p_taucov_compact_spectral_scorecard_summary.csv",
    "doc": ROOT / "docs/p_taucov_compact_spectral_scorecard.md",
}
OUT = ROOT / "evidence/p_taucov_compact_spectral_scorecard_validation.csv"

AUDIT_ID = "P_TAUCOV_COMPACT_SPECTRAL_SCORECARD_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_COMPACT_SPECTRAL_PRIMARY_SCORECARD_DOES_NOT_SURVIVE_NO_CLAIM"
CLAIM_BOUNDARY = "compact_spectral_primary_scorecard_no_survival_claim"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append(
            {
                "AuditID": AUDIT_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for key, path in FILES.items():
        add(f"exists_{key}", path.exists())

    if all(path.exists() for path in FILES.values()):
        summary = pd.read_csv(FILES["summary"]).iloc[0]
        gates = pd.read_csv(FILES["gates"])
        nulls = pd.read_csv(FILES["nulls"])
        oos = pd.read_csv(FILES["oos"])
        doc = FILES["doc"].read_text(encoding="utf-8")
        add("status_non_survivor", str(summary["CurrentStatus"]) == EXPECTED_STATUS)
        add("claim_boundary_matches", str(summary["ClaimBoundary"]) == CLAIM_BOUNDARY)
        add("scoring_authorized_true", bool(summary["PTauCovScoringAuthorized"]))
        add("survival_false", not bool(summary["SurvivalClaimAuthorized"]))
        add("measurement_false", not bool(summary["MeasurementValidationAuthorized"]))
        add("tau_validation_false", not bool(summary["TauCoreValidationClaimAuthorized"]))
        add("eight_gates_present", len(gates) == 8)
        add("gate_counts_match_summary", int(gates["Passed"].sum()) == int(summary["GatesPassed"]))
        add("all_required_nulls_present", len(nulls) == 8)
        add("primary_oos_rows_present", len(oos[oos["PrimaryOOS"]]) > 0)
        add("doc_forbids_validation_claim", "does not authorize survival" in doc and "Tau Core validation claim" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    required_ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_COMPACT_SPECTRAL_SCORECARD_VALID" if required_ok else "P_TAUCOV_COMPACT_SPECTRAL_SCORECARD_INVALID")
    return 0 if required_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
