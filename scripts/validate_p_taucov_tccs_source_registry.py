#!/usr/bin/env python3
"""Validate the TCCS source registry."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "evidence/p_taucov_tccs_source_registry.csv"
SUMMARY = ROOT / "evidence/p_taucov_tccs_source_registry_summary.csv"
DOC = ROOT / "docs/p_taucov_tccs_source_registry.md"
OUT = ROOT / "evidence/p_taucov_tccs_source_registry_validation.csv"

AUDIT_ID = "P_TAUCOV_TCCS_SOURCE_REGISTRY_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_TCCS_SOURCE_REGISTRY_READY_OBJECT_BLOCKED"
REQUIRED_COMPONENTS = {"L_B_red", "P_morph", "Pi_perp", "Pi_bal", "J_tau", "TCCS_OBJECT"}


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append(
        {
            "AuditID": AUDIT_ID,
            "CheckID": check_id,
            "Passed": bool(passed),
            "Required": True,
            "Status": "PASS" if passed else "FAIL",
        }
    )


def main() -> int:
    rows: list[dict] = []
    for path in [REGISTRY, SUMMARY, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [REGISTRY, SUMMARY, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_TCCS_SOURCE_REGISTRY_INVALID")
        return 1

    registry = pd.read_csv(REGISTRY)
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    components = set(registry["ComponentID"].astype(str))

    add(rows, "status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "all_required_components_present", REQUIRED_COMPONENTS.issubset(components))
    add(rows, "j_tau_marked_missing", bool(registry[registry["ComponentID"].eq("J_tau")]["SourceExists"].iloc[0]) is False)
    add(rows, "tccs_object_blocked", "BLOCKED" in str(registry[registry["ComponentID"].eq("TCCS_OBJECT")]["SourceStatus"].iloc[0]))
    add(rows, "scoring_not_authorized_registry", not bool(registry["ScoringAuthorized"].any()))
    add(rows, "scoring_not_authorized_summary", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "object_not_constructed", bool(summary["ObjectConstructed"]) is False)
    add(rows, "survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "doc_mentions_previous_projection_failure", "projection-null" in doc and "previous parent-Hessian commutator" in doc)
    add(rows, "doc_forbids_signal_claim", "shown to carry a Tau signal" in doc)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_TCCS_SOURCE_REGISTRY_VALID" if ok else "P_TAUCOV_TCCS_SOURCE_REGISTRY_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
