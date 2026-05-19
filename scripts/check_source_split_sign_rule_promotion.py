#!/usr/bin/env python3
"""Check whether the family sign-rule preview can be promoted to scoring."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
PREVIEW_SUMMARY = EVIDENCE / "source_split_family_sign_rule_preview_summary.csv"
EXPORT_VALIDATION = EVIDENCE / "source_split_reconstruction_family_export_validation.csv"
OUT = EVIDENCE / "source_split_sign_rule_promotion_readiness.csv"


def main() -> None:
    preview = pd.read_csv(PREVIEW_SUMMARY).iloc[0]
    validation = pd.read_csv(EXPORT_VALIDATION).iloc[0]
    checks = [
        {
            "CheckID": "SRP1_PREVIEW_RULE_DECLARED",
            "Requirement": "Family sign-stability preview rule exists",
            "Available": True,
            "Evidence": "source_split_family_sign_rule_preview_summary.csv",
            "BlockingIssue": "",
            "NextAction": "Keep as preview until candidate export exists.",
        },
        {
            "CheckID": "SRP2_CANDIDATE_EXPORT_EXISTS",
            "Requirement": "Real reconstruction-family candidate export exists",
            "Available": bool(validation["Available"]),
            "Evidence": "source_split_reconstruction_family_export_validation.csv",
            "BlockingIssue": "" if bool(validation["Available"]) else "candidate_export_missing",
            "NextAction": "Export data/reconstruction_families/source_split_reconstruction_family_responses.csv.",
        },
        {
            "CheckID": "SRP3_CANDIDATE_EXPORT_VALID",
            "Requirement": "Candidate export passes schema validation",
            "Available": bool(validation["AllowedForK2Scoring"]),
            "Evidence": "source_split_reconstruction_family_export_validation.csv",
            "BlockingIssue": "" if bool(validation["AllowedForK2Scoring"]) else str(validation["BlockingIssue"]),
            "NextAction": "Fix candidate export until validation is clean.",
        },
        {
            "CheckID": "SRP4_WARNING_ROWS_RETAINED",
            "Requirement": "Warning rows remain warnings and are not hidden support",
            "Available": True,
            "Evidence": "source_split_family_sign_rule_preview.csv",
            "BlockingIssue": "",
            "NextAction": "Carry warning labels into future scorecard.",
        },
        {
            "CheckID": "SRP5_RULE_PROMOTION_AUTHORIZED",
            "Requirement": "Rule can be promoted to scoring rule",
            "Available": False,
            "Evidence": "source_split_family_sign_rule_preview_summary.csv",
            "BlockingIssue": "candidate_export_missing;scoring_rule_not_locked",
            "NextAction": "Promote only after a valid candidate export exists.",
        },
    ]
    output = pd.DataFrame(checks)
    if bool(validation["AllowedForK2Scoring"]):
        output.loc[output["CheckID"].eq("SRP5_RULE_PROMOTION_AUTHORIZED"), "Available"] = True
        output.loc[output["CheckID"].eq("SRP5_RULE_PROMOTION_AUTHORIZED"), "BlockingIssue"] = ""
        output.loc[output["CheckID"].eq("SRP5_RULE_PROMOTION_AUTHORIZED"), "NextAction"] = "Register scoring rule before K2/null scorecard."

    output["StableRows"] = int(preview["StableRows"])
    output["WarningRows"] = int(preview["WarningRows"])
    output["AllowedForK2Scoring"] = output["CheckID"].eq("SRP5_RULE_PROMOTION_AUTHORIZED") & output[
        "Available"
    ].astype(bool)
    output["ClaimBoundary"] = "sign_rule_promotion_readiness_only_no_measurement_validation"
    output.to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
