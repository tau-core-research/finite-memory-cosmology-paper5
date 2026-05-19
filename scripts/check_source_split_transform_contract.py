#!/usr/bin/env python3
"""Check the SN+BAO/source-split transform contract."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.source_split import (
    load_source_split_registry,
    source_split_allowed,
    source_split_issues,
)

REGISTRY = ROOT / "evidence" / "source_split_transform_registry.csv"
K1 = ROOT / "evidence" / "source_split_k1_target_readiness.csv"
COVARIANCE = ROOT / "evidence" / "source_split_covariance_readiness.csv"
SIGN_FAMILY = ROOT / "evidence" / "sign_family_export_readiness.csv"
OUT = ROOT / "evidence" / "source_split_transform_readiness.csv"


def gate_allowed(path: Path, id_column: str, target_id: str) -> bool:
    if not path.exists():
        return False
    df = pd.read_csv(path)
    rows = df[df[id_column].eq(target_id)]
    return not rows.empty and bool(rows.iloc[0]["AllowedForK2Scoring"])


def main() -> None:
    registry = load_source_split_registry(REGISTRY)
    k1_allowed = gate_allowed(K1, "TargetID", "SSK1_COORDINATE_NATIVE_SOURCE_SPLIT_TARGET")
    covariance_allowed = gate_allowed(COVARIANCE, "CovarianceID", "SSCOV_SHRINKAGE_SOURCE_SPLIT")
    sign_family_allowed = gate_allowed(SIGN_FAMILY, "SignFamilyID", "SF_PUBLIC_SOURCE_SPLIT_FAMILIES")
    if k1_allowed and covariance_allowed and sign_family_allowed:
        mask = registry["TransformID"].eq("SST3_PUBLIC_SN_BAO_SOURCE_SPLIT")
        registry.loc[mask, "K1TargetExported"] = True
        registry.loc[mask, "SignFamilyExported"] = True
        registry.loc[mask, "AllowedForK2Scoring"] = True
        registry.loc[mask, "BlockingIssue"] = ""
        registry.loc[mask, "NextAction"] = "Use as coordinate-native source-split transform for preflight K2/null scorecard."
    rows = []
    for _, row in registry.iterrows():
        issues = source_split_issues(row)
        rows.append(
            {
                "TransformID": row["TransformID"],
                "OutputTarget": row["OutputTarget"],
                "Status": row["Status"],
                "UsesPublicSN": row["UsesPublicSN"],
                "UsesPublicBAO": row["UsesPublicBAO"],
                "UsesCovariance": row["UsesCovariance"],
                "CoordinateNative": row["CoordinateNative"],
                "K1TargetExported": row["K1TargetExported"],
                "SignFamilyExported": row["SignFamilyExported"],
                "AllowedForK2Scoring": source_split_allowed(row),
                "BlockingIssue": ";".join(issues),
                "NextAction": row["NextAction"],
            }
        )

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
