#!/usr/bin/env python3
"""Audit the common-mode baseline behind A2 projection gating.

The goal is to decide whether same-sign SN/BAO rows can safely remain in K1,
or whether they expose a source-coherent residual that must be handled by a
future coordinate-native baseline. This script does not change A2, does not
fit K1, and does not use target signs to define a new prediction.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
META = EVIDENCE / "source_split_coordinate_native_target.csv"
V3 = EVIDENCE / "a2_projection_gated_v3_candidate_prediction.csv"
MECH = EVIDENCE / "a2_v3_residual_mechanism_audit.csv"

OUT_AUDIT = EVIDENCE / "a2_common_mode_baseline_audit.csv"
OUT_SUMMARY = EVIDENCE / "a2_common_mode_baseline_summary.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def sign(value: float) -> int:
    if abs(value) < 1e-12:
        return 0
    return 1 if value > 0 else -1


def safe_ratio(num: float, den: float) -> float:
    if abs(den) < 1e-12:
        return float("nan")
    return float(num / den)


def classify(row: pd.Series) -> tuple[str, str, str]:
    same = truthy(row["SNBAOSameSign"])
    stable = truthy(row["SignStableTemplate"])
    target = float(row["SourceSplitCandidate"])
    branch_contrast = float(row["CoordinateNativeBranchContrast"])
    common_mean = float(row["CoordinateNativeCommonModeMean"])
    k1 = float(row["K1Response"])
    projection_state = str(row["ProjectionState"])

    if not same:
        return (
            "NOT_COMMON_MODE_ROW",
            "SN and BAO branch signs are anti-coherent; this is not the common-mode blocker",
            "keep in source-split memory-active / sign-stability audits",
        )

    if projection_state == "K1_NULL_SUPPRESSED":
        return (
            "COMMON_MODE_WITH_K1_NULL_DEGENERACY",
            "same-sign branches coincide with a near-null K1 baseline, so A2 has no independent sign source",
            "resolve through independent K1/source-branch export, not common-mode amplification",
        )

    target_conflict = sign(target) != sign(branch_contrast) and abs(target) > 1.0 and abs(branch_contrast) > 0.1
    target_scale_gap = abs(target) > 2.0 * max(abs(branch_contrast), abs(common_mean), 1e-12)
    k1_misaligned = sign(k1) != sign(target) and abs(target) > 1.0

    if stable and target_conflict and k1_misaligned:
        return (
            "COMMON_MODE_TARGET_BASELINE_CONFLICT",
            "same-sign stable branch row has rerun target opposite to coordinate-native contrast and K1 is misaligned",
            "do not activate A2; freeze a coordinate-native common-mode/K1 baseline before rerun",
        )

    if stable and target_scale_gap:
        return (
            "COMMON_MODE_TARGET_SCALE_GAP",
            "same-sign stable branch row has a rerun target much larger than public branch contrast/common mean",
            "audit residual-policy normalization before interpreting A2 weakness",
        )

    if k1_misaligned:
        return (
            "COMMON_MODE_K1_MISALIGNMENT",
            "same-sign branch row is baseline-misaligned but not enough to identify a target convention conflict",
            "audit K1 export and common-mode subtraction policy",
        )

    return (
        "COMMON_MODE_BASELINE_CONSERVATIVE",
        "same-sign branch row does not justify memory activation under current public metadata",
        "keep K1 baseline treatment until coordinate-native baseline is available",
    )


def main() -> None:
    vector = pd.read_csv(VECTOR)
    meta = pd.read_csv(META)
    v3 = pd.read_csv(V3)
    mech = pd.read_csv(MECH)[["GridIndex", "MechanismClass", "V3Chi2Contribution", "DeltaChi2_V3_minus_K1"]]

    data = (
        vector.merge(
            meta[
                [
                    "GridIndex",
                    "SNStandardizedResidual",
                    "BAOStandardizedResidual",
                    "SourceSplitResponse",
                    "SignStableTemplate",
                    "SNBAOSameSign",
                    "CoordinateNative",
                    "TransformStatus",
                ]
            ],
            on="GridIndex",
            how="left",
        )
        .merge(
            v3[
                [
                    "GridIndex",
                    "ProjectionState",
                    "A2ProjectionGatedV3Prediction",
                    "ProjectionMultiplier",
                    "RuleReason",
                ]
            ],
            on="GridIndex",
            how="left",
        )
        .merge(mech, on="GridIndex", how="left")
        .sort_values("GridIndex")
    )

    rows = []
    for _, row in data.iterrows():
        sn = float(row["SNStandardizedResidual"]) if pd.notna(row["SNStandardizedResidual"]) else float("nan")
        bao = float(row["BAOStandardizedResidual"]) if pd.notna(row["BAOStandardizedResidual"]) else float("nan")
        contrast = sn - bao if np.isfinite(sn) and np.isfinite(bao) else float("nan")
        common_mean = 0.5 * (sn + bao) if np.isfinite(sn) and np.isfinite(bao) else float("nan")
        row = row.copy()
        row["CoordinateNativeBranchContrast"] = contrast
        row["CoordinateNativeCommonModeMean"] = common_mean
        class_id, interpretation, next_check = classify(row)
        target = float(row["SourceSplitCandidate"])
        k1 = float(row["K1Response"])
        v3_pred = float(row["A2ProjectionGatedV3Prediction"])
        rows.append(
            {
                "AuditID": "A2_COMMON_MODE_BASELINE_AUDIT_V1",
                "GridIndex": int(row["GridIndex"]),
                "z_grid": row["z_grid"],
                "x_coordinate": row["x_coordinate"],
                "ProjectionState": row["ProjectionState"],
                "CommonModeClass": class_id,
                "SourceSplitCandidate": target,
                "CoordinateNativeBranchContrast": contrast,
                "CoordinateNativeCommonModeMean": common_mean,
                "SNStandardizedResidual": sn,
                "BAOStandardizedResidual": bao,
                "K1Response": k1,
                "A2ProjectionGatedV3Prediction": v3_pred,
                "ProjectionMultiplier": row["ProjectionMultiplier"],
                "SignStableTemplate": row["SignStableTemplate"],
                "SNBAOSameSign": row["SNBAOSameSign"],
                "TargetSign": sign(target),
                "BranchContrastSign": sign(contrast),
                "CommonModeSign": sign(common_mean),
                "K1Sign": sign(k1),
                "V3Sign": sign(v3_pred),
                "AbsTargetToBranchContrastRatio": safe_ratio(abs(target), abs(contrast)),
                "AbsTargetToCommonModeRatio": safe_ratio(abs(target), abs(common_mean)),
                "K1TargetSignMismatch": sign(k1) != sign(target) and abs(target) > 1e-12 and abs(k1) > 1e-12,
                "TargetBranchContrastSignMismatch": sign(target) != sign(contrast)
                and abs(target) > 1e-12
                and abs(contrast) > 1e-12,
                "MechanismClass": row["MechanismClass"],
                "V3Chi2Contribution": row["V3Chi2Contribution"],
                "DeltaChi2_V3_minus_K1": row["DeltaChi2_V3_minus_K1"],
                "Interpretation": interpretation,
                "RequiredNextCheck": next_check,
                "AllowedToPromoteCommonModeA2": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_common_mode_baseline_audit_no_measurement_validation",
            }
        )

    audit = pd.DataFrame(rows)
    audit.to_csv(OUT_AUDIT, index=False)

    common = audit[audit["SNBAOSameSign"].astype(str).str.lower().isin(["true", "1", "yes"])].copy()
    stable_common = common[common["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"])]
    blocker_rows = common[
        common["CommonModeClass"].isin(
            [
                "COMMON_MODE_TARGET_BASELINE_CONFLICT",
                "COMMON_MODE_TARGET_SCALE_GAP",
                "COMMON_MODE_K1_MISALIGNMENT",
                "COMMON_MODE_WITH_K1_NULL_DEGENERACY",
            ]
        )
    ]
    grid_list = ";".join(str(int(x)) for x in blocker_rows["GridIndex"].to_list())
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "A2_COMMON_MODE_BASELINE_AUDIT_SUMMARY",
                "Rows": len(audit),
                "CommonModeRows": len(common),
                "StableCommonModeRows": len(stable_common),
                "CommonModeBlockerRows": len(blocker_rows),
                "CommonModeBlockerGridIndices": grid_list,
                "PrimaryBlockerClass": blocker_rows["CommonModeClass"].iloc[0]
                if not blocker_rows.empty
                else "NONE",
                "Grid2Class": audit.loc[audit["GridIndex"].eq(2), "CommonModeClass"].iloc[0]
                if bool(audit["GridIndex"].eq(2).any())
                else "MISSING",
                "Grid2TargetBranchContrastSignMismatch": bool(
                    audit.loc[audit["GridIndex"].eq(2), "TargetBranchContrastSignMismatch"].iloc[0]
                )
                if bool(audit["GridIndex"].eq(2).any())
                else False,
                "Grid2K1TargetSignMismatch": bool(audit.loc[audit["GridIndex"].eq(2), "K1TargetSignMismatch"].iloc[0])
                if bool(audit["GridIndex"].eq(2).any())
                else False,
                "AllowedToPromoteCommonModeA2": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "COMMON_MODE_BASELINE_BLOCKED_REQUIRES_COORDINATE_NATIVE_K1"
                    if not blocker_rows.empty
                    else "COMMON_MODE_BASELINE_CONSERVATIVE_OK"
                ),
                "StrongestAllowedClaim": "common-mode rows expose a baseline/target-definition blocker for A2 interpretation",
                "RequiredNextCheck": "freeze coordinate-native common-mode baseline and independent K1/source-branch export before any A2 rerun",
                "ClaimBoundary": "a2_common_mode_baseline_audit_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
