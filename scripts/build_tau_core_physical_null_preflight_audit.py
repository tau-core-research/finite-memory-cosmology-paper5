#!/usr/bin/env python3
"""Summarize physical-null preflight status for the Tau Core A2 chain.

This audit distinguishes three things that should not be conflated:

1. generic polynomial smoothing controls;
2. physical-null sanity/sensitivity proxies;
3. calibrated physical-null benchmarks usable for measurement validation.

The current branch has (2), not (3).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PHYS_SUMMARY = EVIDENCE / "physical_null_preflight_summary.csv"
PHYS_SCORE = EVIDENCE / "physical_null_preflight_scorecard.csv"
MAP_SUMMARY = EVIDENCE / "physical_null_mapping_readiness_summary.csv"
ALPHA_AUTH = EVIDENCE / "physical_null_alpha_scoring_authorization_summary.csv"
TRIAGE = EVIDENCE / "physical_null_candidate_triage.csv"
TARGET_POLY = EVIDENCE / "tau_core_target_regime_polynomial_summary.csv"

OUT = EVIDENCE / "tau_core_physical_null_preflight_audit.csv"
SUMMARY = EVIDENCE / "tau_core_physical_null_preflight_summary.csv"
DOC = DOCS / "tau_core_physical_null_preflight_audit.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    phys = pd.read_csv(PHYS_SUMMARY).iloc[0]
    score = pd.read_csv(PHYS_SCORE)
    mapping = pd.read_csv(MAP_SUMMARY).iloc[0]
    alpha = pd.read_csv(ALPHA_AUTH).iloc[0]
    triage = pd.read_csv(TRIAGE)
    target_poly = pd.read_csv(TARGET_POLY).iloc[0]

    physical_rows = score[score["ModelClass"].astype(str).str.startswith("physical_null")]
    context_rows = score[score["ModelID"].astype(str).isin(["K1_NO_MEMORY_CONTEXT", "K2_LOCKED_RHO4_CONTEXT"])]
    k2_aic = float(phys["K2AIC"])
    best_phys_aic = float(phys["BestPhysicalNullAIC"])
    k1_aic = float(phys["K1AIC"])
    delta_k2_phys = float(phys["DeltaAIC_K2_minus_BestPhysicalNull"])
    delta_k2_k1 = float(phys["DeltaAIC_K2_minus_K1"])

    primary_backreaction = triage[triage["NullID"].astype(str).str.contains("BACKREACTION", na=False)]
    primary_optical = triage[triage["NullID"].astype(str).str.contains("DYER_ROEDER", na=False)]

    rows = [
        {
            "CriterionID": "PHYSICAL_NULL_SCORECARD_EXISTS",
            "Status": "PASS" if len(physical_rows) > 0 and len(context_rows) >= 2 else "BLOCKED",
            "Evidence": f"physical_null_rows={len(physical_rows)}; context_rows={len(context_rows)}",
            "Interpretation": "A2 is now compared against physical-null proxy controls, not only generic polynomial controls.",
            "ClaimImpact": "strengthens preflight chain if K2 remains competitive",
            "ClaimBoundary": "physical_null_preflight_no_measurement_validation",
        },
        {
            "CriterionID": "K2_VS_PHYSICAL_NULL_PROXY",
            "Status": "PASS" if delta_k2_phys < 0 else "WARNING",
            "Evidence": f"K2AIC={k2_aic}; BestPhysicalNullAIC={best_phys_aic}; DeltaAIC_K2_minus_BestPhysicalNull={delta_k2_phys}",
            "Interpretation": "Current calibrated-as-proxy physical nulls do not beat locked K2 in the preflight scorecard.",
            "ClaimImpact": "supports A2 against current physical-null proxy layer",
            "ClaimBoundary": "physical_null_preflight_no_measurement_validation",
        },
        {
            "CriterionID": "K2_VS_K1_CONTEXT",
            "Status": "PASS" if delta_k2_k1 < 0 else "WARNING",
            "Evidence": f"K2AIC={k2_aic}; K1AIC={k1_aic}; DeltaAIC_K2_minus_K1={delta_k2_k1}",
            "Interpretation": "Locked K2 improves over the no-memory context under the physical-null preflight covariance route.",
            "ClaimImpact": "supports memory-active preflight reading",
            "ClaimBoundary": "physical_null_preflight_no_measurement_validation",
        },
        {
            "CriterionID": "PHYSICAL_NULL_MAPPING_BLOCKER",
            "Status": "WARNING" if int(mapping["BenchmarkInputsReadyNow"]) == 0 else "PASS",
            "Evidence": f"BenchmarkInputsReadyNow={mapping['BenchmarkInputsReadyNow']}; PrimaryBlockingIssue={mapping['PrimaryBlockingIssue']}",
            "Interpretation": "Physical null rows remain mapping/covariance blocked for measurement-grade benchmarking.",
            "ClaimImpact": "keeps measurement validation closed",
            "ClaimBoundary": "physical_null_preflight_no_measurement_validation",
        },
        {
            "CriterionID": "ALPHA_SCORING_AUTHORIZATION",
            "Status": "WARNING" if int(alpha["ScorecardAuthorizedCandidates"]) == 0 else "PASS",
            "Evidence": f"ScorecardAuthorizedCandidates={alpha['ScorecardAuthorizedCandidates']}; PrimaryBlockingIssue={alpha['PrimaryBlockingIssue']}",
            "Interpretation": "Dyer-Roeder alpha branch has transform/covariance previews but no source-native scoring authorization.",
            "ClaimImpact": "prevents overclaiming the optical null comparison",
            "ClaimBoundary": "physical_null_preflight_no_measurement_validation",
        },
        {
            "CriterionID": "BACKREACTION_INGEST_GAP",
            "Status": "WARNING",
            "Evidence": f"backreaction_candidates={len(primary_backreaction)}; optical_candidates={len(primary_optical)}",
            "Interpretation": "Backreaction remains a candidate/source-ingest gap rather than a calibrated benchmark.",
            "ClaimImpact": "next physical-null priority is source extraction and mapping, not K2 modification",
            "ClaimBoundary": "physical_null_preflight_no_measurement_validation",
        },
        {
            "CriterionID": "POLYNOMIAL_AND_PHYSICAL_NULL_SPLIT",
            "Status": "PASS" if truthy(target_poly["MemoryActivePolynomialCheckPassed"]) else "WARNING",
            "Evidence": f"target_regime_status={target_poly['CurrentStatus']}; physical_best={phys['BestPhysicalNullModelForDiagnosticsOnly']}",
            "Interpretation": "Polynomial remains an overfit-risk blocker, while physical-null proxies currently do not explain A2 better.",
            "ClaimImpact": "supports target-regime preflight but not all-depth measurement validation",
            "ClaimBoundary": "physical_null_preflight_no_measurement_validation",
        },
    ]

    audit = pd.DataFrame(rows)
    audit.to_csv(OUT, index=False)

    passed = int(audit["Status"].eq("PASS").sum())
    warnings = int(audit["Status"].eq("WARNING").sum())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "TAU_CORE_PHYSICAL_NULL_PREFLIGHT_AUDIT",
                "Criteria": len(audit),
                "PassedCriteria": passed,
                "WarningCriteria": warnings,
                "K2BeatsBestPhysicalNullProxy": delta_k2_phys < 0,
                "K2ImprovesOverK1Context": delta_k2_k1 < 0,
                "PhysicalNullBenchmarkInputsReadyNow": int(mapping["BenchmarkInputsReadyNow"]),
                "AlphaScorecardAuthorizedCandidates": int(alpha["ScorecardAuthorizedCandidates"]),
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "PHYSICAL_NULL_PROXY_LAYER_SUPPORTS_A2_PREFLIGHT_BUT_CALIBRATION_BLOCKED",
                "StrongestAllowedClaim": "locked A2 is stronger than current physical-null proxy controls in preflight scoring",
                "PrimaryResidualRisk": "physical nulls lack measurement-grade source-split mapping and source-native covariance",
                "NextAction": "ingest or derive calibrated backreaction/optical physical-null mappings before stronger claims",
                "ClaimBoundary": "physical_null_preflight_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    DOC.write_text(
        "\n".join(
            [
                "# Tau Core Physical-Null Preflight Audit",
                "",
                "Status: physical-null proxy layer supports A2 preflight; no measurement validation.",
                "",
                "The current physical-null comparison is useful because it separates generic polynomial smoothing from physically motivated controls.",
                "Under the existing preflight scorecard, locked K2 is stronger than the current physical-null proxy controls.",
                "",
                "This is not a calibrated physical-null benchmark yet. Backreaction and Dyer-Roeder/optical branches still need source-split mapping and source-native covariance before measurement-grade comparison.",
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
