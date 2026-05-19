#!/usr/bin/env python3
"""Check scoring-grade reconstruction-family source readiness."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.reconstruction_family import (
    load_reconstruction_family_registry,
    reconstruction_family_allowed,
    reconstruction_family_issues,
)

REGISTRY = ROOT / "evidence" / "source_split_reconstruction_family_source_registry.csv"
VALIDATION = ROOT / "evidence" / "source_split_reconstruction_family_export_validation.csv"
PROMOTION = ROOT / "evidence" / "source_split_sign_rule_promotion_readiness.csv"
OUT = ROOT / "evidence" / "source_split_reconstruction_family_source_readiness.csv"


def validation_clean() -> bool:
    if not VALIDATION.exists():
        return False
    validation = pd.read_csv(VALIDATION)
    return not validation.empty and bool(validation.iloc[0]["AllowedForK2Scoring"])


def sign_rule_declared() -> bool:
    if not PROMOTION.exists():
        return False
    promotion = pd.read_csv(PROMOTION)
    rows = promotion[promotion["CheckID"].eq("SRP5_RULE_PROMOTION_AUTHORIZED")]
    return not rows.empty and bool(rows.iloc[0].get("AllowedForK2Scoring", False))


def main() -> None:
    registry = load_reconstruction_family_registry(REGISTRY)
    if validation_clean() and sign_rule_declared():
        mask = registry["FamilySourceID"].eq("RF_PUBLIC_SOURCE_SPLIT_RECONSTRUCTION_FAMILIES")
        registry.loc[mask, "Status"] = "available"
        registry.loc[mask, "RowAlignedToTarget"] = True
        registry.loc[mask, "FamilyResponseExported"] = True
        registry.loc[mask, "FamilySignRuleDeclared"] = True
        registry.loc[mask, "AllowedForK2Scoring"] = True
        registry.loc[mask, "BlockingIssue"] = ""
        registry.loc[mask, "NextAction"] = (
            "Use as reconstruction-family source input only after remaining K1 and covariance gates are resolved."
        )
    rows = []
    for _, row in registry.iterrows():
        issues = reconstruction_family_issues(row)
        rows.append(
            {
                "FamilySourceID": row["FamilySourceID"],
                "TargetSpace": row["TargetSpace"],
                "Status": row["Status"],
                "UsesPublicSN": row["UsesPublicSN"],
                "UsesPublicBAO": row["UsesPublicBAO"],
                "CoordinateNative": row["CoordinateNative"],
                "RowAlignedToTarget": row["RowAlignedToTarget"],
                "FamilyResponseExported": row["FamilyResponseExported"],
                "FamilySignRuleDeclared": row["FamilySignRuleDeclared"],
                "AllowedForK2Scoring": reconstruction_family_allowed(row),
                "BlockingIssue": ";".join(issues),
                "NextAction": row["NextAction"],
            }
        )
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
