#!/usr/bin/env python3
"""Build the source-native backreaction upgrade matrix.

This is a focused blocker map for replacing the provisional BAO-only
backreaction bridge with the source-native reconstruction used by the published
backreaction addendum. It does not digitize figures, fit K2, change locked K2,
or authorize measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"

OUT_MATRIX = EVIDENCE / "source_native_backreaction_upgrade_matrix.csv"
OUT_SUMMARY = EVIDENCE / "source_native_backreaction_upgrade_summary.csv"
OUT_REQUEST = DATA / "source_native_backreaction_author_request_packet.md"
OUT_DOC = DOCS / "source_native_backreaction_upgrade_matrix.md"

FAMILIES = [
    {
        "FamilyID": "QR_CRITERIA_1",
        "AddendumFigure": "QR_criteria1.pdf",
        "UpstreamInputs": "criteria set 1 H_D,H_D_prime plus reconstructed D,D_prime,D_double_prime",
        "Role": "selection_criteria_family",
    },
    {
        "FamilyID": "QR_CRITERIA_2",
        "AddendumFigure": "QR_criteria2.pdf",
        "UpstreamInputs": "criteria set 2 H_D,H_D_prime plus reconstructed D,D_prime,D_double_prime",
        "Role": "selection_criteria_family",
    },
    {
        "FamilyID": "QR_CRITERIA_3",
        "AddendumFigure": "QR_criteria3.pdf",
        "UpstreamInputs": "criteria set 3 H_D,H_D_prime plus reconstructed D,D_prime,D_double_prime",
        "Role": "selection_criteria_family",
    },
    {
        "FamilyID": "QR_DESI",
        "AddendumFigure": "QR_DESI.pdf",
        "UpstreamInputs": "DESI-dominated symbolic-regression family",
        "Role": "data_combination_family",
    },
    {
        "FamilyID": "QR_EBOSS",
        "AddendumFigure": "QR_eBOSS.pdf",
        "UpstreamInputs": "eBOSS/BOSS-dominated symbolic-regression family",
        "Role": "data_combination_family",
    },
]

REQUIRED_OBJECTS = [
    {
        "ObjectID": "RECONSTRUCTION_VECTOR_MEDIAN",
        "RequiredColumns": "z,D,D_prime,D_double_prime,H_D,H_D_prime",
        "WhyRequired": "computes Omega_R_plus_3Omega_Q with the published formula",
    },
    {
        "ObjectID": "RECONSTRUCTION_BOOTSTRAP_SAMPLES",
        "RequiredColumns": "sample_id,z,D,D_prime,D_double_prime,H_D,H_D_prime",
        "WhyRequired": "propagates non-Gaussian uncertainty and percentile bands without figure digitization",
    },
    {
        "ObjectID": "RECONSTRUCTION_COVARIANCE",
        "RequiredColumns": "row-wise covariance for D,D_prime,D_double_prime,H_D,H_D_prime",
        "WhyRequired": "allows covariance-aware K2/backreaction bridge scoring",
    },
    {
        "ObjectID": "SELECTION_METADATA",
        "RequiredColumns": "criteria_set,data_combination,algorithm,expression_id,selection_rule",
        "WhyRequired": "separates criteria-set sensitivity from data-combination sensitivity",
    },
    {
        "ObjectID": "GRID_AND_UNITS_METADATA",
        "RequiredColumns": "redshift_grid,D_definition,H_D_units,normalization",
        "WhyRequired": "prevents convention mismatch in the bridge to the locked K2 diagnostic vector",
    },
]


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    for family in FAMILIES:
        for obj in REQUIRED_OBJECTS:
            rows.append(
                {
                    "AuditID": "SOURCE_NATIVE_BACKREACTION_UPGRADE_MATRIX_V1",
                    "FamilyID": family["FamilyID"],
                    "FamilyRole": family["Role"],
                    "AddendumFigure": family["AddendumFigure"],
                    "UpstreamInputs": family["UpstreamInputs"],
                    "RequiredObjectID": obj["ObjectID"],
                    "RequiredColumns": obj["RequiredColumns"],
                    "WhyRequired": obj["WhyRequired"],
                    "AvailableInRepo": False,
                    "AvailableInArxivSourcePackage": False,
                    "FigureDigitizationAllowed": False,
                    "ProvisionalBAOOnlyFallbackAvailable": True,
                    "BlocksSourceNativeScoring": True,
                    "MeasurementValidationAllowed": False,
                    "NextAction": "obtain from authors or reproduce upstream symbolic-regression bootstrap pipeline",
                    "ClaimBoundary": "source_native_backreaction_upgrade_no_measurement_validation",
                }
            )

    matrix = pd.DataFrame(rows)
    matrix.to_csv(OUT_MATRIX, index=False)

    blocking = int(matrix["BlocksSourceNativeScoring"].sum())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_BACKREACTION_UPGRADE_MATRIX_V1",
                "FamiliesRequired": len(FAMILIES),
                "RequiredObjectsPerFamily": len(REQUIRED_OBJECTS),
                "TotalRequiredItems": len(matrix),
                "BlockingItems": blocking,
                "SourceNativeScoringReady": False,
                "ProvisionalBAOOnlyFallbackAvailable": True,
                "FigureDigitizationAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_BACKREACTION_BLOCKED_REQUIRED_OBJECTS_DECLARED",
                "StrongestAllowedClaim": (
                    "the source-native backreaction upgrade path is fully specified, "
                    "but the required reconstruction vectors, bootstrap samples, and covariance are not available in the repo or arXiv source packages"
                ),
                "PrimaryResidualRisk": "provisional BAO-only bridge may not match the published symbolic-regression reconstruction families",
                "NextAction": "request author tables or reproduce the cp3-bench/PySR bootstrap reconstruction route",
                "ClaimBoundary": "source_native_backreaction_upgrade_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    request_lines = [
        "# Source-Native Backreaction Data Request Packet",
        "",
        "Purpose: replace the provisional BAO-only backreaction bridge with the source-native reconstruction used for the published `Omega_R + 3 Omega_Q` constraints.",
        "",
        "Please provide, for each published backreaction family:",
        "",
    ]
    for family in FAMILIES:
        request_lines.extend(
            [
                f"## {family['FamilyID']}",
                "",
                f"- Addendum figure: `{family['AddendumFigure']}`",
                f"- Upstream input route: {family['UpstreamInputs']}",
                "",
                "Required machine-readable objects:",
            ]
        )
        for obj in REQUIRED_OBJECTS:
            request_lines.append(f"- `{obj['ObjectID']}`: {obj['RequiredColumns']}")
        request_lines.append("")
    request_lines.extend(
        [
            "Claim boundary: these files would be used for a source-native benchmark only. They would not by themselves imply measurement validation or discovery.",
            "",
        ]
    )
    OUT_REQUEST.write_text("\n".join(request_lines), encoding="utf-8")

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Backreaction Upgrade Matrix",
                "",
                "Status: source-native scoring blocked; required objects declared.",
                "",
                "The backreaction addendum computes `Omega_R + 3 Omega_Q` from reconstructed `D`, `H_D`, and derivatives. The arXiv source packages expose formula and figure routes, but not the machine-readable reconstruction vectors or covariance needed for source-native scoring.",
                "",
                "## Outputs",
                "",
                f"- Upgrade matrix: `{OUT_MATRIX.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                f"- Author/request packet: `{OUT_REQUEST.relative_to(ROOT)}`",
                "",
                "## Boundary",
                "",
                "No K2 parameter is changed. Figure digitization remains disabled for this source-native route. Measurement validation remains closed.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_MATRIX}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_REQUEST}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
