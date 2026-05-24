#!/usr/bin/env python3
"""Validate the no-score microscopic residue source specification."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_microscopic_residue_source_spec.csv"
SUMMARY = ROOT / "evidence/p_taucov_microscopic_residue_source_spec_summary.csv"
DOC = ROOT / "docs/p_taucov_microscopic_residue_source_spec.md"
OUT = ROOT / "evidence/p_taucov_microscopic_residue_source_spec_validation.csv"

AUDIT_ID = "P_TAUCOV_MICROSCOPIC_RESIDUE_SOURCE_SPEC_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_MICROSCOPIC_RESIDUE_SOURCE_SPEC_DEFINED_NO_OBJECT_NO_SCORING"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append(
            {
                "AuditID": AUDIT_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": True,
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [TABLE, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        table = pd.read_csv(TABLE)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        routes = set(table["SourceRouteID"].astype(str))
        required = {
            "MRS_ROUTE_A_COMPACT_SPECTRAL_RESIDUE",
            "MRS_ROUTE_B_BOUNDARY_DOMAIN_RESIDUE",
            "MRS_ROUTE_C_INDEX_RESIDUE",
            "MRS_ROUTE_D_PARENT_ACTION_HESSIAN_RESIDUE",
        }
        primary = table[table["Primary"].astype(bool)]

        add("status_expected", str(summary["Status"]) == EXPECTED_STATUS)
        add("all_routes_present", required.issubset(routes))
        add("exactly_one_primary", len(primary) == 1)
        add("primary_is_compact_spectral", len(primary) == 1 and str(primary.iloc[0]["SourceRouteID"]) == "MRS_ROUTE_A_COMPACT_SPECTRAL_RESIDUE")
        add("summary_next_artifact_declared", str(summary["NextAllowedArtifact"]) == "p_taucov_compact_spectral_residue_source_v1_no_score_preflight")
        add("records_parent_source_gap", float(summary["ResidueNormBeforeNormalization"]) < 1e-10)
        add("records_smooth_psd_loss", float(summary["ExpandedPrimaryMinusStrongestNull"]) < 0.0)
        add("no_route_authorizes_scoring", not bool(table["ScoringAuthorized"].any()))
        add("no_route_authorizes_survival", not bool(table["SurvivalClaimAuthorized"].any()))
        add("summary_scoring_false", bool(summary["ScoringAuthorized"]) is False)
        add("summary_tau_validation_false", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("doc_forbids_signal_claim", "Forbidden Claim" in doc and "produces a Tau Core signal" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_MICROSCOPIC_RESIDUE_SOURCE_SPEC_VALID" if ok else "P_TAUCOV_MICROSCOPIC_RESIDUE_SOURCE_SPEC_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
