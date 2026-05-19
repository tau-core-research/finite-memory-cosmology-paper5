#!/usr/bin/env python3
"""Build a non-scoring family-level sign-stability preview."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.reconstruction_family import family_sign_status

EVIDENCE = ROOT / "evidence"
PREVIEW = EVIDENCE / "source_split_reconstruction_family_response_preview.csv"
OUT = EVIDENCE / "source_split_family_sign_rule_preview.csv"
SUMMARY = EVIDENCE / "source_split_family_sign_rule_preview_summary.csv"


def main() -> None:
    preview = pd.read_csv(PREVIEW)
    rows = []
    for grid_index, group in preview.groupby("GridIndex", sort=True):
        signs = [int(value) for value in group["ResponseSign"].tolist()]
        status = family_sign_status(signs)
        sign_map = ";".join(
            f"{row.FamilyID}:{int(row.ResponseSign)}" for row in group.itertuples(index=False)
        )
        values = ";".join(
            f"{row.FamilyID}:{float(row.ResponseValue):.12g}" for row in group.itertuples(index=False)
        )
        first = group.iloc[0]
        rows.append(
            {
                "RulePreviewID": "RF_FAMILY_SIGN_RULE_PREVIEW_V1",
                "ExportID": first["ExportID"],
                "TargetID": first["TargetID"],
                "GridIndex": int(grid_index),
                "z_grid": float(first["z_grid"]),
                "x_coordinate": float(first["x_coordinate"]),
                "x_mapping": first["x_mapping"],
                "FamilyCount": int(group["FamilyID"].nunique()),
                "FamilySigns": sign_map,
                "FamilyResponseValues": values,
                "FamilySignStatus": status,
                "FamilySignStable": status == "FAMILY_SIGN_STABLE",
                "WarningPolicy": "unstable family signs remain warnings and are not hidden support or hidden rejection",
                "AllowedForK2Scoring": False,
                "BlockingIssue": "sign_rule_preview_only;candidate_export_missing;scoring_rule_not_locked",
                "ClaimBoundary": "sign_rule_preview_only_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "RulePreviewID": "RF_FAMILY_SIGN_RULE_PREVIEW_V1",
                "Rows": len(output),
                "StableRows": int(output["FamilySignStable"].sum()),
                "WarningRows": int((~output["FamilySignStable"]).sum()),
                "Rule": "stable if all nonzero public reconstruction-family signs agree",
                "AllowedForK2Scoring": False,
                "BlockingIssue": "sign_rule_preview_only;candidate_export_missing;scoring_rule_not_locked",
                "NextAction": "Promote only after a real candidate export exists and the rule is registered for scoring.",
                "ClaimBoundary": "sign_rule_preview_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
