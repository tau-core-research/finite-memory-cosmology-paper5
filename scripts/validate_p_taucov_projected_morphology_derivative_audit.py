#!/usr/bin/env python3
"""Validate the projected morphology derivative audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "evidence/p_taucov_projected_morphology_derivative_b.csv"
DPHI = ROOT / "evidence/p_taucov_projected_morphology_derivative_phi.csv"
AUDIT = ROOT / "evidence/p_taucov_projected_morphology_derivative_audit.csv"
SUMMARY = ROOT / "evidence/p_taucov_projected_morphology_derivative_summary.csv"
DOC = ROOT / "docs/p_taucov_projected_morphology_derivative_audit.md"
OUT = ROOT / "evidence/p_taucov_projected_morphology_derivative_validation.csv"

AUDIT_ID = "P_TAUCOV_PROJECTED_MORPHOLOGY_DERIVATIVE_VALIDATION"


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

    for path in [DB, DPHI, AUDIT, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [DB, DPHI, AUDIT, SUMMARY, DOC]):
        db = pd.read_csv(DB)
        dphi = pd.read_csv(DPHI)
        audit = pd.read_csv(AUDIT)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_pass_no_scoring", str(summary["Status"]) == "P_TAUCOV_PROJECTED_MORPHOLOGY_DERIVATIVE_PASS_NO_SCORING")
        add("all_gates_pass", bool(audit["Passed"].all()))
        add("db_nonzero", float(summary["DBMProjFrobeniusNorm"]) > 0.0 and len(db) > 0)
        add("dphi_nonzero", float(summary["DPhiMProjFrobeniusNorm"]) > 0.0 and len(dphi) > 0)
        add("strict_linear_formula_recorded", str(summary["StrictLinearFormula"]) == "D_B_M_proj=P0*A_B;D_Phi_M_proj=P0*A_Phi")
        add("db_pmorph_term_not_included", bool(summary["DBPmorhTermIncluded"]) is False)
        add("resolves_db_mproj_blocker", str(summary["ResolvesBlocker"]) == "D_B_M_proj")
        add("physical_model_still_open", "PHYSICAL_MORPHOLOGY_MODEL" in str(summary["StillOpen"]))
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("doc_forbids_physical_validation", "physical morphology model" in doc and "validates Tau Core" in doc)
        add("uses_no_target_or_score", not bool(db["UsesTargetResiduals"].any()) and not bool(dphi["UsesScoreOutcome"].any()))

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PROJECTED_MORPHOLOGY_DERIVATIVE_VALID" if ok else "P_TAUCOV_PROJECTED_MORPHOLOGY_DERIVATIVE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
