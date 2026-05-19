#!/usr/bin/env python3
"""Build a locked alpha-to-source-split transform contract and preview.

The transform is a preflight mapping contract for Dyer-Roeder optical
smoothness candidates. It is not a scorecard and it does not compare against
K2. The only allowed amplitude comes from the public source value
clumpiness = 1 - alpha; no residual fitting is performed.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

MANIFEST = EVIDENCE / "physical_null_provisional_extraction_manifest.csv"
READINESS = EVIDENCE / "physical_null_mapping_readiness.csv"
TEMPLATE = EVIDENCE / "physical_null_proxy_templates.csv"

POLICY_OUT = EVIDENCE / "physical_null_alpha_transform_policy.csv"
PREVIEW_OUT = EVIDENCE / "physical_null_alpha_response_preview.csv"
SUMMARY_OUT = EVIDENCE / "physical_null_alpha_transform_summary.csv"


def numeric(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    manifest = pd.read_csv(MANIFEST)
    readiness = pd.read_csv(READINESS)
    template = pd.read_csv(TEMPLATE)

    optical_template = template[template["TemplateID"].eq("DYER_ROEDER_OPTICAL_UNIT_NORM_V1")].copy()
    candidates = readiness[
        readiness["Status"].eq("MAPPING_PRECHECK_PARTIAL_READY")
        & readiness["Quantity"].eq("alpha_smoothness")
        & readiness["NullID"].eq("DYER_ROEDER_OPTICAL")
    ].copy()

    policy = pd.DataFrame(
        [
            {
                "PolicyID": "ALPHA_TO_SOURCE_SPLIT_OPTICAL_V1",
                "AppliesTo": "DYER_ROEDER_OPTICAL alpha_smoothness rows",
                "TransformFormula": "response_i = (1 - alpha) * DYER_ROEDER_OPTICAL_UNIT_NORM_V1_i",
                "UncertaintyPreviewFormula": "sigma_i = 0.5*(alpha_lower_error+alpha_upper_error)*abs(unit_shape_i)",
                "AmplitudeSource": "public alpha value from provisional extraction manifest",
                "AmplitudeFitToTargetAllowed": False,
                "K2ResidualInspectionAllowed": False,
                "CovarianceStatus": "diagonal_amplitude_preview_only",
                "CanSupportPreflightPreview": True,
                "CanSupportMeasurementScoring": False,
                "RequiredBeforeScoring": "source-native covariance or declared covariance propagation; sign convention audit; no post-hoc amplitude selection",
                "ClaimBoundary": "alpha_transform_contract_no_measurement_validation",
            }
        ]
    )
    policy.to_csv(POLICY_OUT, index=False)

    preview_rows: list[dict[str, object]] = []
    for _, candidate in candidates.iterrows():
        extraction_id = candidate["ExtractionID"]
        source = manifest[manifest["ExtractionID"].eq(extraction_id)].iloc[0]
        alpha = numeric(source["Value"])
        lower = numeric(source["LowerError"])
        upper = numeric(source["UpperError"])
        if alpha is None or lower is None or upper is None:
            continue
        amplitude = 1.0 - alpha
        amplitude_sigma = 0.5 * (lower + upper)
        for _, point in optical_template.iterrows():
            proxy = float(point["ProxyValue"])
            preview_rows.append(
                {
                    "PreviewID": "ALPHA_TO_SOURCE_SPLIT_OPTICAL_V1",
                    "ExtractionID": extraction_id,
                    "CandidateID": source["CandidateID"],
                    "ArxivID": source["ArxivID"],
                    "GridIndex": int(point["GridIndex"]),
                    "z_grid": float(point["z_grid"]),
                    "x_coordinate": float(point["x_coordinate"]),
                    "Alpha": alpha,
                    "AlphaLowerError": lower,
                    "AlphaUpperError": upper,
                    "ClumpinessAmplitude": amplitude,
                    "AmplitudeSigmaDiagPreview": amplitude_sigma,
                    "UnitShapeValue": proxy,
                    "ResponsePreview": amplitude * proxy,
                    "ResponseSigmaDiagPreview": abs(proxy) * amplitude_sigma,
                    "TransformPolicy": "response_i=(1-alpha)*unit_norm(centered[x^2])",
                    "ScoringAllowed": False,
                    "CovarianceStatus": "diagonal_amplitude_preview_only",
                    "BlockingIssue": "full_covariance_propagation_missing;sign_convention_audit_missing;measurement_scorecard_not_authorized",
                    "ClaimBoundary": "alpha_response_preview_no_measurement_validation",
                }
            )

    preview = pd.DataFrame(preview_rows)
    preview.to_csv(PREVIEW_OUT, index=False)

    summary = pd.DataFrame(
        [
            {
                "SummaryID": "PHYSICAL_NULL_ALPHA_TRANSFORM_SUMMARY",
                "PolicyRows": len(policy),
                "CandidateExtractionsPreviewed": int(preview["ExtractionID"].nunique()) if not preview.empty else 0,
                "PreviewRows": len(preview),
                "ScoringAllowedRows": int(preview["ScoringAllowed"].sum()) if not preview.empty else 0,
                "MeasurementValidationRows": 0,
                "FirstCandidateExtractionID": candidates.iloc[0]["ExtractionID"] if len(candidates) else "",
                "TransformFormula": "response_i=(1-alpha)*DYER_ROEDER_OPTICAL_UNIT_NORM_V1_i",
                "PrimaryBlockingIssue": "full_covariance_propagation_missing;sign_convention_audit_missing",
                "Interpretation": "alpha transform preview exists but remains non-scoring",
                "ClaimBoundary": "alpha_transform_contract_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    print(f"Wrote {POLICY_OUT}")
    print(f"Wrote {PREVIEW_OUT}")
    print(f"Wrote {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
