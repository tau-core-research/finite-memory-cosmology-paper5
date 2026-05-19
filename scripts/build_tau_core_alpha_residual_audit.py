#!/usr/bin/env python3
"""Audit whether as-declared Dyer-Roeder alpha can absorb the A2 signal.

This does not tune alpha, flip the sign by score, or change K2. It only
summarizes existing alpha-as-declared and alpha-subtraction diagnostics.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ALPHA_DECLARED = EVIDENCE / "alpha_as_declared_preflight_summary.csv"
ALPHA_SUB = EVIDENCE / "alpha_subtracted_k2_residual_summary.csv"
ALPHA_AUTH = EVIDENCE / "physical_null_alpha_scoring_authorization_summary.csv"

OUT = EVIDENCE / "tau_core_alpha_residual_audit.csv"
SUMMARY = EVIDENCE / "tau_core_alpha_residual_summary.csv"
DOC = DOCS / "tau_core_alpha_residual_audit.md"


def main() -> None:
    declared = pd.read_csv(ALPHA_DECLARED)
    sub = pd.read_csv(ALPHA_SUB)
    auth = pd.read_csv(ALPHA_AUTH).iloc[0]

    rows: list[dict[str, object]] = []
    for _, row in declared.iterrows():
        extraction_id = row["ExtractionID"]
        sub_row = sub[sub["ExtractionID"].eq(extraction_id)].iloc[0]
        rms_ratio = float(row["PreviewToTargetRMSRatio"])
        cosine = float(row["CosineSimilarity"])
        after_delta_chi2 = float(sub_row["DeltaChi2VsK2AfterAlpha"])
        after_delta_cos = float(sub_row["DeltaCosineVsK2AfterAlpha"])
        stable_delta_cos = float(sub_row.get("StableDeltaCosineVsK2AfterAlpha", 0.0))

        rows.extend(
            [
                {
                    "CriterionID": "ALPHA_AS_DECLARED_SCALE",
                    "ExtractionID": extraction_id,
                    "Status": "PASS" if rms_ratio < 0.1 else "WARNING",
                    "Evidence": f"PreviewToTargetRMSRatio={rms_ratio}; PreviewRMS={row['PreviewRMS']}; TargetRMS={row['TargetRMS']}",
                    "Interpretation": "as-declared optical alpha preview is much smaller than the source-split target",
                    "ClaimImpact": "alpha cannot currently absorb the A2-scale memory-active residual",
                    "ClaimBoundary": "alpha_residual_audit_no_measurement_validation",
                },
                {
                    "CriterionID": "ALPHA_AS_DECLARED_SIGN",
                    "ExtractionID": extraction_id,
                    "Status": "WARNING",
                    "Evidence": f"SignMatchFraction={row['SignMatchFraction']}; SignStableMatchFraction={row['SignStableMatchFraction']}; CosineSimilarity={cosine}",
                    "Interpretation": "alpha sign agreement is partial and cannot be used as score-selected convention",
                    "ClaimImpact": "keeps optical null as weak partial control",
                    "ClaimBoundary": "alpha_residual_audit_no_measurement_validation",
                },
                {
                    "CriterionID": "ALPHA_SUBTRACTION_EFFECT",
                    "ExtractionID": extraction_id,
                    "Status": "PASS" if abs(after_delta_cos) < 0.05 and abs(after_delta_chi2) < 1.5 else "WARNING",
                    "Evidence": f"DeltaCosineVsK2AfterAlpha={after_delta_cos}; StableDeltaCosineVsK2AfterAlpha={stable_delta_cos}; DeltaChi2VsK2AfterAlpha={after_delta_chi2}",
                    "Interpretation": "subtracting alpha barely changes K2-relevant structure",
                    "ClaimImpact": "A2 residual is not removed by current as-declared optical-alpha preview",
                    "ClaimBoundary": "alpha_residual_audit_no_measurement_validation",
                },
                {
                    "CriterionID": "ALPHA_SCORECARD_AUTHORIZATION",
                    "ExtractionID": extraction_id,
                    "Status": "WARNING",
                    "Evidence": f"ScorecardAuthorizedCandidates={auth['ScorecardAuthorizedCandidates']}; PrimaryBlockingIssue={auth['PrimaryBlockingIssue']}",
                    "Interpretation": "alpha remains non-scoring until sign and covariance are externally frozen",
                    "ClaimImpact": "prevents measurement-level optical-null rejection claim",
                    "ClaimBoundary": "alpha_residual_audit_no_measurement_validation",
                },
            ]
        )

    audit = pd.DataFrame(rows)
    audit.to_csv(OUT, index=False)

    scale_pass = int(audit[audit["CriterionID"].eq("ALPHA_AS_DECLARED_SCALE")]["Status"].eq("PASS").sum())
    sub_pass = int(audit[audit["CriterionID"].eq("ALPHA_SUBTRACTION_EFFECT")]["Status"].eq("PASS").sum())
    candidate_count = int(declared["ExtractionID"].nunique())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "TAU_CORE_ALPHA_RESIDUAL_AUDIT",
                "CandidateExtractions": candidate_count,
                "Criteria": len(audit),
                "PassedCriteria": int(audit["Status"].eq("PASS").sum()),
                "WarningCriteria": int(audit["Status"].eq("WARNING").sum()),
                "SmallScaleAlphaCandidates": scale_pass,
                "AlphaSubtractionDoesNotRemoveK2Structure": sub_pass == candidate_count,
                "AlphaScorecardAuthorizedCandidates": int(auth["ScorecardAuthorizedCandidates"]),
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "AS_DECLARED_ALPHA_TOO_SMALL_TO_EXPLAIN_A2_PREFLIGHT_SIGNAL",
                "StrongestAllowedClaim": "current as-declared optical alpha preview does not absorb the locked A2 preflight residual",
                "PrimaryResidualRisk": "alpha sign convention and source-native covariance remain non-scoring",
                "NextAction": "ingest source-native optical covariance or freeze external sign rationale before calibrated physical-null scorecard",
                "ClaimBoundary": "alpha_residual_audit_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    DOC.write_text(
        "\n".join(
            [
                "# Tau Core Alpha Residual Audit",
                "",
                "Status: as-declared optical alpha does not absorb the A2 preflight residual; no measurement validation.",
                "",
                "The current Dyer-Roeder alpha preview is much smaller than the source-split target. Subtracting it barely changes the K2-relevant structure.",
                "",
                "This weakens the idea that the observed preflight A2 alignment is simply an optical-alpha proxy. It does not reject Dyer-Roeder physics, because the alpha branch still lacks a source-native covariance and externally frozen sign convention.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")
    print(f"Wrote {DOC}")


if __name__ == "__main__":
    main()
