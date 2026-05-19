#!/usr/bin/env python3
"""Export external physical-null calibration source candidates.

This step separates source acquisition from scoring. It promotes extracted
public values into machine-readable source files only when they are sourced from
papers, not from the K2 scorecard. Measurement validation remains closed.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data" / "physical_nulls"

MANIFEST = EVIDENCE / "physical_null_provisional_extraction_manifest.csv"

OUT_DYER = DATA / "dyer_roeder_optical_calibration_source.csv"
OUT_BACK = DATA / "backreaction_calibration_source.csv"
OUT_SUMMARY = EVIDENCE / "external_physical_null_calibration_source_summary.csv"
OUT_DOC = ROOT / "docs" / "external_physical_null_calibration_sources.md"


def main() -> None:
    manifest = pd.read_csv(MANIFEST)
    DATA.mkdir(parents=True, exist_ok=True)

    dyer = manifest[
        manifest["NullID"].eq("DYER_ROEDER_OPTICAL")
        & manifest["Quantity"].eq("alpha_smoothness")
        & manifest["Value"].ne("not_extracted")
    ].copy()
    dyer["Alpha"] = dyer["Value"].astype(float)
    dyer["AlphaLowerError"] = dyer["LowerError"].astype(float)
    dyer["AlphaUpperError"] = dyer["UpperError"].astype(float)
    dyer["ClumpinessAmplitude"] = 1.0 - dyer["Alpha"]
    dyer["AmplitudeSigmaMeanHalfWidth"] = 0.5 * (dyer["AlphaLowerError"] + dyer["AlphaUpperError"])
    dyer["AmplitudeSourceType"] = "published_alpha_constraint"
    dyer["AmplitudeFitToTargetAllowed"] = False
    dyer["AllowedForPreflightCalibration"] = True
    dyer["AllowedForMeasurementCalibration"] = False
    dyer["BlockingIssue"] = "source_native_joint_covariance_missing;mapping_remains_preflight"
    dyer["ClaimBoundary"] = "external_physical_null_calibration_source_no_measurement_validation"
    dyer[
        [
            "ExtractionID",
            "CandidateID",
            "ArxivID",
            "NullID",
            "Quantity",
            "Alpha",
            "AlphaLowerError",
            "AlphaUpperError",
            "ClumpinessAmplitude",
            "AmplitudeSigmaMeanHalfWidth",
            "ConfidenceLevel",
            "RedshiftRange",
            "SourceLocation",
            "AmplitudeSourceType",
            "AmplitudeFitToTargetAllowed",
            "AllowedForPreflightCalibration",
            "AllowedForMeasurementCalibration",
            "BlockingIssue",
            "ClaimBoundary",
        ]
    ].to_csv(OUT_DYER, index=False)

    back = manifest[manifest["NullID"].eq("BACKREACTION_ONLY")].copy()
    back["AllowedForPreflightCalibration"] = False
    back["AllowedForMeasurementCalibration"] = False
    back["BlockingIssue"] = "numeric_backreaction_constraint_not_extracted"
    back["ClaimBoundary"] = "external_backreaction_calibration_source_not_ready"
    back[
        [
            "ExtractionID",
            "CandidateID",
            "ArxivID",
            "NullID",
            "Quantity",
            "Value",
            "SourceLocation",
            "ExtractionRoute",
            "AllowedForPreflightCalibration",
            "AllowedForMeasurementCalibration",
            "BlockingIssue",
            "ClaimBoundary",
        ]
    ].to_csv(OUT_BACK, index=False)

    summary = pd.DataFrame(
        [
            {
                "SummaryID": "EXTERNAL_PHYSICAL_NULL_CALIBRATION_SOURCE_SUMMARY",
                "DyerRoederSources": len(dyer),
                "DyerRoederPreflightCalibrationSourcesAllowed": int(dyer["AllowedForPreflightCalibration"].sum()),
                "BackreactionSources": len(back),
                "BackreactionPreflightCalibrationSourcesAllowed": int(back["AllowedForPreflightCalibration"].sum()),
                "MeasurementCalibrationSourcesAllowed": 0,
                "BestCurrentSourceClass": "published_dyer_roeder_alpha_constraints",
                "BackreactionStatus": "route_identified_but_numeric_constraint_not_extracted",
                "StrongestAllowedClaim": (
                    "published Dyer-Roeder alpha constraints can support a preflight optical-null amplitude check; "
                    "backreaction remains source-route only"
                ),
                "PrimaryResidualRisk": "alpha constraints are not source-native to the current SN-BAO branch contrast and lack full joint covariance",
                "NextAction": "run as-declared alpha calibrated preflight on whitened routes; keep measurement validation closed",
                "ClaimBoundary": "external_physical_null_calibration_source_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DOC.write_text(
        "\n".join(
            [
                "# External Physical-Null Calibration Sources",
                "",
                "Status: source export for preflight calibration; no measurement-validation claim.",
                "",
                "The Dyer-Roeder optical branch has published alpha constraints available as machine-readable source rows. The backreaction branch has a source route but no extracted numeric calibration table yet.",
                "",
                "## Outputs",
                "",
                f"- Dyer-Roeder source: `{OUT_DYER.relative_to(ROOT)}`",
                f"- Backreaction source: `{OUT_BACK.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DYER}")
    print(f"Wrote {OUT_BACK}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
