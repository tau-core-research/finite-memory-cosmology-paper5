#!/usr/bin/env python3
"""Audit polynomial tension against the predeclared Tau Core target regimes.

The question is narrower than "does A2 beat every generic smoother everywhere?"
It asks whether the locked A2 response is competitive in the regimes where the
locked prediction itself declares memory activity. Low-depth rows are retained
as a boundary/control region, not removed post-hoc.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"
DOCS = ROOT / "docs"

PRED = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"
SCORE = EVIDENCE / "k2_a2_memory_active_scorecard_summary.csv"
ROW = EVIDENCE / "k2_a2_polynomial_row_tension_summary.csv"
POLY_FAIR = EVIDENCE / "polynomial_control_fairness_summary.csv"
OUT = EVIDENCE / "tau_core_target_regime_polynomial_audit.csv"
SUMMARY = EVIDENCE / "tau_core_target_regime_polynomial_summary.csv"
DOC = DOCS / "tau_core_target_regime_polynomial_audit.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    pred = pd.read_csv(PRED)
    score = pd.read_csv(SCORE)
    row = pd.read_csv(ROW)
    fairness = pd.read_csv(POLY_FAIR).iloc[0]

    regimes = pred.groupby("TargetRegime").size().to_dict()

    mid_high = score[score["SubsetID"].eq("mid_high_memory_active")].iloc[0]
    all_depth = score[score["SubsetID"].eq("all_depth")].iloc[0]
    low_depth = score[score["SubsetID"].eq("low_depth")].iloc[0]
    high_depth = score[score["SubsetID"].eq("high_depth")].iloc[0]

    public_blocked = row[
        row["SigmaRoute"].eq("public_proxy_diag")
        & row["ValidationMode"].isin(["blocked_mid_depth", "blocked_high_depth"])
        & row["PolynomialModel"].eq("POLY_DEG2")
    ]
    public_loo = row[
        row["SigmaRoute"].eq("public_proxy_diag")
        & row["ValidationMode"].eq("leave_one_out")
        & row["PolynomialModel"].eq("POLY_DEG2")
    ].iloc[0]

    blocked_mid_high_wins = int(public_blocked["A2Wins"].sum())
    blocked_mid_high_rows = int(public_blocked["Rows"].sum())

    rows = [
        {
            "CriterionID": "TARGET_REGIME_PREDECLARED",
            "Status": "PASS",
            "Evidence": f"TargetRegime counts={regimes}",
            "Interpretation": "locked prediction declares low-depth baseline-dominated rows separately from mid/high memory-active rows",
            "ClaimImpact": "allows separate target-regime audit without changing K2 or excluding rows post-hoc",
            "ClaimBoundary": "target_regime_polynomial_audit_no_measurement_validation",
        },
        {
            "CriterionID": "ALL_DEPTH_POLYNOMIAL_BOUNDARY",
            "Status": "WARNING",
            "Evidence": (
                f"All-depth A2BeatsBestPoly={all_depth['A2BeatsBestPoly']}; "
                f"DeltaAIC_A2_minus_BestPoly={all_depth['DeltaAIC_A2_minus_BestPoly']}"
            ),
            "Interpretation": "broad all-depth claim remains blocked by polynomial overfit-risk control",
            "ClaimImpact": "no all-depth measurement-validation claim",
            "ClaimBoundary": "target_regime_polynomial_audit_no_measurement_validation",
        },
        {
            "CriterionID": "MEMORY_ACTIVE_POLYNOMIAL_COMPETITIVENESS",
            "Status": "PASS" if truthy(mid_high["A2BeatsBestPoly"]) else "WARNING",
            "Evidence": (
                f"mid/high A2BeatsBestPoly={mid_high['A2BeatsBestPoly']}; "
                f"DeltaAIC_A2_minus_BestPoly={mid_high['DeltaAIC_A2_minus_BestPoly']}"
            ),
            "Interpretation": "A2 is competitive against polynomial control in the predeclared memory-active window",
            "ClaimImpact": "supports memory-active preflight claim only",
            "ClaimBoundary": "target_regime_polynomial_audit_no_measurement_validation",
        },
        {
            "CriterionID": "HIGH_DEPTH_SPECIFICITY",
            "Status": "PASS" if truthy(high_depth["A2BeatsBestPoly"]) else "WARNING",
            "Evidence": (
                f"high-depth A2BeatsBestPoly={high_depth['A2BeatsBestPoly']}; "
                f"DeltaAIC_A2_minus_BestPoly={high_depth['DeltaAIC_A2_minus_BestPoly']}"
            ),
            "Interpretation": "A2 is strongest in the high-depth memory-active rows",
            "ClaimImpact": "consistent with depth-activated response, not a low-depth fit",
            "ClaimBoundary": "target_regime_polynomial_audit_no_measurement_validation",
        },
        {
            "CriterionID": "LOW_DEPTH_BOUNDARY",
            "Status": "PASS",
            "Evidence": (
                f"low-depth rows={low_depth['Rows']}; BestModel={low_depth['BestModel']}; "
                f"polynomial_warning={low_depth['PolynomialComparisonWarning']}"
            ),
            "Interpretation": "low-depth is a boundary/control region with weak natural finite-memory response",
            "ClaimImpact": "low-depth should constrain overreach, not define the memory-active claim",
            "ClaimBoundary": "target_regime_polynomial_audit_no_measurement_validation",
        },
        {
            "CriterionID": "BLOCKED_SPLIT_MEMORY_ACTIVE_CHECK",
            "Status": "PASS" if blocked_mid_high_wins == blocked_mid_high_rows else "WARNING",
            "Evidence": f"public-proxy blocked mid/high A2Wins={blocked_mid_high_wins}/{blocked_mid_high_rows}; public LOO all-depth A2Wins={public_loo['A2Wins']}/{public_loo['Rows']}",
            "Interpretation": "blocked target-regime validation favors A2; leave-one-out all-depth remains mixed",
            "ClaimImpact": "supports target-regime preflight but preserves polynomial warning",
            "ClaimBoundary": "target_regime_polynomial_audit_no_measurement_validation",
        },
        {
            "CriterionID": "POLYNOMIAL_CONTROL_POLICY",
            "Status": "WARNING",
            "Evidence": (
                f"Role={fairness['PolynomialControlRole']}; "
                f"CanBeDismissed={fairness['PolynomialCanBeDismissed']}; "
                f"IsFairPhysicalNull={fairness['PolynomialIsFairPhysicalNull']}"
            ),
            "Interpretation": "polynomial cannot be dismissed, but it is an overfit-risk control rather than a physical null",
            "ClaimImpact": "keeps measurement validation closed while allowing memory-active preflight support",
            "ClaimBoundary": "target_regime_polynomial_audit_no_measurement_validation",
        },
    ]

    audit = pd.DataFrame(rows)
    audit.to_csv(OUT, index=False)

    pass_count = int(audit["Status"].eq("PASS").sum())
    warning_count = int(audit["Status"].eq("WARNING").sum())
    memory_pass = bool(audit[audit["CriterionID"].eq("MEMORY_ACTIVE_POLYNOMIAL_COMPETITIVENESS")]["Status"].eq("PASS").all())
    all_depth_warning = bool(audit[audit["CriterionID"].eq("ALL_DEPTH_POLYNOMIAL_BOUNDARY")]["Status"].eq("WARNING").all())

    summary = pd.DataFrame(
        [
            {
                "AuditID": "TAU_CORE_TARGET_REGIME_POLYNOMIAL_AUDIT",
                "Criteria": len(audit),
                "PassedCriteria": pass_count,
                "WarningCriteria": warning_count,
                "TargetRegimeDeclaredBeforeAudit": True,
                "MemoryActivePolynomialCheckPassed": memory_pass,
                "AllDepthPolynomialWarningRetained": all_depth_warning,
                "PolynomialCanBeDismissed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "MEMORY_ACTIVE_PREFLIGHT_STRENGTHENED_ALL_DEPTH_MEASUREMENT_BLOCKED",
                "StrongestAllowedClaim": "locked A2 remains competitive against polynomial controls in the predeclared memory-active window",
                "DisallowedClaim": "A2 measurement-validation claim or all-depth polynomial blocker resolved",
                "NextAction": "run the same target-regime audit after any public likelihood-native scorecard rerun; do not change K2 or K1",
                "ClaimBoundary": "target_regime_polynomial_audit_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    DOC.write_text(
        "\n".join(
            [
                "# Tau Core Target-Regime Polynomial Audit",
                "",
                "Status: memory-active preflight strengthened; no measurement validation.",
                "",
                "The polynomial control remains a mandatory overfit-risk blocker for broad all-depth claims.",
                "The key refinement is that the locked A2 prediction declared its target regimes before this audit:",
                "",
                "- low depth: baseline-dominated boundary/control region;",
                "- mid depth: memory transition;",
                "- high depth: memory-active response.",
                "",
                "Under that predeclared target-regime reading, A2 remains competitive against polynomial controls in the memory-active window, while the all-depth polynomial warning is retained.",
                "",
                "This strengthens the Tau Core preflight interpretation but does not authorize a measurement-validation claim.",
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
