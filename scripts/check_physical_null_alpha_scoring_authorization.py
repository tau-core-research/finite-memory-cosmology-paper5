#!/usr/bin/env python3
"""Gate physical-null alpha controls before any scorecard use.

This guard consolidates the alpha transform, sign-convention, and covariance
preview artifacts. It is intentionally strict: previews do not authorize
measurement scoring, and no sign convention may be selected by score.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

TRANSFORM_SUMMARY = EVIDENCE / "physical_null_alpha_transform_summary.csv"
SIGN_SUMMARY = EVIDENCE / "physical_null_alpha_sign_convention_summary.csv"
COV_SUMMARY = EVIDENCE / "physical_null_alpha_covariance_preview_summary.csv"
MAPPING_SUMMARY = EVIDENCE / "physical_null_mapping_readiness_summary.csv"

OUT = EVIDENCE / "physical_null_alpha_scoring_authorization.csv"
OUT_SUMMARY = EVIDENCE / "physical_null_alpha_scoring_authorization_summary.csv"


def bool_from_count(value: object) -> bool:
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


def main() -> None:
    transform = pd.read_csv(TRANSFORM_SUMMARY).iloc[0]
    sign = pd.read_csv(SIGN_SUMMARY)
    cov = pd.read_csv(COV_SUMMARY)
    mapping = pd.read_csv(MAPPING_SUMMARY).iloc[0]

    extraction_ids = sorted(set(sign["ExtractionID"]).union(set(cov["ExtractionID"])))
    rows: list[dict[str, object]] = []

    for extraction_id in extraction_ids:
        sign_rows = sign[sign["ExtractionID"].eq(extraction_id)]
        cov_rows = cov[cov["ExtractionID"].eq(extraction_id)]

        transform_preview_exists = bool_from_count(transform["PreviewRows"])
        full_coverage_exists = int(mapping["RowsWithFullUsableCoverage"]) > 0
        sign_audited = not sign_rows.empty
        sign_frozen_external = False
        cov_preview_exists = not cov_rows.empty
        source_native_covariance_ready = False
        scoring_allowed_by_inputs = False

        blockers: list[str] = []
        if not transform_preview_exists:
            blockers.append("alpha_transform_preview_missing")
        if not full_coverage_exists:
            blockers.append("full_source_split_coverage_missing")
        if not sign_audited:
            blockers.append("sign_convention_audit_missing")
        if not sign_frozen_external:
            blockers.append("external_sign_convention_not_frozen")
        if not cov_preview_exists:
            blockers.append("covariance_preview_missing")
        if not source_native_covariance_ready:
            blockers.append("source_native_covariance_missing")
        if not scoring_allowed_by_inputs:
            blockers.append("measurement_scorecard_not_authorized")

        rows.append(
            {
                "AuthorizationID": "PHYSNULL_ALPHA_SCORING_AUTHORIZATION_V1",
                "ExtractionID": extraction_id,
                "TransformPreviewExists": transform_preview_exists,
                "FullSourceSplitCoverageExists": full_coverage_exists,
                "SignConventionAudited": sign_audited,
                "SignConventionFrozenExternally": sign_frozen_external,
                "CovariancePreviewExists": cov_preview_exists,
                "SourceNativeCovarianceReady": source_native_covariance_ready,
                "ScoringAllowedByInputs": scoring_allowed_by_inputs,
                "PhysicalNullScorecardAuthorized": False,
                "MeasurementValidationAuthorized": False,
                "BlockingIssue": ";".join(blockers),
                "NextAction": "freeze external optical sign convention and attach source-native covariance before scorecard",
                "Interpretation": "alpha branch has transform/covariance previews but remains closed for scoring",
                "ClaimBoundary": "alpha_scoring_authorization_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    summary = pd.DataFrame(
        [
            {
                "SummaryID": "PHYSNULL_ALPHA_SCORING_AUTHORIZATION_SUMMARY",
                "CandidatesChecked": len(output),
                "TransformPreviewCandidates": int(output["TransformPreviewExists"].sum()),
                "SignAuditedCandidates": int(output["SignConventionAudited"].sum()),
                "CovariancePreviewCandidates": int(output["CovariancePreviewExists"].sum()),
                "SourceNativeCovarianceReadyCandidates": int(output["SourceNativeCovarianceReady"].sum()),
                "ScorecardAuthorizedCandidates": int(output["PhysicalNullScorecardAuthorized"].sum()),
                "MeasurementValidationAuthorizedCandidates": int(output["MeasurementValidationAuthorized"].sum()),
                "PrimaryBlockingIssue": "external_sign_convention_not_frozen;source_native_covariance_missing;measurement_scorecard_not_authorized",
                "RecommendedNextAction": "write external sign-convention rationale or ingest source-native covariance; do not score yet",
                "Interpretation": "alpha branch is technically prepared for future scoring inputs, but the gate remains closed",
                "ClaimBoundary": "alpha_scoring_authorization_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
