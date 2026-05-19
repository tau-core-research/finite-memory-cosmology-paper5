#!/usr/bin/env python3
"""Adjudicate public target-vector conventions without using A2 score.

The decision matrix separates physical/statistical admissibility from
K2/A2 performance. It does not promote a new measurement target.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

BRANCH = EVIDENCE / "public_rerun_branch_contribution_summary.csv"
TARGET = EVIDENCE / "public_rerun_target_construction_summary.csv"
VARIANTS = EVIDENCE / "public_rerun_target_variant_summary.csv"

OUT = EVIDENCE / "public_target_convention_adjudication.csv"
SUMMARY = EVIDENCE / "public_target_convention_adjudication_summary.csv"
DOC = DOCS / "public_target_convention_adjudication.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty evidence file: {path}")
    return df.iloc[0]


def main() -> None:
    branch = first(BRANCH)
    target = first(TARGET)
    variants = first(VARIANTS)

    rows = [
        {
            "ConventionID": "RAW_PROJECTED_SN_MINUS_BAO_CURRENT",
            "ConventionClass": "raw_likelihood_projection_candidate",
            "Definition": "y = L_SN*r_SN_raw - L_BAO*r_BAO_log",
            "UsesPublicCovarianceInputs": True,
            "CommonBranchUnits": False,
            "PreservesCoordinateNativeSign": False,
            "ScoreIndependentJustification": "closest to current public residual projection, but branch units differ and sign/scale is convention-sensitive",
            "KnownIssue": (
                f"projected/standardized sign mismatch rows={branch['ProjectedVsStandardizedSignMismatchRows']}; "
                f"compressed rows={branch['RawProjectedTargetCompressedRows']}"
            ),
            "PromotionStatus": "DO_NOT_PROMOTE_TO_MEASUREMENT_TARGET",
            "AllowedUse": "rerun_candidate_diagnostic_only",
            "RequiredNextCheck": "derive branch-unit normalization or replace with whitening target before interpretation",
        },
        {
            "ConventionID": "STANDARDIZED_SN_MINUS_BAO_COORDINATE_TARGET",
            "ConventionClass": "standardized_branch_contrast",
            "Definition": "y = SN_standardized - BAO_standardized on the frozen coordinate-native grid",
            "UsesPublicCovarianceInputs": True,
            "CommonBranchUnits": True,
            "PreservesCoordinateNativeSign": True,
            "ScoreIndependentJustification": "puts SN and BAO branches on common dimensionless units and matches the source-split sign-family convention",
            "KnownIssue": "not a full covariance-whitened likelihood target; remains preflight unless covariance-native transform is built",
            "PromotionStatus": "PREFERRED_PREFLIGHT_CONVENTION_NOT_MEASUREMENT_TARGET",
            "AllowedUse": "preflight_target_convention",
            "RequiredNextCheck": "construct covariance-native whitening transform using the same branch convention",
        },
        {
            "ConventionID": "RAW_PROJECTED_SIGN_ALIGNED_TO_STANDARDIZED",
            "ConventionClass": "sign_alignment_counterfactual",
            "Definition": "y = sign(y_standardized) * abs(L_SN*r_SN_raw - L_BAO*r_BAO_log)",
            "UsesPublicCovarianceInputs": True,
            "CommonBranchUnits": False,
            "PreservesCoordinateNativeSign": True,
            "ScoreIndependentJustification": "diagnoses sign-convention sensitivity only; sign is imposed from another target",
            "KnownIssue": "uses target sign alignment and is therefore not admissible as a primary measurement convention",
            "PromotionStatus": "FORBIDDEN_AS_PRIMARY_TARGET",
            "AllowedUse": "counterfactual_diagnostic_only",
            "RequiredNextCheck": "none for promotion; retain only as sensitivity check",
        },
        {
            "ConventionID": "WHITENED_STANDARDIZED_BRANCH_CONTRAST_V1",
            "ConventionClass": "future_covariance_native_target",
            "Definition": "y = W_cov * [SN_standardized - BAO_standardized] with W_cov declared before scoring",
            "UsesPublicCovarianceInputs": True,
            "CommonBranchUnits": True,
            "PreservesCoordinateNativeSign": True,
            "ScoreIndependentJustification": "retains common branch units while allowing public covariance to define the metric scale",
            "KnownIssue": "not implemented yet; whitening matrix and cross-covariance policy must be declared before scoring",
            "PromotionStatus": "RECOMMENDED_NEXT_MEASUREMENT_CANDIDATE",
            "AllowedUse": "implementation_target_for_next_locked_rerun",
            "RequiredNextCheck": "build whitening transform and rerun K1/A2/nulls unchanged",
        },
        {
            "ConventionID": "STANDARDIZED_SN_PLUS_BAO_SIGN_FLIP_CHECK",
            "ConventionClass": "sign_flip_counterfactual",
            "Definition": "y = SN_standardized + BAO_standardized",
            "UsesPublicCovarianceInputs": True,
            "CommonBranchUnits": True,
            "PreservesCoordinateNativeSign": False,
            "ScoreIndependentJustification": "tests opposite source-split orientation only",
            "KnownIssue": "does not match the declared source-split contrast orientation",
            "PromotionStatus": "FORBIDDEN_AS_PRIMARY_TARGET",
            "AllowedUse": "counterfactual_diagnostic_only",
            "RequiredNextCheck": "none for promotion; retain only as sign-orientation control",
        },
    ]
    detail = pd.DataFrame(rows)
    detail["SelectionUsesK2Score"] = False
    detail["MeasurementValidationAllowed"] = False
    detail["ClaimBoundary"] = "public_target_convention_adjudication_no_measurement_validation"
    detail.to_csv(OUT, index=False)

    promoted = detail[detail["PromotionStatus"].eq("RECOMMENDED_NEXT_MEASUREMENT_CANDIDATE")]
    preferred = detail[detail["PromotionStatus"].eq("PREFERRED_PREFLIGHT_CONVENTION_NOT_MEASUREMENT_TARGET")]
    forbidden = detail[detail["PromotionStatus"].str.contains("FORBIDDEN", na=False)]
    summary = pd.DataFrame(
        [
            {
                "AdjudicationID": "PUBLIC_TARGET_CONVENTION_ADJUDICATION_V1",
                "Conventions": len(detail),
                "SelectionUsesK2Score": False,
                "CurrentRawProjectedTargetPromoted": False,
                "PreferredPreflightConvention": preferred.iloc[0]["ConventionID"],
                "RecommendedNextMeasurementCandidate": promoted.iloc[0]["ConventionID"],
                "ForbiddenPrimaryTargets": ";".join(forbidden["ConventionID"]),
                "CurrentTargetSignMismatchRows": target["CandidateCoordinateSignMismatchRows"],
                "CurrentTargetCompressedRows": target["CandidateScaleCompressedRows"],
                "VariantSensitivityCounterfactualsK2OverK1": variants["CounterfactualVariantsK2OverK1"],
                "VariantSensitivityCounterfactuals": variants["CounterfactualVariants"],
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "TARGET_CONVENTION_ADJUDICATED_MEASUREMENT_STILL_BLOCKED",
                "StrongestAllowedClaim": "the current public rerun tension is target-convention sensitive and requires a declared whitening/standardized target before interpretation",
                "NextAction": "implement WHITENED_STANDARDIZED_BRANCH_CONTRAST_V1, then rerun locked A2, K1, and nulls unchanged",
                "ClaimBoundary": "public_target_convention_adjudication_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Public Target Convention Adjudication",
        "",
        "Status: target convention adjudicated without using A2 score. Measurement validation remains closed.",
        "",
        "## Decision",
        "",
        f"- Preferred preflight convention: `{preferred.iloc[0]['ConventionID']}`",
        f"- Recommended next measurement candidate: `{promoted.iloc[0]['ConventionID']}`",
        "- Current raw projected target: diagnostic only, not promoted.",
        "- Locked A2 changes allowed: False.",
        "",
        "## Conventions",
        "",
    ]
    for _, row in detail.iterrows():
        lines.extend(
            [
                f"### {row['ConventionID']}",
                "",
                f"- Class: {row['ConventionClass']}",
                f"- Definition: {row['Definition']}",
                f"- Promotion status: {row['PromotionStatus']}",
                f"- Allowed use: {row['AllowedUse']}",
                f"- Score-independent justification: {row['ScoreIndependentJustification']}",
                f"- Known issue: {row['KnownIssue']}",
                f"- Required next check: {row['RequiredNextCheck']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "This adjudication does not choose the target that makes A2 look best. It selects the next route by branch-unit consistency and covariance-native measurability.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")
    print(f"Wrote {DOC}")


if __name__ == "__main__":
    main()
