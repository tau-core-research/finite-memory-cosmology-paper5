#!/usr/bin/env python3
"""Validate TCCS transfer-curvature protocol."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "evidence/p_taucov_tccs_transfer_curvature_protocol_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_tccs_transfer_curvature_protocol_summary.csv"
DOC = ROOT / "docs/p_taucov_tccs_transfer_curvature_protocol.md"
OUT = ROOT / "evidence/p_taucov_tccs_transfer_curvature_protocol_validation.csv"

AUDIT_ID = "P_TAUCOV_TCCS_TRANSFER_CURVATURE_PROTOCOL_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_TCCS_TRANSFER_CURVATURE_PROTOCOL_DEFINED_NO_OBJECT_NO_SCORING"


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append({"AuditID": AUDIT_ID, "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})


def main() -> int:
    rows: list[dict] = []
    for path in [GATES, SUMMARY, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [GATES, SUMMARY, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_TCCS_TRANSFER_CURVATURE_PROTOCOL_INVALID")
        return 1
    gates = pd.read_csv(GATES)
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    add(rows, "status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "object_not_constructed", bool(summary["ObjectConstructed"]) is False)
    add(rows, "scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False and not bool(gates["ScoringAuthorizedByGate"].any()))
    add(rows, "survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "doc_contains_corrected_object", "K_curv = Pi_perp [H,P] P [H,P]^T Pi_perp" in doc)
    add(rows, "doc_forbids_scoring_claim", "authorizes empirical scoring" in doc)
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_TCCS_TRANSFER_CURVATURE_PROTOCOL_VALID" if ok else "P_TAUCOV_TCCS_TRANSFER_CURVATURE_PROTOCOL_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
