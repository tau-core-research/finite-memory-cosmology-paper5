#!/usr/bin/env python3
"""Audit sign conventions for the alpha-response preview.

This is not a K2 scorecard. It compares the non-scoring optical alpha preview
against the current source-split response orientation under two explicit sign
conventions:

- as_declared: response_i = (1-alpha) * optical_shape_i
- inverted:    response_i = -(1-alpha) * optical_shape_i

No convention is promoted by this script. The output records whether a future
scoring run must freeze a sign convention before physical-null comparison.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

PREVIEW = EVIDENCE / "physical_null_alpha_response_preview.csv"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"

OUT = EVIDENCE / "physical_null_alpha_sign_convention_audit.csv"
OUT_SUMMARY = EVIDENCE / "physical_null_alpha_sign_convention_summary.csv"


def sign(value: float) -> int:
    if not math.isfinite(value) or abs(value) < 1e-12:
        return 0
    return 1 if value > 0 else -1


def main() -> None:
    preview = pd.read_csv(PREVIEW)
    target = pd.read_csv(TARGET)
    merged = preview.merge(
        target[
            [
                "GridIndex",
                "SourceSplitResponse",
                "HasSNAndBAO",
                "SignStableTemplate",
                "SNBAOSameSign",
                "ResponseDefinition",
            ]
        ],
        on="GridIndex",
        how="left",
    )
    usable = merged[merged["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"])].copy()

    rows: list[dict[str, object]] = []
    for _, row in usable.iterrows():
        for convention, factor in [
            ("AS_DECLARED_ALPHA_CLUMPINESS_SIGN", 1.0),
            ("INVERTED_ALPHA_CLUMPINESS_SIGN", -1.0),
        ]:
            response = float(row["ResponsePreview"]) * factor
            source_response = float(row["SourceSplitResponse"])
            preview_sign = sign(response)
            target_sign = sign(source_response)
            rows.append(
                {
                    "AuditID": "ALPHA_SIGN_CONVENTION_AUDIT_V1",
                    "ExtractionID": row["ExtractionID"],
                    "ConventionID": convention,
                    "GridIndex": int(row["GridIndex"]),
                    "z_grid": float(row["z_grid"]),
                    "ResponseDefinition": row["ResponseDefinition"],
                    "Alpha": float(row["Alpha"]),
                    "PreviewResponse": response,
                    "SourceSplitResponse": source_response,
                    "PreviewSign": preview_sign,
                    "TargetSign": target_sign,
                    "SignMatchesTarget": preview_sign == target_sign if preview_sign and target_sign else False,
                    "SignStableTemplate": bool(row["SignStableTemplate"]),
                    "SNBAOSameSign": bool(row["SNBAOSameSign"]),
                    "ScoringAllowed": False,
                    "Status": "SIGN_CONVENTION_AUDIT_ONLY",
                    "BlockingIssue": "sign_convention_not_frozen;covariance_propagation_missing;measurement_scorecard_not_authorized",
                    "ClaimBoundary": "alpha_sign_convention_audit_no_measurement_validation",
                }
            )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    summary_rows: list[dict[str, object]] = []
    for (extraction_id, convention), group in output.groupby(["ExtractionID", "ConventionID"]):
        stable = group[group["SignStableTemplate"]]
        summary_rows.append(
            {
                "SummaryID": "ALPHA_SIGN_CONVENTION_AUDIT_SUMMARY",
                "ExtractionID": extraction_id,
                "ConventionID": convention,
                "Rows": len(group),
                "SignMatches": int(group["SignMatchesTarget"].sum()),
                "SignMatchFraction": float(group["SignMatchesTarget"].mean()) if len(group) else 0.0,
                "SignStableRows": len(stable),
                "SignStableMatches": int(stable["SignMatchesTarget"].sum()),
                "SignStableMatchFraction": float(stable["SignMatchesTarget"].mean()) if len(stable) else 0.0,
                "ScoringAllowed": False,
                "RecommendedAction": "freeze physical sign convention from external optical-response reasoning before scorecard use",
                "PrimaryBlockingIssue": "sign_convention_not_frozen;covariance_propagation_missing",
                "Interpretation": "sign agreement is diagnostic metadata only, not model selection",
                "ClaimBoundary": "alpha_sign_convention_audit_no_measurement_validation",
            }
        )

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
