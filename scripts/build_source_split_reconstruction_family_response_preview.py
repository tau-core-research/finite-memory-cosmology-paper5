#!/usr/bin/env python3
"""Build a non-scoring preview reconstruction-family response export.

This converts existing source-split preflight rows into the frozen long-format
schema so the schema can be tested without writing the scoring candidate path.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.reconstruction_family import response_sign, validate_reconstruction_family_export

EVIDENCE = ROOT / "evidence"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
OUT = EVIDENCE / "source_split_reconstruction_family_response_preview.csv"
SUMMARY = EVIDENCE / "source_split_reconstruction_family_response_preview_summary.csv"


def family_row(source: pd.Series, family_id: str, family_type: str, source_product: str, value_column: str) -> dict[str, object]:
    value = float(source[value_column])
    return {
        "ExportID": "RF_RESPONSE_PREVIEW_V1",
        "FamilyID": family_id,
        "FamilyType": family_type,
        "SourceProductID": source_product,
        "TargetID": source["TargetID"],
        "GridIndex": int(source["GridIndex"]),
        "z_grid": float(source["z_grid"]),
        "x_coordinate": float(source["x_coordinate"]),
        "x_mapping": source["x_mapping"],
        "ResponseValue": value,
        "ResponseSigma": 1.0,
        "ResponseSign": response_sign(value),
        "CoordinateNative": True,
        "UsesPublicSN": family_type == "SN_branch",
        "UsesPublicBAO": family_type == "BAO_branch",
        "FittedInThisNote": False,
        "ClaimBoundary": "schema_preview_only_no_measurement_validation",
    }


def main() -> None:
    target = pd.read_csv(TARGET)
    usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")]
    rows: list[dict[str, object]] = []
    for _, source in usable.iterrows():
        rows.append(
            family_row(
                source,
                family_id="RFAM_SN_RESIDUAL_BRANCH",
                family_type="SN_branch",
                source_product="PANTHEON_PLUS_SH0ES_SN",
                value_column="SNStandardizedResidual",
            )
        )
        rows.append(
            family_row(
                source,
                family_id="RFAM_BAO_RESIDUAL_BRANCH",
                family_type="BAO_branch",
                source_product="DESI_DR2_BAO_ALL_GAUSSIAN",
                value_column="BAOStandardizedResidual",
            )
        )

    preview = pd.DataFrame(rows)
    preview.to_csv(OUT, index=False)

    validation_issues = validate_reconstruction_family_export(preview, target)
    pair_signs = preview.pivot(index="GridIndex", columns="FamilyID", values="ResponseSign")
    sign_stable = pair_signs.apply(lambda row: len(set(row.dropna().astype(int))) == 1, axis=1)
    summary = pd.DataFrame(
        [
            {
                "PreviewID": "RF_RESPONSE_PREVIEW_V1",
                "Rows": len(preview),
                "Families": int(preview["FamilyID"].nunique()),
                "UsableTargetRows": len(usable),
                "SchemaValid": not validation_issues,
                "ValidationIssue": ";".join(validation_issues),
                "FamilySignStableRows": int(sign_stable.sum()),
                "FamilySignUnstableRows": int((~sign_stable).sum()),
                "AllowedForK2Scoring": False,
                "BlockingIssue": "preview_not_scoring_candidate;family_level_rule_not_locked;covariance_policy_not_promoted",
                "NextAction": "If accepted, export a real candidate to data/reconstruction_families/source_split_reconstruction_family_responses.csv and rerun validation.",
                "ClaimBoundary": "schema_preview_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
