#!/usr/bin/env python3
"""Validate the P-TauCov delta_C_Tau construction contract."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_delta_c_tau_contract.md"
CSV = ROOT / "evidence/p_taucov_delta_c_tau_contract.csv"
YAML = ROOT / "evidence/p_taucov_delta_c_tau_contract.yaml"
OUT = ROOT / "evidence/p_taucov_delta_c_tau_contract_validation.csv"

REQUIRED_ITEMS = {
    "ProtocolID",
    "ContractID",
    "BranchEquation",
    "ProjectedMorphology",
    "TauMorphologyResponse",
    "CovarianceResponse",
    "AdmissibleInputs",
    "ForbiddenTargets",
    "OutputMatrix",
    "OutputNormalization",
    "LeakageAudit",
    "BranchSupportAuthorization",
    "PTauCovScoringAuthorization",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_DELTA_C_TAU_CONTRACT_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("csv_exists", CSV.exists())
    add("yaml_exists", YAML.exists())
    if not all(path.exists() for path in [DOC, CSV, YAML]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_DELTA_C_TAU_CONTRACT_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    yaml_text = YAML.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)

    add("required_items_present", REQUIRED_ITEMS.issubset(set(df["Item"])))
    add("all_required_before_scoring", df["RequiredBeforeScoring"].astype(bool).all())
    add("no_scoring_authorized", (df["ScoringAuthorized"].astype(str).str.lower() == "false").all())
    for phrase in [
        "B = B_*(\\Phi)",
        "\\delta B_*",
        "M_{\\rm proj}(\\Phi,B)",
        "T_{\\tau}",
        "\\delta C_{\\tau}",
        "Allowed Inputs",
        "Forbidden Inputs",
        "held-out residuals",
        "P5C v3 family-localized gain pattern",
        "does not authorize scoring",
        "branch-support freeze",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)
    add("branch_support_not_authorized", "branch_support_authorized: false" in yaml_text)
    add("delta_c_tau_artifact_absent", "delta_c_tau_artifact_present: false" in yaml_text)
    add("scoring_not_authorized_yaml", "scoring_authorized: false" in yaml_text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_DELTA_C_TAU_CONTRACT_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_DELTA_C_TAU_CONTRACT_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
