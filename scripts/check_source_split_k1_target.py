#!/usr/bin/env python3
"""Check source-split K1/no-memory target readiness."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.source_split_k1 import (
    load_source_split_k1_registry,
    source_split_k1_allowed,
    source_split_k1_issues,
)

REGISTRY = ROOT / "evidence" / "source_split_k1_target_registry.csv"
COVARIANCE = ROOT / "evidence" / "source_split_covariance_readiness.csv"
SIGN_FAMILY = ROOT / "evidence" / "sign_family_export_readiness.csv"
OUT = ROOT / "evidence" / "source_split_k1_target_readiness.csv"


def covariance_allowed() -> bool:
    if not COVARIANCE.exists():
        return False
    covariance = pd.read_csv(COVARIANCE)
    rows = covariance[covariance["CovarianceID"].eq("SSCOV_SHRINKAGE_SOURCE_SPLIT")]
    return not rows.empty and bool(rows.iloc[0]["AllowedForK2Scoring"])


def sign_family_allowed() -> bool:
    if not SIGN_FAMILY.exists():
        return False
    sign_family = pd.read_csv(SIGN_FAMILY)
    rows = sign_family[sign_family["SignFamilyID"].eq("SF_PUBLIC_SOURCE_SPLIT_FAMILIES")]
    return not rows.empty and bool(rows.iloc[0]["AllowedForK2Scoring"])


def main() -> None:
    registry = load_source_split_k1_registry(REGISTRY)
    if covariance_allowed() and sign_family_allowed():
        mask = registry["TargetID"].eq("SSK1_COORDINATE_NATIVE_SOURCE_SPLIT_TARGET")
        registry.loc[mask, "UsesJointCovariance"] = True
        registry.loc[mask, "SignFamilyExported"] = True
        registry.loc[mask, "AllowedForK2Scoring"] = True
        registry.loc[mask, "BlockingIssue"] = ""
        registry.loc[mask, "NextAction"] = "Use as zero-contrast no-memory K1 target for source-split preflight scorecard."
    rows = []
    for _, row in registry.iterrows():
        issues = source_split_k1_issues(row)
        rows.append(
            {
                "TargetID": row["TargetID"],
                "TargetSpace": row["TargetSpace"],
                "Status": row["Status"],
                "CoordinateNative": row["CoordinateNative"],
                "UsesPublicSN": row["UsesPublicSN"],
                "UsesPublicBAO": row["UsesPublicBAO"],
                "UsesJointCovariance": row["UsesJointCovariance"],
                "AmplitudePolicy": row["AmplitudePolicy"],
                "SameDataAmplitudeFit": row["SameDataAmplitudeFit"],
                "SignFamilyExported": row["SignFamilyExported"],
                "AllowedForK2Scoring": source_split_k1_allowed(row),
                "BlockingIssue": ";".join(issues),
                "NextAction": row["NextAction"],
            }
        )
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
