#!/usr/bin/env python3
"""Check sign-family export readiness."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.sign_family import load_sign_family_registry, sign_family_allowed, sign_family_issues

REGISTRY = ROOT / "evidence" / "sign_family_export_registry.csv"
SOURCE_READINESS = ROOT / "evidence" / "source_split_reconstruction_family_source_readiness.csv"
OUT = ROOT / "evidence" / "sign_family_export_readiness.csv"


def reconstruction_family_source_allowed() -> bool:
    if not SOURCE_READINESS.exists():
        return False
    readiness = pd.read_csv(SOURCE_READINESS)
    rows = readiness[readiness["FamilySourceID"].eq("RF_PUBLIC_SOURCE_SPLIT_RECONSTRUCTION_FAMILIES")]
    return not rows.empty and bool(rows.iloc[0]["AllowedForK2Scoring"])


def main() -> None:
    registry = load_sign_family_registry(REGISTRY)
    if reconstruction_family_source_allowed():
        mask = registry["SignFamilyID"].eq("SF_PUBLIC_SOURCE_SPLIT_FAMILIES")
        registry.loc[mask, "ReconstructionFamilies"] = "RFAM_SN_RESIDUAL_BRANCH;RFAM_BAO_RESIDUAL_BRANCH"
        registry.loc[mask, "SignStableRule"] = "stable if all nonzero reconstruction-family response signs agree"
        registry.loc[mask, "AllowedForK2Scoring"] = True
        registry.loc[mask, "BlockingIssue"] = ""
        registry.loc[mask, "NextAction"] = "Use with explicit warning rows; do not treat warnings as support."
    rows = []
    for _, row in registry.iterrows():
        issues = sign_family_issues(row)
        rows.append(
            {
                "SignFamilyID": row["SignFamilyID"],
                "TargetSpace": row["TargetSpace"],
                "Status": row["Status"],
                "UsesPublicSN": row["UsesPublicSN"],
                "UsesPublicBAO": row["UsesPublicBAO"],
                "CoordinateNative": row["CoordinateNative"],
                "ReconstructionFamilies": row["ReconstructionFamilies"],
                "SignStableRule": row["SignStableRule"],
                "AllowedForK2Scoring": sign_family_allowed(row),
                "BlockingIssue": ";".join(issues),
                "NextAction": row["NextAction"],
            }
        )
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
