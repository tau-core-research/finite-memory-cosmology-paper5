#!/usr/bin/env python3
"""Build the reconstruction-family upgrade contract for source-split signs.

The existing TQ4 artifact exports public SN/BAO branch signs. This script
records what is still required before that branch-sign preflight can become a
scoring-grade public reconstruction-family sign export.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
SIGN = EVIDENCE / "source_split_public_sign_family.csv"
OUT = EVIDENCE / "source_split_reconstruction_family_upgrade_contract.csv"
SUMMARY = EVIDENCE / "source_split_reconstruction_family_upgrade_summary.csv"


REQUIREMENTS = [
    {
        "RequirementID": "RF1_PUBLIC_RECONSTRUCTION_FAMILIES",
        "Requirement": "Declare at least two public reconstruction families in source-split target space",
        "CurrentArtifact": "source_split_public_sign_family.csv",
        "CurrentStatus": "BRANCH_SIGN_PREFLIGHT_ONLY",
        "Available": False,
        "BlockingIssue": "reconstruction_families_missing",
        "NextAction": "Export public reconstruction-family responses on the coordinate-native target rows.",
    },
    {
        "RequirementID": "RF2_ROW_ALIGNED_SIGNS",
        "Requirement": "Every reconstruction-family sign must be row-aligned to the coordinate-native target",
        "CurrentArtifact": "source_split_public_sign_family.csv",
        "CurrentStatus": "TARGET_ROWS_AVAILABLE",
        "Available": True,
        "BlockingIssue": "",
        "NextAction": "Reuse the existing target row IDs and x_chi coordinate.",
    },
    {
        "RequirementID": "RF3_SIGN_STABLE_RULE",
        "Requirement": "Declare sign-stable rule across reconstruction families before scoring",
        "CurrentArtifact": "source_split_public_sign_family.csv",
        "CurrentStatus": "BRANCH_RULE_AVAILABLE_NOT_FAMILY_RULE",
        "Available": False,
        "BlockingIssue": "family_level_sign_rule_missing",
        "NextAction": "Define stable if all declared public reconstruction-family signs agree.",
    },
    {
        "RequirementID": "RF4_WARNING_POLICY",
        "Requirement": "Retain sign-unstable rows as warnings instead of hidden support or hidden rejection",
        "CurrentArtifact": "docs/sign_family_export_plan.md",
        "CurrentStatus": "POLICY_DECLARED",
        "Available": True,
        "BlockingIssue": "",
        "NextAction": "Carry warning labels into the future K2/null scorecard.",
    },
    {
        "RequirementID": "RF5_NO_K2_SCORING",
        "Requirement": "Keep K2 scoring closed until reconstruction-family signs are exported",
        "CurrentArtifact": "source_split_gate_dashboard.csv",
        "CurrentStatus": "SCORING_BLOCKED",
        "Available": True,
        "BlockingIssue": "",
        "NextAction": "Do not run source-split K2/null scorecard yet.",
    },
]


def main() -> None:
    sign = pd.read_csv(SIGN)
    usable = sign[sign["HasTargetRow"].astype(str).str.lower().eq("true")]
    rows = []
    for item in REQUIREMENTS:
        row = dict(item)
        row["ContractID"] = "SOURCE_SPLIT_RECONSTRUCTION_FAMILY_UPGRADE_V1"
        row["CoordinateNativeRows"] = len(sign)
        row["UsableRows"] = len(usable)
        row["AllowedForK2Scoring"] = False
        row["ClaimBoundary"] = "upgrade_contract_only_no_measurement_validation"
        rows.append(row)

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    blockers = output[~output["Available"]]
    summary = pd.DataFrame(
        [
            {
                "ContractID": "SOURCE_SPLIT_RECONSTRUCTION_FAMILY_UPGRADE_V1",
                "Requirements": len(output),
                "SatisfiedRequirements": int(output["Available"].sum()),
                "BlockingRequirements": len(blockers),
                "BlockingIssue": ";".join(blockers["BlockingIssue"].astype(str).tolist()),
                "NextTask": "export_public_reconstruction_family_responses",
                "AllowedForK2Scoring": False,
                "Status": "RECONSTRUCTION_FAMILY_UPGRADE_REQUIRED",
                "NextAction": "Export public reconstruction-family signs before source-split K2/null scorecard.",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
