#!/usr/bin/env python3
"""Validate the TCCS transfer-curvature preflight."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TRANSFER = ROOT / "evidence/p_taucov_tccs_transfer_preflight_matrix.csv"
CURV = ROOT / "evidence/p_taucov_tccs_transfer_curvature_preflight_matrix.csv"
GATES = ROOT / "evidence/p_taucov_tccs_transfer_curvature_preflight_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_tccs_transfer_curvature_preflight_summary.csv"
DOC = ROOT / "docs/p_taucov_tccs_transfer_curvature_preflight.md"
OUT = ROOT / "evidence/p_taucov_tccs_transfer_curvature_preflight_validation.csv"

AUDIT_ID = "P_TAUCOV_TCCS_TRANSFER_CURVATURE_PREFLIGHT_VALIDATION"
ALLOWED_STATUSES = {
    "P_TAUCOV_TCCS_TRANSFER_CURVATURE_PREFLIGHT_PASS_NO_SCORING",
    "P_TAUCOV_TCCS_TRANSFER_CURVATURE_PREFLIGHT_FAIL_NO_SCORING",
}


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append({"AuditID": AUDIT_ID, "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})


def main() -> int:
    rows: list[dict] = []
    for path in [TRANSFER, CURV, GATES, SUMMARY, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [TRANSFER, CURV, GATES, SUMMARY, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_TCCS_TRANSFER_CURVATURE_PREFLIGHT_INVALID")
        return 1
    gates = pd.read_csv(GATES)
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    status = str(summary["Status"])
    all_gates_pass = bool(gates["Passed"].all())
    add(rows, "status_allowed", status in ALLOWED_STATUSES)
    add(rows, "status_matches_gate_result", (status.endswith("PASS_NO_SCORING")) == all_gates_pass)
    add(rows, "scoring_not_authorized_gates", not bool(gates["ScoringAuthorized"].any()))
    add(rows, "scoring_not_authorized_summary", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "doc_forbids_validation_claim", "validated Tau Core" in doc)
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_TCCS_TRANSFER_CURVATURE_PREFLIGHT_VALID" if ok else "P_TAUCOV_TCCS_TRANSFER_CURVATURE_PREFLIGHT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
