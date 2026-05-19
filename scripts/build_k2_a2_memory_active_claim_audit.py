#!/usr/bin/env python3
"""Audit whether the A2 claim is all-depth or memory-active only.

This does not change the locked prediction. It separates the scientific claim
boundary after the row-level polynomial tension audit showed that the public
proxy polynomial advantage is concentrated at low depth.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ROW_TENSION = ROOT / "evidence" / "k2_a2_polynomial_row_tension_summary.csv"
DEPTH_TRANSITION = ROOT / "evidence" / "source_split_a2_depth_transition.csv"
PUBLIC_SCORE = ROOT / "evidence" / "k2_a2_public_covariance_proxy_summary.csv"
OUT = ROOT / "evidence" / "k2_a2_memory_active_claim_audit.csv"
SUMMARY = ROOT / "evidence" / "k2_a2_memory_active_claim_summary.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    row = pd.read_csv(ROW_TENSION)
    depth = pd.read_csv(DEPTH_TRANSITION)
    public = pd.read_csv(PUBLIC_SCORE).iloc[0]

    public_poly2 = row[
        (row["SigmaRoute"].eq("public_proxy_diag"))
        & (row["PolynomialModel"].eq("POLY_DEG2"))
    ].copy()
    loo = public_poly2[public_poly2["ValidationMode"].eq("leave_one_out")].iloc[0]
    blocked = public_poly2[public_poly2["ValidationMode"].str.startswith("blocked_")]
    low = blocked[blocked["ValidationMode"].eq("blocked_low_depth")].iloc[0]
    mid = blocked[blocked["ValidationMode"].eq("blocked_mid_depth")].iloc[0]
    high = blocked[blocked["ValidationMode"].eq("blocked_high_depth")].iloc[0]

    depth_rows = depth.set_index("DepthZone") if "DepthZone" in depth.columns else pd.DataFrame()
    rows = [
        {
            "AuditID": "ALL_DEPTH_PUBLIC_PROXY",
            "ClaimScope": "all_depth",
            "Finding": "A2 improves over K1 and unit K2 but does not beat POLY_DEG2 in the in-sample public proxy.",
            "Evidence": (
                f"A2MinusK1={public['DeltaAIC_A2_minus_K1']}; "
                f"A2MinusUnitK2={public['DeltaAIC_A2_minus_UnitK2']}; "
                f"A2MinusBestPoly={public['DeltaAIC_A2_minus_BestPoly']}"
            ),
            "AllowedClaim": "preflight_support_vs_memory_nulls_only",
            "DisallowedClaim": "all_depth_measurement_validation",
            "ClaimBoundary": "memory_active_claim_audit_no_measurement_validation",
        },
        {
            "AuditID": "LOW_DEPTH_TENSION",
            "ClaimScope": "low_depth",
            "Finding": "Low-depth rows dominate the public-proxy leave-one-out polynomial advantage.",
            "Evidence": (
                f"LOO_A2Wins={loo['A2Wins']}/{loo['Rows']}; "
                f"BlockedLowDepthA2Wins={low['A2Wins']}/{low['Rows']}; "
                f"BlockedLowDepthDeltaChi2={low['DeltaChi2_A2_minus_Poly']}"
            ),
            "AllowedClaim": "low_depth_is_diagnostic_anchor_and_tension_source",
            "DisallowedClaim": "low_depth_detection",
            "ClaimBoundary": "memory_active_claim_audit_no_measurement_validation",
        },
        {
            "AuditID": "MID_DEPTH_MEMORY_ACTIVE",
            "ClaimScope": "mid_depth",
            "Finding": "A2 is competitive in the mid-depth blocked split while retaining at least one local tension point.",
            "Evidence": (
                f"BlockedMidDepthA2Wins={mid['A2Wins']}/{mid['Rows']}; "
                f"BlockedMidDepthDeltaChi2={mid['DeltaChi2_A2_minus_Poly']}"
            ),
            "AllowedClaim": "memory_active_preflight_support_mid_depth",
            "DisallowedClaim": "mid_depth_measurement_validation",
            "ClaimBoundary": "memory_active_claim_audit_no_measurement_validation",
        },
        {
            "AuditID": "HIGH_DEPTH_MEMORY_ACTIVE",
            "ClaimScope": "high_depth",
            "Finding": "A2 is strongest in the high-depth blocked split, matching the finite-memory expectation.",
            "Evidence": (
                f"BlockedHighDepthA2Wins={high['A2Wins']}/{high['Rows']}; "
                f"BlockedHighDepthDeltaChi2={high['DeltaChi2_A2_minus_Poly']}"
            ),
            "AllowedClaim": "memory_active_preflight_support_high_depth",
            "DisallowedClaim": "high_depth_measurement_validation",
            "ClaimBoundary": "memory_active_claim_audit_no_measurement_validation",
        },
        {
            "AuditID": "CLAIM_SELECTION",
            "ClaimScope": "registered_claim_boundary",
            "Finding": "The defensible claim is memory-active preflight support, not all-depth validation.",
            "Evidence": "Public-proxy in-sample polynomial control remains a blocker; blocked/depth and reconstruction-scatter checks favor A2 in the memory-active regime.",
            "AllowedClaim": "A2 is a locked memory-active preflight candidate",
            "DisallowedClaim": "A2 is measured or validated on cosmological data",
            "ClaimBoundary": "memory_active_claim_audit_no_measurement_validation",
        },
    ]

    pd.DataFrame(rows).to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "K2_A2_MEMORY_ACTIVE_CLAIM_SUMMARY",
                "AllDepthValidationAllowed": False,
                "MemoryActivePreflightClaimAllowed": True,
                "LowDepthTensionAcknowledged": True,
                "PolynomialControlStillBlocksMeasurementValidation": True,
                "RecommendedPaperLanguage": "locked memory-active preflight candidate; not measurement validation",
                "NextAction": "run likelihood-native SN/BAO transform benchmark and keep low-depth rows as anchor/tension diagnostics",
                "ClaimBoundary": "memory_active_claim_audit_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
