#!/usr/bin/env python3
"""Register decision rules for future source-native backreaction exports.

The rules translate a future source-native bridge scorecard into predeclared
support/weakening categories. They prevent post-hoc reinterpretation and keep
measurement validation closed until source-native covariance exists.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

RANK = EVIDENCE / "source_native_surrogate_family_rank_summary.csv"
SHAPE = EVIDENCE / "source_native_surrogate_bridge_shape_summary.csv"
SURR_BRIDGE = EVIDENCE / "source_native_surrogate_bridge_summary.csv"

OUT_RULES = EVIDENCE / "source_native_backreaction_decision_rules.csv"
OUT_SUMMARY = EVIDENCE / "source_native_backreaction_decision_rules_summary.csv"
OUT_DOC = DOCS / "source_native_backreaction_decision_rules.md"

CLAIM_BOUNDARY = "source_native_backreaction_decision_rules_no_measurement_validation"


def read_first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty evidence file: {path}")
    return df.iloc[0]


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    rank = read_first(RANK)
    shape = read_first(SHAPE)
    bridge = read_first(SURR_BRIDGE)

    top_family = str(rank["TopFamilyID"])
    top_corr = float(rank["TopFamilyMeanCorrelationWithK2"])
    median_corr_k2 = float(shape["MedianCorrelationSurrogateWithK2"])
    median_corr_target = float(shape["MedianCorrelationSurrogateWithTarget"])

    rules = [
        {
            "RuleID": "SNBR_R1_SOURCE_NATIVE_INPUT_COMPLETENESS",
            "RequiredCondition": (
                "valid D,D_prime,D_double_prime,H_D,H_D_prime vectors plus selection metadata and covariance/bootstrap"
            ),
            "SupportiveOutcome": "all required source-native objects valid and covariance-aware scorecard executable",
            "WeakeningOutcome": "vectors valid but covariance/bootstrap missing; preflight-only scoring remains allowed",
            "StrongNegativeOutcome": "vectors invalid, missing required columns, or formula denominators fail",
            "InterpretationIfTriggered": "without complete source-native objects, no physical-null measurement comparison is allowed",
            "NextAction": "run export validation and uncertainty validation before bridge interpretation",
        },
        {
            "RuleID": "SNBR_R2_K2_VS_SOURCE_NATIVE_NULL",
            "RequiredCondition": "score source-native Omega_R_plus_3Omega_Q under the same route/covariance as locked K2",
            "SupportiveOutcome": "locked K2 is closer than source-native backreaction null on the registered primary route",
            "WeakeningOutcome": "source-native null is comparable to locked K2 within the registered uncertainty band",
            "StrongNegativeOutcome": "source-native null is clearly closer than locked K2 under source-native covariance",
            "InterpretationIfTriggered": "tests whether backreaction can replace or absorb the locked K2 response",
            "NextAction": "report K2-vs-source-native deltas without refitting K2 or scaling the null to target",
        },
        {
            "RuleID": "SNBR_R3_SHAPE_CLASSIFICATION",
            "RequiredCondition": "run the same shape/amplitude diagnosis used for surrogate families",
            "SupportiveOutcome": "source-native family falls into sign/shape mismatch or mixed mismatch classes while K2 remains closer",
            "WeakeningOutcome": f"source-native family resembles the K2-like surrogate class led by {top_family} but does not beat K2",
            "StrongNegativeOutcome": "source-native family is both K2-like and target-aligned while beating locked K2",
            "InterpretationIfTriggered": "separates physical-null shape overlap from physical-null replacement",
            "NextAction": "compare future source-native class to surrogate rank without promoting the surrogate rank itself",
        },
        {
            "RuleID": "SNBR_R4_SIGN_STABLE_ROWS",
            "RequiredCondition": "evaluate only predeclared sign-stable rows separately from sign-unstable rows",
            "SupportiveOutcome": "locked K2 has equal or better stable-row sign agreement than source-native backreaction",
            "WeakeningOutcome": "source-native null improves unstable rows but not stable rows",
            "StrongNegativeOutcome": "source-native null improves stable rows and locked K2 has stable-row sign contradictions",
            "InterpretationIfTriggered": "protects against over-reading reconstruction-sensitive sign changes",
            "NextAction": "publish all/stable/unstable subset scorecards side by side",
        },
        {
            "RuleID": "SNBR_R5_FORBIDDEN_SCALE_DIAGNOSTIC",
            "RequiredCondition": "best-scale diagnostics may be computed only for mismatch classification",
            "SupportiveOutcome": "K2 remains closer without fitting a source-native-null amplitude",
            "WeakeningOutcome": "source-native null becomes competitive only after a forbidden target-fit scale",
            "StrongNegativeOutcome": "source-native null beats K2 without any fitted scale under the registered covariance",
            "InterpretationIfTriggered": "prevents amplitude-rescue narratives on either side",
            "NextAction": "keep best-scale columns labeled forbidden-for-claims",
        },
        {
            "RuleID": "SNBR_R6_MEASUREMENT_LANGUAGE_LOCK",
            "RequiredCondition": "all reporting must preserve measurement-validation closure unless every registered requirement is satisfied",
            "SupportiveOutcome": "preflight support can be strengthened while measurement language remains closed",
            "WeakeningOutcome": "mixed result; leave as diagnostic physical-null comparison",
            "StrongNegativeOutcome": "source-native covariance-aware result substantially favors the physical null over locked K2",
            "InterpretationIfTriggered": "controls language, not physics",
            "NextAction": "update claim ladder, not locked K2 parameters",
        },
    ]

    rules_df = pd.DataFrame(rules)
    rules_df["LockedK2Changed"] = False
    rules_df["RhoGreaterThan4Allowed"] = False
    rules_df["K1RefitAllowed"] = False
    rules_df["ScaleFitAllowedForClaims"] = False
    rules_df["MeasurementValidationAllowed"] = False
    rules_df["ClaimBoundary"] = CLAIM_BOUNDARY
    rules_df.to_csv(OUT_RULES, index=False)

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_BACKREACTION_DECISION_RULES_V1",
                "Rules": len(rules_df),
                "TopSurrogateFamilyForFutureComparison": top_family,
                "TopSurrogateMeanCorrelationWithK2": top_corr,
                "SurrogateMedianCorrelationWithK2": median_corr_k2,
                "SurrogateMedianCorrelationWithTarget": median_corr_target,
                "SurrogateCasesWhereK2BeatsBackreactionNull": int(bridge["K2BeatsSurrogateBackreactionCases"]),
                "SourceNativeExportReady": False,
                "SourceNativeCovarianceReady": False,
                "LockedK2Changed": False,
                "RhoGreaterThan4Allowed": False,
                "K1RefitAllowed": False,
                "ScaleFitAllowedForClaims": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_BACKREACTION_DECISION_RULES_REGISTERED",
                "StrongestAllowedClaim": (
                    "future source-native backreaction exports now have predeclared interpretation rules"
                ),
                "PrimaryResidualRisk": (
                    "rules cannot replace missing source-native derivative vectors and covariance"
                ),
                "NextAction": "apply these rules to real source-native exports when available; keep locked K2 unchanged",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Backreaction Decision Rules",
                "",
                "Status: decision rules registered; source-native exports still missing.",
                "",
                "These rules define how future source-native backreaction vectors will be interpreted against locked K2. They do not select a physical null, fit an amplitude, or authorize measurement language.",
                "",
                "## Anchors From Surrogate Rehearsal",
                "",
                f"- Top surrogate follow-up class: `{top_family}`",
                f"- Top surrogate mean corr(K2): {top_corr:.3f}",
                f"- Surrogate median corr(K2): {median_corr_k2:.3f}",
                f"- Surrogate median corr(target): {median_corr_target:.3f}",
                "",
                "## Outputs",
                "",
                f"- Rules: `{OUT_RULES.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_RULES}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
