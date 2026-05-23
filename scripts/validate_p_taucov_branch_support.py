#!/usr/bin/env python3
"""Validate the P-TauCov branch-support freeze template."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_branch_support_freeze.md"
CSV = ROOT / "evidence/p_taucov_branch_support_freeze.csv"
YAML = ROOT / "evidence/p_taucov_branch_support_freeze.yaml"
OUT = ROOT / "evidence/p_taucov_branch_support_validation.csv"


REQUIRED_ITEMS = {
    "ProtocolID",
    "FreezeID",
    "BranchSupportSource",
    "DefaultContinuousWeight",
    "DefaultBinarySupport",
    "q_branch",
    "ForbiddenInputP5Cv3GainPattern",
    "ForbiddenInputHeldOutResiduals",
    "ForbiddenInputDominantFamily",
    "P5Cv3Status",
    "V4KernelAuthorized",
    "PTauCovScoringAuthorized",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_BRANCH_SUPPORT_VALIDATION",
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
        print("P_TAUCOV_BRANCH_SUPPORT_TEMPLATE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    manifest_text = YAML.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)

    add("required_items_present", REQUIRED_ITEMS.issubset(set(df["Item"])))
    add("no_scoring_authorized", (df["ScoringAuthorized"].astype(str).str.lower() == "false").all())
    add(
        "branch_support_source_delta_c_tau_only",
        df.loc[df["Item"].eq("BranchSupportSource"), "Value"].iloc[0] == "delta_C_Tau_only",
    )
    add(
        "q_branch_not_set",
        df.loc[df["Item"].eq("q_branch"), "Value"].iloc[0] == "NOT_SET",
    )
    add(
        "v4_not_authorized",
        df.loc[df["Item"].eq("V4KernelAuthorized"), "Status"].iloc[0] == "NOT_AUTHORIZED",
    )
    add(
        "p_taucov_scoring_not_authorized",
        df.loc[df["Item"].eq("PTauCovScoringAuthorized"), "Status"].iloc[0] == "NOT_AUTHORIZED",
    )
    add("doc_contains_default_weight", "W_{\\rm branch}(i,j)" in text)
    add("doc_contains_hard_blocks", "Hard Blocks" in text and "held-out residuals" in text)
    add("yaml_scoring_false", "scoring_authorized: false" in manifest_text)
    add("yaml_v4_false", "v4_kernel_authorized: false" in manifest_text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_BRANCH_SUPPORT_TEMPLATE_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_BRANCH_SUPPORT_TEMPLATE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
