#!/usr/bin/env python3
"""Build the Tau Core A2 preflight claim ladder.

The ladder separates strong preflight statements from conditional diagnostics
and blocked measurement claims. It does not change K2, fit K1, or authorize
measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

MIDHIGH = EVIDENCE / "midhigh_component_stability_summary.csv"
LOW_DEPTH = EVIDENCE / "low_depth_tau_core_support_summary.csv"
SOURCE_NATIVE = EVIDENCE / "source_native_reproduction_task_readiness.csv"
FULL_GATE = EVIDENCE / "k2_a2_full_likelihood_gate_readiness.csv"

OUT_MATRIX = EVIDENCE / "tau_core_a2_claim_ladder.csv"
OUT_SUMMARY = EVIDENCE / "tau_core_a2_claim_ladder_summary.csv"
OUT_DOC = DOCS / "tau_core_a2_claim_ladder.md"

CLAIM_BOUNDARY = "tau_core_a2_claim_ladder_no_measurement_validation"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty evidence file: {path}")
    return df.iloc[0]


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    midhigh = read_first(MIDHIGH)
    low_depth = read_first(LOW_DEPTH)
    source_native = read_first(SOURCE_NATIVE)
    full_gate = pd.read_csv(FULL_GATE)
    required = full_gate[full_gate["GateClass"].astype(str).eq("required")]
    blocked_required = required[required["Status"].astype(str).eq("BLOCKED")]

    midhigh_pass = (
        int(midhigh["ChecksSurvivingThreshold"]) == int(midhigh["Checks"])
        and not truthy(midhigh["MeasurementValidationAllowed"])
    )
    low_operator_pass = (
        int(low_depth["TauCoreSuppressionChecks"]) >= 3
        and not truthy(low_depth["MeasurementValidationAllowed"])
    )
    low_physical_null_stable = truthy(low_depth["LowDepthStableAsPilotPhysicalNull"])
    source_native_ready = truthy(source_native["SourceNativeScoringReady"])

    rows = [
        {
            "ClaimLevel": 1,
            "ClaimID": "LOCKED_OPERATOR_LOW_DEPTH_SUPPRESSION",
            "EvidenceFile": str(LOW_DEPTH.relative_to(ROOT)),
            "Status": "STRONG_PREFLIGHT" if low_operator_pass else "WARNING",
            "AllowedLanguage": (
                "Low-depth response is naturally suppressed by the locked finite-memory operator and target-scale ratios."
            ),
            "DisallowedLanguage": "Low-depth physical-null suppression has measurement-grade status.",
            "KeyEvidence": (
                f"locked delta-W low/high={low_depth['LockedDeltaWLowToHighRatio']}; "
                f"locked K2 target low/high={low_depth['LockedK2TargetLowToHighRatio']}; "
                f"memory boost target low/high={low_depth['MemoryBoostTargetLowToHighRatio']}."
            ),
            "ResidualRisk": (
                "operator-level suppression is stronger than the current derivative-pilot low-depth physical-null route"
            ),
            "NextAction": "keep this as an operator-level Tau Core claim until source-native derivative/covariance exists",
        },
        {
            "ClaimLevel": 2,
            "ClaimID": "MIDHIGH_BACKREACTION_LIKE_COMPONENT",
            "EvidenceFile": str(MIDHIGH.relative_to(ROOT)),
            "Status": "STRONG_PREFLIGHT" if midhigh_pass else "WARNING",
            "AllowedLanguage": (
                "The non-source-native stress audits consistently retain a mid/high backreaction-like K2 component."
            ),
            "DisallowedLanguage": "The mid/high component is observationally validated.",
            "KeyEvidence": (
                f"checks={midhigh['ChecksSurvivingThreshold']}/{midhigh['Checks']}; "
                f"mid/high lower min={midhigh['MidHighLowerMinAcrossChecks']}; "
                f"mid/high central median={midhigh['MidHighCentralMedianAcrossChecks']}."
            ),
            "ResidualRisk": "component magnitude remains route-sensitive without source-native covariance",
            "NextAction": "carry forward as the strongest current preflight component statement",
        },
        {
            "ClaimLevel": 3,
            "ClaimID": "LOW_DEPTH_PHYSICAL_NULL_SUPPRESSION",
            "EvidenceFile": str(LOW_DEPTH.relative_to(ROOT)),
            "Status": "WEAK_CONDITIONAL" if not low_physical_null_stable else "STRONG_PREFLIGHT",
            "AllowedLanguage": (
                "The derivative-pilot low-depth physical-null route is reconstruction-sensitive and remains conditional."
            ),
            "DisallowedLanguage": "The derivative-pilot low-depth route independently validates the Tau Core response.",
            "KeyEvidence": (
                f"pilot physical-null stable={low_depth['LowDepthStableAsPilotPhysicalNull']}; "
                f"reconstruction warning checks={low_depth['ReconstructionWarningChecks']}."
            ),
            "ResidualRisk": str(low_depth["PrimaryResidualRisk"]),
            "NextAction": "do not promote low-depth physical-null language before source-native rerun",
        },
        {
            "ClaimLevel": 4,
            "ClaimID": "SOURCE_NATIVE_BACKREACTION_NULL",
            "EvidenceFile": str(SOURCE_NATIVE.relative_to(ROOT)),
            "Status": "BLOCKED_FOR_MEASUREMENT" if not source_native_ready else "PREFLIGHT_READY",
            "AllowedLanguage": (
                "Source-native backreaction reproduction remains the main route to a measurement-grade physical null."
            ),
            "DisallowedLanguage": "The current public derivative pilot is source-native.",
            "KeyEvidence": (
                f"available tasks={source_native['AvailableRequiredTasks']}/{source_native['RequiredTasks']}; "
                f"blocking tasks={source_native['BlockingTasks']}."
            ),
            "ResidualRisk": "missing upstream derivative reconstruction table and attached covariance",
            "NextAction": "obtain or reproduce D_A, H_D derivative vectors with source-native covariance",
        },
        {
            "ClaimLevel": 5,
            "ClaimID": "MEASUREMENT_VALIDATION",
            "EvidenceFile": str(FULL_GATE.relative_to(ROOT)),
            "Status": "NOT_AUTHORIZED",
            "AllowedLanguage": "Measurement validation remains closed until the registered public benchmark is source-native and covariance-aware.",
            "DisallowedLanguage": "Tau Core A2 has measurement-grade status.",
            "KeyEvidence": (
                f"required gates={len(required)}; blocked required gates={len(blocked_required)}; "
                "MeasurementValidationAllowed=False."
            ),
            "ResidualRisk": "full measurement language would overstate the current preflight packet",
            "NextAction": "keep locked K2 unchanged and rerun only after source-native public covariance is available",
        },
    ]

    matrix = pd.DataFrame(rows)
    matrix["LockedK2Changed"] = False
    matrix["RhoGreaterThan4Allowed"] = False
    matrix["K1RefitAllowed"] = False
    matrix["MeasurementValidationAllowed"] = False
    matrix["ClaimBoundary"] = CLAIM_BOUNDARY
    matrix.to_csv(OUT_MATRIX, index=False)

    strong_preflight = int(matrix["Status"].eq("STRONG_PREFLIGHT").sum())
    warnings = int(matrix["Status"].str.contains("WEAK|BLOCKED|NOT_AUTHORIZED|WARNING", regex=True).sum())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "TAU_CORE_A2_CLAIM_LADDER_V1",
                "Claims": len(matrix),
                "StrongPreflightClaims": strong_preflight,
                "ConditionalOrBlockedClaims": warnings,
                "LockedOperatorLowDepthSuppression": low_operator_pass,
                "MidHighBackreactionLikeComponentStable": midhigh_pass,
                "LowDepthPhysicalNullStable": low_physical_null_stable,
                "SourceNativeScoringReady": source_native_ready,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "A2_PREFLIGHT_CLAIM_LADDER_READY_MEASUREMENT_CLOSED",
                "StrongestAllowedClaim": (
                    "A2 has strong preflight support for locked low-depth operator suppression and a stable mid/high backreaction-like component"
                ),
                "PrimaryResidualRisk": (
                    "low-depth physical-null promotion and measurement validation still require source-native derivative/covariance exports"
                ),
                "NextAction": "use the claim ladder for paper language; continue with source-native backreaction reproduction",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Tau Core A2 Claim Ladder",
                "",
                "Status: preflight claim ladder ready; measurement validation closed.",
                "",
                "This ladder separates what the current packet can say from what remains conditional or blocked.",
                "",
                "## Allowed Strong Preflight Language",
                "",
                "- Low-depth suppression is supported at locked Tau Core operator and target-scale level.",
                "- A mid/high backreaction-like K2 component survives the current non-source-native stress audits.",
                "",
                "## Conditional Or Closed Language",
                "",
                "- The derivative-pilot low-depth physical-null route remains weak and reconstruction-sensitive.",
                "- Source-native backreaction reproduction is still required for a measurement-grade physical null.",
                "- Measurement validation remains closed.",
                "",
                "## Outputs",
                "",
                f"- Matrix: `{OUT_MATRIX.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_MATRIX}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
