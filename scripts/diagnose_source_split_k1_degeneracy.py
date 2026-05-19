#!/usr/bin/env python3
"""Diagnose why multiplicative K2 degenerates on the source-split K1 target."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
K1 = EVIDENCE / "source_split_k1_coordinate_native_target.csv"
SIGN = EVIDENCE / "source_split_family_sign_rule_preview.csv"
OUT = EVIDENCE / "source_split_k1_degeneracy_audit.csv"
SUMMARY = EVIDENCE / "source_split_k1_degeneracy_summary.csv"


def main() -> None:
    target = pd.read_csv(TARGET)
    k1 = pd.read_csv(K1)
    sign = pd.read_csv(SIGN)

    usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    merged = usable.merge(
        k1[
            [
                "GridIndex",
                "K1NoMemoryResponse",
                "NoMemoryDefinition",
                "AmplitudePolicy",
                "SameDataAmplitudeFit",
            ]
        ],
        on="GridIndex",
        how="left",
        validate="one_to_one",
    ).merge(
        sign[["GridIndex", "FamilySignStable", "FamilySignStatus", "FamilySigns"]],
        on="GridIndex",
        how="left",
        validate="one_to_one",
    )

    rows = []
    for _, row in merged.iterrows():
        x = float(row["x_coordinate"])
        w3 = 1.0 + 3.0 * x**3
        w4 = 1.0 + 4.0 * x**3
        k1_value = float(row["K1NoMemoryResponse"])
        target_value = float(row["SourceSplitResponse"])
        k2_rho3 = w3 * k1_value
        k2_rho4 = w4 * k1_value
        finite_memory_leverage = k2_rho4 - k1_value
        rows.append(
            {
                "AuditID": "SOURCE_SPLIT_K1_DEGENERACY_AUDIT_V1",
                "GridIndex": int(row["GridIndex"]),
                "z_grid": float(row["z_grid"]),
                "x_coordinate": x,
                "W_rho3": w3,
                "W_rho4": w4,
                "K1NoMemoryResponse": k1_value,
                "K2Rho3Response": k2_rho3,
                "K2Rho4Response": k2_rho4,
                "FiniteMemoryLeverageRho4": finite_memory_leverage,
                "SourceSplitResponse": target_value,
                "ResidualVsK1": target_value - k1_value,
                "ResidualVsK2Rho4": target_value - k2_rho4,
                "K2EqualsK1": bool(np.isclose(k2_rho4, k1_value)),
                "K2CanSeparateFromNoMemory": not np.isclose(finite_memory_leverage, 0.0),
                "FamilySignStable": bool(row["FamilySignStable"]),
                "FamilySignStatus": row["FamilySignStatus"],
                "FamilySigns": row["FamilySigns"],
                "DegeneracyReason": "zero_k1_makes_multiplicative_k2_zero"
                if np.isclose(k1_value, 0.0)
                else "nonzero_k1_has_leverage",
                "RequiredNextCheck": "derive nonzero coordinate-native K1 response from public reconstruction or move to likelihood-native K1",
                "ClaimBoundary": "degeneracy_audit_only_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)
    leverage = output["FiniteMemoryLeverageRho4"].astype(float).to_numpy()
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_SPLIT_K1_DEGENERACY_AUDIT_V1",
                "Rows": len(output),
                "ZeroK1Rows": int(np.isclose(output["K1NoMemoryResponse"].astype(float), 0.0).sum()),
                "RowsWhereK2EqualsK1": int(output["K2EqualsK1"].sum()),
                "RowsWithFiniteMemoryLeverage": int(output["K2CanSeparateFromNoMemory"].sum()),
                "MaxAbsFiniteMemoryLeverageRho4": float(np.max(np.abs(leverage))) if len(leverage) else np.nan,
                "Conclusion": "multiplicative_k2_degenerate_with_zero_k1",
                "NextAction": "Define an externally derived nonzero K1 response target before treating source-split K2 as a distinct measurement benchmark.",
                "ClaimBoundary": "degeneracy_audit_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
