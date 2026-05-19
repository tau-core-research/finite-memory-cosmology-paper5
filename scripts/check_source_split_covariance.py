#!/usr/bin/env python3
"""Check source-split joint covariance readiness."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.source_split_covariance import (
    load_source_split_covariance_registry,
    source_split_covariance_allowed,
    source_split_covariance_issues,
)

REGISTRY = ROOT / "evidence" / "source_split_covariance_registry.csv"
SIGN_FAMILY = ROOT / "evidence" / "sign_family_export_readiness.csv"
OUT = ROOT / "evidence" / "source_split_covariance_readiness.csv"


def sign_family_allowed() -> bool:
    if not SIGN_FAMILY.exists():
        return False
    sign_family = pd.read_csv(SIGN_FAMILY)
    rows = sign_family[sign_family["SignFamilyID"].eq("SF_PUBLIC_SOURCE_SPLIT_FAMILIES")]
    return not rows.empty and bool(rows.iloc[0]["AllowedForK2Scoring"])


def main() -> None:
    registry = load_source_split_covariance_registry(REGISTRY)
    if sign_family_allowed():
        mask = registry["CovarianceID"].eq("SSCOV_SHRINKAGE_SOURCE_SPLIT")
        registry.loc[mask, "AllowedForK2Scoring"] = True
        registry.loc[mask, "BlockingIssue"] = ""
        registry.loc[mask, "NextAction"] = (
            "Use as declared shrinkage covariance for source-split preflight scorecard; replace with public full covariance when available."
        )
    rows = []
    for _, row in registry.iterrows():
        issues = source_split_covariance_issues(row)
        rows.append(
            {
                "CovarianceID": row["CovarianceID"],
                "TargetSpace": row["TargetSpace"],
                "Status": row["Status"],
                "UsesPublicSN": row["UsesPublicSN"],
                "UsesPublicBAO": row["UsesPublicBAO"],
                "IncludesSNBAOCrossCovariance": row["IncludesSNBAOCrossCovariance"],
                "CoordinateNative": row["CoordinateNative"],
                "K1Compatible": row["K1Compatible"],
                "AllowedForK2Scoring": source_split_covariance_allowed(row),
                "BlockingIssue": ";".join(issues),
                "NextAction": row["NextAction"],
            }
        )
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
