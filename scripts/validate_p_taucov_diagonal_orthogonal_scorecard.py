#!/usr/bin/env python3
"""Validate diagonal-orthogonal P-TauCov signed alignment scorecard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OOS = ROOT / "evidence/p_taucov_diagonal_orthogonal_oos_scorecard.csv"
NULLS = ROOT / "evidence/p_taucov_diagonal_orthogonal_null_scorecard.csv"
SUMMARY = ROOT / "evidence/p_taucov_diagonal_orthogonal_scorecard_summary.csv"
OUT = ROOT / "evidence/p_taucov_diagonal_orthogonal_scorecard_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_DIAGONAL_ORTHOGONAL_SCORECARD_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [OOS, NULLS, SUMMARY]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [OOS, NULLS, SUMMARY]):
        oos = pd.read_csv(OOS)
        nulls = pd.read_csv(NULLS)
        summary = pd.read_csv(SUMMARY).iloc[0]
        primary = oos[oos["PrimaryOOS"]]
        add("authorized_true", bool(summary["DiagonalOrthogonalScoringAuthorized"]) is True)
        add("covariance_survival_not_authorized", bool(summary["CovarianceSurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("measurement_not_authorized", bool(summary["MeasurementValidationAuthorized"]) is False)
        add("has_primary_oos", len(primary) > 0)
        add("has_nulls", len(nulls) >= 4)
        add("summary_primary_matches", abs(float(summary["PrimarySignedS"]) - float(primary["SignedS"].sum())) < 1e-9)
        add("claim_boundary", str(summary["ClaimBoundary"]) == "diagonal_orthogonal_alignment_scorecard_no_survival_claim")

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_DIAGONAL_ORTHOGONAL_SCORECARD_VALID" if ok else "P_TAUCOV_DIAGONAL_ORTHOGONAL_SCORECARD_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
