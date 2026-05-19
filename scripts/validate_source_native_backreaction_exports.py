#!/usr/bin/env python3
"""Validate source-native backreaction exports when they become available."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.source_native_backreaction import (
    build_backreaction_vector,
    load_csv_if_exists,
    validate_reconstruction_vector,
    validate_selection_metadata,
)

DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

RECON_EXPORT = DATA / "source_native_reconstruction_vector.csv"
META_EXPORT = DATA / "source_native_selection_metadata.csv"
OMEGA_EXPORT = DATA / "source_native_backreaction_vector.csv"

OUT_AUDIT = EVIDENCE / "source_native_backreaction_export_validation.csv"
OUT_SUMMARY = EVIDENCE / "source_native_backreaction_export_validation_summary.csv"
OUT_DOC = DOCS / "source_native_backreaction_export_validation.md"


def status_from_issues(exists: bool, issues: list[str]) -> str:
    if not exists:
        return "MISSING"
    if issues:
        return "INVALID"
    return "VALID"


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    recon = load_csv_if_exists(RECON_EXPORT)
    meta = load_csv_if_exists(META_EXPORT)

    recon_issues = ["source_native_reconstruction_vector_missing"] if recon is None else validate_reconstruction_vector(recon)
    meta_issues = ["source_native_selection_metadata_missing"] if meta is None else validate_selection_metadata(meta)

    omega_written = False
    omega_rows = 0
    if recon is not None and not recon_issues:
        omega = build_backreaction_vector(recon)
        omega.to_csv(OMEGA_EXPORT, index=False)
        omega_written = True
        omega_rows = len(omega)

    audit = pd.DataFrame(
        [
            {
                "ObjectID": "SOURCE_NATIVE_RECONSTRUCTION_VECTOR",
                "Path": str(RECON_EXPORT.relative_to(ROOT)),
                "Exists": recon is not None,
                "Status": status_from_issues(recon is not None, recon_issues),
                "Issues": ";".join(recon_issues),
                "Rows": 0 if recon is None else len(recon),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "source_native_backreaction_export_validation_no_measurement_validation",
            },
            {
                "ObjectID": "SOURCE_NATIVE_SELECTION_METADATA",
                "Path": str(META_EXPORT.relative_to(ROOT)),
                "Exists": meta is not None,
                "Status": status_from_issues(meta is not None, meta_issues),
                "Issues": ";".join(meta_issues),
                "Rows": 0 if meta is None else len(meta),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "source_native_backreaction_export_validation_no_measurement_validation",
            },
        ]
    )
    audit.to_csv(OUT_AUDIT, index=False)

    ready = bool(recon is not None and meta is not None and not recon_issues and not meta_issues)
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_BACKREACTION_EXPORT_VALIDATION_V1",
                "ReconstructionVectorValid": bool(recon is not None and not recon_issues),
                "SelectionMetadataValid": bool(meta is not None and not meta_issues),
                "BackreactionVectorWritten": omega_written,
                "BackreactionVectorRows": omega_rows,
                "SourceNativeBackreactionExportsReady": ready,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_EXPORTS_READY" if ready else "SOURCE_NATIVE_EXPORTS_MISSING_OR_INVALID",
                "StrongestAllowedClaim": (
                    "source-native exports are valid for preflight bridge scoring"
                    if ready
                    else "source-native export validation gate is ready, but required exports are missing or invalid"
                ),
                "PrimaryResidualRisk": (
                    "source-native covariance or bootstrap export is still required for measurement-grade scoring"
                    if ready
                    else "missing source-native reconstruction vector and/or selection metadata"
                ),
                "NextAction": (
                    "run source-native bridge scorecard"
                    if ready
                    else "provide data/physical_nulls/backreaction_reproduction/source_native_reconstruction_vector.csv and source_native_selection_metadata.csv"
                ),
                "ClaimBoundary": "source_native_backreaction_export_validation_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Backreaction Export Validation",
                "",
                "Status: validation gate ready.",
                "",
                "This script validates future source-native reconstruction exports and computes the fixed-formula `Omega_R + 3 Omega_Q` vector when possible. It does not alter locked K2 or authorize measurement validation.",
                "",
                "## Outputs",
                "",
                f"- Audit: `{OUT_AUDIT.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                f"- Backreaction vector, if valid: `{OMEGA_EXPORT.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")
    if omega_written:
        print(f"Wrote {OMEGA_EXPORT}")


if __name__ == "__main__":
    main()
