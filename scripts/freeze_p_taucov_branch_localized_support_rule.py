#!/usr/bin/env python3
"""Freeze branch-localized support rule for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
COV_MAP = ROOT / "evidence/p_taucov_covariance_map_matrix.csv"
OUT = ROOT / "evidence/p_taucov_branch_localized_support_rule.csv"
SUMMARY = ROOT / "evidence/p_taucov_branch_localized_support_rule_summary.csv"
DOC = ROOT / "docs/p_taucov_branch_localized_support_rule.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_BRANCH_LOCALIZED_SUPPORT_RULE_FREEZE_v1"
CLAIM_BOUNDARY = "branch_localized_support_rule_freeze_no_scoring"


def main() -> int:
    cov = pd.read_csv(COV_MAP)
    cov["AbsValue"] = cov["Value"].abs()
    total = float(cov["AbsValue"].sum())
    cov["SupportMass"] = cov["AbsValue"] / total if total > 0.0 else 0.0
    cov = cov.sort_values(["SupportMass", "RowCoordinate", "ColumnCoordinate"], ascending=[False, True, True]).reset_index(drop=True)
    cov["CumulativeSupportMass"] = cov["SupportMass"].cumsum()
    cov["BranchSupport"] = cov["CumulativeSupportMass"].le(0.8) | (cov.index.to_series(index=cov.index) == 0)
    cov["ProtocolID"] = PROTOCOL_ID
    cov["FreezeID"] = FREEZE_ID
    cov["SupportSource"] = "target_blind_parent_action_covariance_map_abs_mass"
    cov["UsesTargetResiduals"] = False
    cov["UsesScoreOutcome"] = False
    cov["ScoringAuthorized"] = False
    cov["ClaimBoundary"] = CLAIM_BOUNDARY
    cov[
        [
            "ProtocolID",
            "FreezeID",
            "RowCoordinate",
            "ColumnCoordinate",
            "Value",
            "AbsValue",
            "SupportMass",
            "CumulativeSupportMass",
            "BranchSupport",
            "SupportSource",
            "UsesTargetResiduals",
            "UsesScoreOutcome",
            "ScoringAuthorized",
            "ClaimBoundary",
        ]
    ].to_csv(OUT, index=False)
    support = cov[cov["BranchSupport"]]
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_BRANCH_LOCALIZED_SUPPORT_RULE_FROZEN_NO_SCORING",
                "SupportRows": len(support),
                "TotalRows": len(cov),
                "SupportMass": float(support["SupportMass"].sum()),
                "Threshold": 0.8,
                "ScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Branch-Localized Support Rule",
                "",
                "Status: `P_TAUCOV_BRANCH_LOCALIZED_SUPPORT_RULE_FROZEN_NO_SCORING`.",
                "",
                "Branch support is selected from the absolute mass of the already",
                "declared target-blind parent-action covariance map. Rows are sorted",
                "by support mass and included until the cumulative mass reaches the",
                "frozen 0.8 threshold.",
                "",
                f"- support rows: `{len(support)}`",
                f"- support mass: `{float(support['SupportMass'].sum())}`",
                "- threshold: `0.8`",
                "",
                "No target residuals or score outcomes are used by this support rule.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("P_TAUCOV_BRANCH_LOCALIZED_SUPPORT_RULE_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
