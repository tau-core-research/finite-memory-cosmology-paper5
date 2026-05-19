#!/usr/bin/env python3
"""Build the external source-split K1 export schema and template."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
SCHEMA_OUT = EVIDENCE / "source_split_external_k1_export_schema.csv"
TEMPLATE_OUT = EVIDENCE / "source_split_external_k1_export_template.csv"

REQUIRED_COLUMNS = [
    "K1TargetID",
    "SourceTargetID",
    "GridIndex",
    "z_grid",
    "x_coordinate",
    "x_mapping",
    "K1Response",
    "K1Sigma",
    "K1SourceID",
    "ProvenanceType",
    "CoordinateNative",
    "LikelihoodNative",
    "UsesPublicSN",
    "UsesPublicBAO",
    "UsesJointCovariance",
    "SameDataAmplitudeFit",
    "FittedInThisNote",
    "AmplitudePolicy",
    "Predeclared",
    "AllowedAsPrimaryK1Candidate",
    "ClaimBoundary",
]


def schema() -> pd.DataFrame:
    descriptions = {
        "K1TargetID": "Stable identifier for the external source-split K1 target.",
        "SourceTargetID": "Coordinate-native source-split target id matched row by row.",
        "GridIndex": "Integer row key from evidence/source_split_coordinate_native_target.csv.",
        "z_grid": "Redshift grid value copied from the source-split target.",
        "x_coordinate": "Coordinate-native x value copied from the source-split target.",
        "x_mapping": "Coordinate mapping identifier copied from the source-split target.",
        "K1Response": "Externally derived nonzero K1/no-memory response value.",
        "K1Sigma": "Positive uncertainty scale for K1Response under the declared covariance policy.",
        "K1SourceID": "Public source or reproducible model-export identifier.",
        "ProvenanceType": "Allowed examples: external_reconstruction_family_mean, likelihood_native_baseline, independent_public_model_response.",
        "CoordinateNative": "Must be true for source-split scoring.",
        "LikelihoodNative": "True only if generated in the likelihood-native benchmark; false is allowed for coordinate-native preflight.",
        "UsesPublicSN": "Must be true for source-split scoring.",
        "UsesPublicBAO": "Must be true for source-split scoring.",
        "UsesJointCovariance": "Must be true for source-split scoring.",
        "SameDataAmplitudeFit": "Must be false; same-data amplitude rescue is not allowed.",
        "FittedInThisNote": "Must be false; this note may not fit K1 to rescue K2.",
        "AmplitudePolicy": "Predeclared amplitude/normalization policy.",
        "Predeclared": "Must be true; K1 must be frozen before locked K2 scoring.",
        "AllowedAsPrimaryK1Candidate": "Set true only if the export is intended as a primary K1 candidate.",
        "ClaimBoundary": "Must state no measurement validation from this export alone.",
    }
    return pd.DataFrame(
        [
            {
                "Column": column,
                "Required": True,
                "Description": descriptions[column],
            }
            for column in REQUIRED_COLUMNS
        ]
    )


def template() -> pd.DataFrame:
    target = pd.read_csv(TARGET)
    usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    rows = []
    for _, row in usable.sort_values("GridIndex").iterrows():
        rows.append(
            {
                "K1TargetID": "SSK1_EXTERNAL_NONZERO_SOURCE_SPLIT_TARGET",
                "SourceTargetID": row["TargetID"],
                "GridIndex": int(row["GridIndex"]),
                "z_grid": float(row["z_grid"]),
                "x_coordinate": float(row["x_coordinate"]),
                "x_mapping": row["x_mapping"],
                "K1Response": "",
                "K1Sigma": "",
                "K1SourceID": "TO_BE_DECLARED",
                "ProvenanceType": "TO_BE_DECLARED",
                "CoordinateNative": True,
                "LikelihoodNative": False,
                "UsesPublicSN": True,
                "UsesPublicBAO": True,
                "UsesJointCovariance": True,
                "SameDataAmplitudeFit": False,
                "FittedInThisNote": False,
                "AmplitudePolicy": "TO_BE_DECLARED",
                "Predeclared": True,
                "AllowedAsPrimaryK1Candidate": False,
                "ClaimBoundary": "external_k1_export_only_no_measurement_validation",
            }
        )
    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)


def main() -> None:
    schema().to_csv(SCHEMA_OUT, index=False)
    template().to_csv(TEMPLATE_OUT, index=False)
    print(f"Wrote {SCHEMA_OUT}")
    print(f"Wrote {TEMPLATE_OUT}")


if __name__ == "__main__":
    main()
