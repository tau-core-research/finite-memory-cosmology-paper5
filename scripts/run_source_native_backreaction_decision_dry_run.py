#!/usr/bin/env python3
"""Apply future source-native decision rules to surrogate exports as a dry run.

This checks that the registered rules are executable. The result is explicitly
surrogate-only and cannot be used as source-native evidence.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

RULES = EVIDENCE / "source_native_backreaction_decision_rules.csv"
SURROGATE_EXPORT = EVIDENCE / "source_native_surrogate_family_export_summary.csv"
SURROGATE_BRIDGE = EVIDENCE / "source_native_surrogate_bridge_summary.csv"
SURROGATE_SHAPE = EVIDENCE / "source_native_surrogate_bridge_shape_summary.csv"
SURROGATE_RANK = EVIDENCE / "source_native_surrogate_family_rank_summary.csv"

OUT_DRY_RUN = EVIDENCE / "source_native_backreaction_decision_dry_run.csv"
OUT_SUMMARY = EVIDENCE / "source_native_backreaction_decision_dry_run_summary.csv"
OUT_DOC = DOCS / "source_native_backreaction_decision_dry_run.md"

CLAIM_BOUNDARY = "source_native_backreaction_decision_dry_run_no_measurement_validation"


def read_first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty evidence file: {path}")
    return df.iloc[0]


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    rules = pd.read_csv(RULES)
    export = read_first(SURROGATE_EXPORT)
    bridge = read_first(SURROGATE_BRIDGE)
    shape = read_first(SURROGATE_SHAPE)
    rank = read_first(SURROGATE_RANK)

    route_cases = int(bridge["RouteFamilyCases"])
    k2_beats_surrogate = int(bridge["K2BeatsSurrogateBackreactionCases"])
    k2_like_cases = int(shape["K2LikeShapeCases"])
    sign_or_shape_cases = int(shape["SignOrShapeMismatchCases"])
    source_native_ready = False
    covariance_ready = False

    outcomes = {
        "SNBR_R1_SOURCE_NATIVE_INPUT_COMPLETENESS": (
            "WEAKENING_PRECHECK"
            if bool(export["SurrogateFamilyExportsReady"]) and not source_native_ready
            else "STRONG_NEGATIVE"
        ),
        "SNBR_R2_K2_VS_SOURCE_NATIVE_NULL": (
            "SUPPORTIVE_DRY_RUN" if k2_beats_surrogate == route_cases else "WEAKENING_OR_NEGATIVE_DRY_RUN"
        ),
        "SNBR_R3_SHAPE_CLASSIFICATION": (
            "SUPPORTIVE_DRY_RUN"
            if sign_or_shape_cases >= k2_like_cases and k2_beats_surrogate == route_cases
            else "WEAKENING_DRY_RUN"
        ),
        "SNBR_R4_SIGN_STABLE_ROWS": "WEAKENING_DRY_RUN_NO_SOURCE_NATIVE_STABLE_ROW_COVARIANCE",
        "SNBR_R5_FORBIDDEN_SCALE_DIAGNOSTIC": (
            "SUPPORTIVE_DRY_RUN" if k2_beats_surrogate == route_cases else "STRONG_NEGATIVE_DRY_RUN"
        ),
        "SNBR_R6_MEASUREMENT_LANGUAGE_LOCK": "SUPPORTIVE_LANGUAGE_LOCK",
    }

    interpretations = {
        "SNBR_R1_SOURCE_NATIVE_INPUT_COMPLETENESS": (
            "surrogate objects are executable, but source-native export and covariance remain missing"
        ),
        "SNBR_R2_K2_VS_SOURCE_NATIVE_NULL": (
            f"locked K2 is closer than surrogate null in {k2_beats_surrogate}/{route_cases} route-family cases"
        ),
        "SNBR_R3_SHAPE_CLASSIFICATION": (
            f"surrogate classes are mostly mismatch/mixed rather than replacement-like; K2-like cases={k2_like_cases}"
        ),
        "SNBR_R4_SIGN_STABLE_ROWS": (
            "stable-row rule is present, but dry-run cannot replace source-native stable-row covariance scoring"
        ),
        "SNBR_R5_FORBIDDEN_SCALE_DIAGNOSTIC": (
            "K2 remains closer without applying forbidden amplitude rescue to surrogate nulls"
        ),
        "SNBR_R6_MEASUREMENT_LANGUAGE_LOCK": (
            "dry-run preserves measurement-validation closure"
        ),
    }

    rows = []
    for _, rule in rules.iterrows():
        rule_id = str(rule["RuleID"])
        outcome = outcomes.get(rule_id, "NOT_EVALUATED")
        rows.append(
            {
                "AuditID": "SOURCE_NATIVE_BACKREACTION_DECISION_DRY_RUN_V1",
                "RuleID": rule_id,
                "DryRunInput": "surrogate_family_exports_not_source_native",
                "DryRunOutcome": outcome,
                "Interpretation": interpretations.get(rule_id, "not evaluated"),
                "SupportiveOutcomeDefinition": rule["SupportiveOutcome"],
                "WeakeningOutcomeDefinition": rule["WeakeningOutcome"],
                "StrongNegativeOutcomeDefinition": rule["StrongNegativeOutcome"],
                "SourceNativeExportReady": source_native_ready,
                "SourceNativeCovarianceReady": covariance_ready,
                "LockedK2Changed": False,
                "RhoGreaterThan4Allowed": False,
                "K1RefitAllowed": False,
                "ScaleFitAllowedForClaims": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    dry = pd.DataFrame(rows)
    dry.to_csv(OUT_DRY_RUN, index=False)
    supportive = int(dry["DryRunOutcome"].str.contains("SUPPORTIVE", regex=False).sum())
    weakening = int(dry["DryRunOutcome"].str.contains("WEAKENING", regex=False).sum())
    strong_negative = int(dry["DryRunOutcome"].str.contains("STRONG_NEGATIVE", regex=False).sum())

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_BACKREACTION_DECISION_DRY_RUN_V1",
                "RulesEvaluated": len(dry),
                "SupportiveDryRunRules": supportive,
                "WeakeningDryRunRules": weakening,
                "StrongNegativeDryRunRules": strong_negative,
                "TopSurrogateFamily": rank["TopFamilyID"],
                "K2BeatsSurrogateCases": k2_beats_surrogate,
                "RouteFamilyCases": route_cases,
                "SourceNativeExportReady": source_native_ready,
                "SourceNativeCovarianceReady": covariance_ready,
                "LockedK2Changed": False,
                "RhoGreaterThan4Allowed": False,
                "K1RefitAllowed": False,
                "ScaleFitAllowedForClaims": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_DECISION_RULES_DRY_RUN_EXECUTABLE",
                "StrongestAllowedClaim": (
                    "decision rules are executable on surrogate inputs and preserve source-native measurement closure"
                ),
                "PrimaryResidualRisk": (
                    "surrogate dry-run outcomes do not count as source-native physical-null evidence"
                ),
                "NextAction": "rerun the same decision rules on real source-native exports and covariance when available",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Backreaction Decision Dry Run",
                "",
                "Status: decision rules executable on surrogate inputs; source-native evidence still missing.",
                "",
                "This dry run applies the registered source-native interpretation rules to the surrogate family exports. It verifies the machinery and preserves the measurement-language lock.",
                "",
                "## Result",
                "",
                f"- Rules evaluated: {len(dry)}",
                f"- Supportive dry-run rules: {supportive}",
                f"- Weakening dry-run rules: {weakening}",
                f"- Strong-negative dry-run rules: {strong_negative}",
                f"- K2 beats surrogate cases: {k2_beats_surrogate}/{route_cases}",
                "",
                "## Outputs",
                "",
                f"- Dry run: `{OUT_DRY_RUN.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DRY_RUN}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
