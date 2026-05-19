#!/usr/bin/env python3
"""Create source-native backreaction export templates."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.source_native_backreaction import (
    SOURCE_NATIVE_FAMILY_IDS,
    empty_bootstrap_sample_template,
    empty_omega_covariance_template,
    empty_reconstruction_vector_template,
    empty_selection_metadata_template,
)

DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT_RECON_TEMPLATE = DATA / "source_native_reconstruction_vector_template.csv"
OUT_META_TEMPLATE = DATA / "source_native_selection_metadata_template.csv"
OUT_BOOTSTRAP_TEMPLATE = DATA / "source_native_backreaction_bootstrap_samples_template.csv"
OUT_COV_TEMPLATE = DATA / "source_native_backreaction_covariance_template.csv"
OUT_SCHEMA = EVIDENCE / "source_native_backreaction_export_schema.csv"
OUT_SUMMARY = EVIDENCE / "source_native_backreaction_template_summary.csv"
OUT_DOC = DOCS / "source_native_backreaction_export_templates.md"


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    empty_reconstruction_vector_template().to_csv(OUT_RECON_TEMPLATE, index=False)
    empty_selection_metadata_template().to_csv(OUT_META_TEMPLATE, index=False)
    empty_bootstrap_sample_template().to_csv(OUT_BOOTSTRAP_TEMPLATE, index=False)
    empty_omega_covariance_template().to_csv(OUT_COV_TEMPLATE, index=False)

    schema_rows = []
    for path, object_id, role in [
        (OUT_RECON_TEMPLATE, "SOURCE_NATIVE_RECONSTRUCTION_VECTOR", "source-native D/H_D derivative export"),
        (OUT_META_TEMPLATE, "SOURCE_NATIVE_SELECTION_METADATA", "family selection metadata"),
        (OUT_BOOTSTRAP_TEMPLATE, "SOURCE_NATIVE_BACKREACTION_BOOTSTRAP_SAMPLES", "source-native omega bootstrap samples"),
        (OUT_COV_TEMPLATE, "SOURCE_NATIVE_BACKREACTION_COVARIANCE", "source-native omega covariance"),
    ]:
        columns = pd.read_csv(path).columns
        for col in columns:
            schema_rows.append(
                {
                    "ObjectID": object_id,
                    "Column": col,
                    "Required": True,
                    "Role": role,
                    "ClaimBoundary": "source_native_backreaction_templates_no_measurement_validation",
                }
            )
    pd.DataFrame(schema_rows).to_csv(OUT_SCHEMA, index=False)

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_BACKREACTION_TEMPLATES_V1",
                "FamiliesDeclared": len(SOURCE_NATIVE_FAMILY_IDS),
                "FamilyIDs": ";".join(SOURCE_NATIVE_FAMILY_IDS),
                "ReconstructionTemplateCreated": OUT_RECON_TEMPLATE.exists(),
                "SelectionMetadataTemplateCreated": OUT_META_TEMPLATE.exists(),
                "BootstrapTemplateCreated": OUT_BOOTSTRAP_TEMPLATE.exists(),
                "CovarianceTemplateCreated": OUT_COV_TEMPLATE.exists(),
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_EXPORT_TEMPLATES_READY",
                "StrongestAllowedClaim": "source-native export schemas are ready for author exports or reproduced symbolic-regression outputs",
                "PrimaryResidualRisk": "templates do not supply the missing reconstruction family data",
                "NextAction": "validate real exports with scripts/validate_source_native_backreaction_exports.py",
                "ClaimBoundary": "source_native_backreaction_templates_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Backreaction Export Templates",
                "",
                "Status: templates ready; source-native data still missing.",
                "",
                "These templates define the CSV shape expected from either author-provided exports or a reproduced symbolic-regression pipeline.",
                "",
                "## Outputs",
                "",
                f"- Reconstruction vector template: `{OUT_RECON_TEMPLATE.relative_to(ROOT)}`",
                f"- Selection metadata template: `{OUT_META_TEMPLATE.relative_to(ROOT)}`",
                f"- Bootstrap samples template: `{OUT_BOOTSTRAP_TEMPLATE.relative_to(ROOT)}`",
                f"- Covariance template: `{OUT_COV_TEMPLATE.relative_to(ROOT)}`",
                f"- Schema: `{OUT_SCHEMA.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_RECON_TEMPLATE}")
    print(f"Wrote {OUT_META_TEMPLATE}")
    print(f"Wrote {OUT_BOOTSTRAP_TEMPLATE}")
    print(f"Wrote {OUT_COV_TEMPLATE}")
    print(f"Wrote {OUT_SCHEMA}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
