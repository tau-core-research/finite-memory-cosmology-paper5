#!/usr/bin/env python3
"""Build the P-TauCov coordinate/source basis schema."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_coordinate_basis_schema.md"
OUT_CSV = EVIDENCE / "p_taucov_coordinate_basis_schema.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_coordinate_basis_schema_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
SCHEMA_ID = "P_TAUCOV_COORDINATE_BASIS_SCHEMA_v1"
CLAIM_BOUNDARY = "coordinate_basis_schema_declared_no_basis_values_no_packet"

ROWS = [
    {
        "Field": "coordinate_id",
        "Role": "stable row identifier for a coordinate/source basis element",
        "Required": True,
        "AllowedSource": "declared_coordinate_convention",
        "ForbiddenSource": "score_or_residual_derived_identifier",
    },
    {
        "Field": "coordinate_family",
        "Role": "predeclared family/group label for symmetry and blocked audits",
        "Required": True,
        "AllowedSource": "source_metadata_or_theory_declared_grouping",
        "ForbiddenSource": "post_scoring_family_gain_cluster",
    },
    {
        "Field": "coordinate_kind",
        "Role": "basis-kind tag such as parent, branch, morphology, clock, environment, or projection",
        "Required": True,
        "AllowedSource": "Tau_side_definition_or_source_metadata",
        "ForbiddenSource": "held_out_residual_pattern",
    },
    {
        "Field": "basis_axis",
        "Role": "axis name used to build matrices and exclusion subspaces",
        "Required": True,
        "AllowedSource": "frozen_coordinate_system",
        "ForbiddenSource": "P5C_v3_gain_direction",
    },
    {
        "Field": "origin_value",
        "Role": "target-blind reference value used for Phi_0 origin or center selection",
        "Required": True,
        "AllowedSource": "physical_zero_or_predeclared_coordinate_center",
        "ForbiddenSource": "OOS_DeltaNLL_optimized_center",
    },
    {
        "Field": "scale_value",
        "Role": "normalization scale for coordinate comparability",
        "Required": True,
        "AllowedSource": "physical_unit_or_training_blind_source_distribution",
        "ForbiddenSource": "target_residual_normalization",
    },
    {
        "Field": "is_null_candidate",
        "Role": "predeclared flag for possible exact zero-mode audit",
        "Required": True,
        "AllowedSource": "operator_or_symmetry_declaration",
        "ForbiddenSource": "metric_failure_or_success_pattern",
    },
    {
        "Field": "is_gauge_candidate",
        "Role": "predeclared flag for coordinate redundancy audit",
        "Required": True,
        "AllowedSource": "basis_symmetry_certificate",
        "ForbiddenSource": "post_hoc_covariance_alignment",
    },
    {
        "Field": "is_forbidden_candidate",
        "Role": "predeclared flag for outcome-derived or target-leaking field exclusion",
        "Required": True,
        "AllowedSource": "input_provenance_leakage_audit",
        "ForbiddenSource": "after_the_fact_manual_exclusion",
    },
    {
        "Field": "provenance",
        "Role": "human-readable source and freeze note",
        "Required": True,
        "AllowedSource": "file_hash_or_citable_source_or_theory_note",
        "ForbiddenSource": "undocumented_manual_edit",
    },
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SchemaID": SCHEMA_ID,
                **row,
                "ConcreteBasisSupplied": False,
                "ReferenceDomainSelectable": False,
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in ROWS
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SchemaID": SCHEMA_ID,
                "RequiredFields": len(df[df["Required"]]),
                "SchemaDeclared": True,
                "ConcreteBasisSupplied": False,
                "ReferenceDomainSelectable": False,
                "ReducedDomainFrozen": False,
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "ExpectedPacketPath": "data/p_taucov/linear/coordinate_basis.csv",
                "ExpectedManifestPath": "evidence/p_taucov_coordinate_basis_manifest.yaml",
                "ExpectedHashPath": "evidence/p_taucov_coordinate_basis.sha256",
                "NextStep": "supply_coordinate_basis_csv_manifest_hash_and_leakage_audit",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Coordinate/Source Basis Schema

Status: schema only / no concrete coordinate basis / no `Phi_0` / no reduced
domain / no linear packet / no metric evaluation / no scoring authorization.

The reference-domain selection rule requires a frozen coordinate/source basis.
This schema declares the fields that such a basis must contain before `Phi_0`,
`P_null`, `P_gauge`, `P_forbidden`, and `P_red` can be built.

## Required Basis Fields

| Field | Role | Forbidden source |
| --- | --- | --- |
| `coordinate_id` | Stable row identifier for a coordinate/source basis element. | score- or residual-derived identifier |
| `coordinate_family` | Predeclared family/group label for symmetry and blocked audits. | post-scoring family-gain cluster |
| `coordinate_kind` | Basis-kind tag such as parent, branch, morphology, clock, environment, or projection. | held-out residual pattern |
| `basis_axis` | Axis name used to build matrices and exclusion subspaces. | P5C v3 gain direction |
| `origin_value` | Target-blind reference value used for `Phi_0` origin or center selection. | OOS DeltaNLL optimized center |
| `scale_value` | Normalization scale for coordinate comparability. | target-residual normalization |
| `is_null_candidate` | Predeclared flag for possible exact zero-mode audit. | metric failure/success pattern |
| `is_gauge_candidate` | Predeclared flag for coordinate redundancy audit. | post-hoc covariance alignment |
| `is_forbidden_candidate` | Predeclared flag for outcome-derived or target-leaking field exclusion. | after-the-fact manual exclusion |
| `provenance` | Human-readable source and freeze note. | undocumented manual edit |

## Expected Packet Files

```text
data/p_taucov/linear/coordinate_basis.csv
evidence/p_taucov_coordinate_basis_manifest.yaml
evidence/p_taucov_coordinate_basis.sha256
evidence/p_taucov_coordinate_basis_leakage_audit.csv
```

## Minimum Freeze Conditions

The concrete coordinate-basis packet may be accepted only if:

```text
all required fields are present;
all coordinate_id values are unique;
origin_value and scale_value are finite;
scale_value is nonzero;
provenance is nonempty for every row;
no forbidden target, score, residual, or post-scoring source is used;
the leakage audit declares no outcome-derived basis columns;
the manifest and hash match the frozen packet.
```

## Claim Boundary

Allowed statement:

```text
The coordinate/source basis schema is declared.
```

Forbidden statement:

```text
A concrete P-TauCov coordinate basis or reference domain is frozen.
```
""",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DOC}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
