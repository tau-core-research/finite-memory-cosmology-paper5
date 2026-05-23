#!/usr/bin/env python3
"""Validate the TCCS commutator no-go theorem artifact."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
THEOREM = ROOT / "evidence/p_taucov_tccs_commutator_nogo_theorem.csv"
DOC = ROOT / "docs/p_taucov_tccs_commutator_nogo_theorem.md"
OUT = ROOT / "evidence/p_taucov_tccs_commutator_nogo_theorem_validation.csv"

AUDIT_ID = "P_TAUCOV_TCCS_COMMUTATOR_NOGO_THEOREM_VALIDATION"
EXPECTED_STATUS = "TCCS_DOUBLE_SIDED_PERP_COMMUTATOR_NOGO_PROVEN"


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append({"AuditID": AUDIT_ID, "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})


def main() -> int:
    rows: list[dict] = []
    for path in [THEOREM, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [THEOREM, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_TCCS_COMMUTATOR_NOGO_THEOREM_INVALID")
        return 1
    theorem = pd.read_csv(THEOREM)
    doc = DOC.read_text(encoding="utf-8")
    add(rows, "all_rows_expected_status", set(theorem["Status"].astype(str)) == {EXPECTED_STATUS})
    add(rows, "contains_vanishing_result", "Pi_perp [H,P] Pi_perp = 0" in set(theorem["Expression"].astype(str)))
    add(rows, "doc_contains_proof", "Pi_perp H (P Pi_perp)" in doc and "(Pi_perp P) H Pi_perp" in doc)
    add(rows, "doc_forbids_empirical_signal", "empirical Tau signal" in doc)
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_TCCS_COMMUTATOR_NOGO_THEOREM_VALID" if ok else "P_TAUCOV_TCCS_COMMUTATOR_NOGO_THEOREM_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
