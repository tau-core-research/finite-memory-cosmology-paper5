#!/usr/bin/env python3
"""Validate the frozen P5C v3 scoring-mode decision."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "evidence/p5c_kernel_v3_scoring_mode_freeze.csv"
MANIFEST = ROOT / "evidence/p5c_kernel_v3_scoring_mode_freeze.yaml"
OUT = ROOT / "evidence/p5c_kernel_v3_scoring_mode_validation.csv"

REQUIRED_PRIMARY = "PSD_COVARIANCE_DEFORMATION"
REQUIRED_SECONDARY = "SIGNED_OPERATOR_CONTRAST_DIAGNOSTIC_ONLY"
REQUIRED_STATUS = "SCORING_MODE_FREEZE_READY"


def main() -> int:
    if not FREEZE.exists():
        raise FileNotFoundError(FREEZE)
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)
    row = pd.read_csv(FREEZE).iloc[0]
    checks = [
        ("freeze_exists", True, True),
        ("manifest_exists", True, True),
        ("status_freeze_ready", row["Status"] == REQUIRED_STATUS, True),
        ("primary_psd_covariance", row["PrimaryScoringMode"] == REQUIRED_PRIMARY, True),
        ("secondary_signed_diagnostic_only", row["SecondaryMode"] == REQUIRED_SECONDARY, True),
        ("scoring_not_authorized_here", bool(row["ScoringAuthorizedByThisArtifact"]) is False, True),
        ("target_residual_not_used", bool(row["TargetResidualUsed"]) is False, True),
        ("score_not_used", bool(row["ScoreUsed"]) is False, True),
        ("psd_orientation_retention_gate", float(row["PSDOrientationRetention"]) >= 0.60, True),
        ("psd_random_smooth_gate", float(row["PSDRandomSmoothMedianAbsCorrelation"]) <= 0.60, True),
        ("psd_diagonal_gate", float(row["PSDDiagonalEnergyShare"]) <= 0.10, True),
        ("psd_family_block_gate", float(row["PSDMaxFamilyBlockEnergyShare"]) <= 0.20, True),
        ("psd_family_gain_gate", float(row["PSDMaxFamilyGainCapacity"]) <= 0.40, True),
    ]
    records = []
    for check_id, passed, required in checks:
        records.append(
            {
                "AuditID": "P5C_KERNEL_V3_SCORING_MODE_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )
    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P5C_KERNEL_V3_SCORING_MODE_INVALID")
        print(failed.to_string(index=False))
        return 1
    print("P5C_KERNEL_V3_SCORING_MODE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
