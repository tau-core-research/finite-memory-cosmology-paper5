#!/usr/bin/env python3
"""Validate the TCCS protocol spec."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "evidence/p_taucov_tccs_protocol_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_tccs_protocol_summary.csv"
DOC = ROOT / "docs/p_taucov_tccs_protocol.md"
OUT = ROOT / "evidence/p_taucov_tccs_protocol_validation.csv"

AUDIT_ID = "P_TAUCOV_TCCS_PROTOCOL_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_TCCS_PROTOCOL_DEFINED_NO_OBJECT_NO_SCORING"
REQUIRED_GATES = {
    "TCCS-G1_PARENT_HESSIAN_SOURCE",
    "TCCS-G2_COMMUTATOR_OBJECT",
    "TCCS-G3_PROJECTION_ORTHOGONALITY",
    "TCCS-G4_MORPHOLOGY_ORTHOGONALITY",
    "TCCS-G5_BALANCE_RETENTION",
    "TCCS-G6_FAMILY_BALANCE",
    "TCCS-G7_DIAGONAL_CONTROL",
    "TCCS-G8_ORIENTATION_ANCHOR",
    "TCCS-G9_SIGN_FLIP_NOT_EQUIVALENT",
    "TCCS-G10_TARGET_BLINDNESS",
}


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append({"AuditID": AUDIT_ID, "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})


def main() -> int:
    rows: list[dict] = []
    for path in [GATES, SUMMARY, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [GATES, SUMMARY, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_TCCS_PROTOCOL_INVALID")
        return 1
    gates = pd.read_csv(GATES)
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    add(rows, "status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "all_required_gates_present", REQUIRED_GATES.issubset(set(gates["GateID"].astype(str))))
    add(rows, "object_not_constructed", bool(summary["ObjectConstructed"]) is False)
    add(rows, "scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "formal_object_contains_commutator", "[L_B_red, P_morph]" in str(summary["FormalObject"]))
    add(rows, "doc_mentions_projection_orthogonal", "Pi_perp" in doc and "projection-null" in doc)
    add(rows, "doc_mentions_balance", "Pi_bal" in doc and "family/clock" in doc)
    add(rows, "doc_mentions_orientation_anchor", "J_tau" in doc and "Orient_+" in doc)
    add(rows, "doc_forbids_empirical_claim", "has produced a Tau signal" in doc)
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_TCCS_PROTOCOL_VALID" if ok else "P_TAUCOV_TCCS_PROTOCOL_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
