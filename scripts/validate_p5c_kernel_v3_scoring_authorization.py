#!/usr/bin/env python3
"""Validate the P5C v3 final scoring authorization manifest."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence/p5c_kernel_v3_final_manifest.yaml"
AUTH = ROOT / "evidence/p5c_kernel_v3_scoring_authorization.csv"
SHA = ROOT / "evidence/p5c_kernel_v3_final_manifest.sha256"
OUT = ROOT / "evidence/p5c_kernel_v3_scoring_authorization_validation.csv"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_hashes(manifest: dict) -> bool:
    for rel_name, expected in manifest["hashes"].items():
        # Names are keys, not paths. Reconstruct through the builder's known file map.
        pass
    return True


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P5C_KERNEL_V3_SCORING_AUTHORIZATION_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("manifest_exists", MANIFEST.exists())
    add("authorization_csv_exists", AUTH.exists())
    add("sha_exists", SHA.exists())
    if not MANIFEST.exists() or not AUTH.exists() or not SHA.exists():
        out = pd.DataFrame(records)
        out.to_csv(OUT, index=False)
        print("P5C_KERNEL_V3_SCORING_AUTHORIZATION_INVALID")
        return 1

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    auth = pd.read_csv(AUTH).iloc[0]
    sha_line = SHA.read_text(encoding="utf-8").strip().split()[0]

    add("manifest_hash_matches_sha_file", file_sha256(MANIFEST) == sha_line)
    add("status_authorized", manifest["status"] == "P5C_KERNEL_V3_SCORING_AUTHORIZED")
    add("csv_status_authorized", auth["Status"] == "P5C_KERNEL_V3_SCORING_AUTHORIZED")
    add("primary_is_psd", manifest["primary"]["mode"] == "PSD_COVARIANCE_DEFORMATION")
    add("diagnostic_is_signed_only", manifest["diagnostic"]["mode"] == "SIGNED_OPERATOR_CONTRAST_DIAGNOSTIC_ONLY")
    add("diagnostic_survival_forbidden", bool(manifest["diagnostic"]["survival_claim_allowed"]) is False)
    add("csv_secondary_promotion_forbidden", bool(auth["SecondaryPromotionAllowed"]) is False)
    add("mode_switch_forbidden", bool(auth["PrimaryModeSwitchAfterScoringAllowed"]) is False)
    add("target_residual_not_used", bool(auth["TargetResidualUsedInFreeze"]) is False)
    add("score_not_used", bool(auth["ScoreUsedInFreeze"]) is False)
    add("kernel_freeze_valid", bool(auth["KernelFreezeValid"]) is True)
    add("scoring_mode_freeze_valid", bool(auth["ScoringModeFreezeValid"]) is True)
    add("folds_unchanged", bool(auth["FoldsUnchanged"]) is True)
    add("nulls_unchanged", bool(auth["NullsUnchanged"]) is True)
    add("covariance_policy_unchanged", bool(auth["CovariancePolicyUnchanged"]) is True)
    add("df_policy_unchanged", bool(auth["DFPolicyUnchanged"]) is True)
    add("survival_kill_gates_unchanged", bool(auth["SurvivalKillGatesUnchanged"]) is True)

    # Validate that every hashed file still exists and has the frozen digest.
    required_paths = {
        "kernel_manifest": ROOT / "evidence/p5c_bstar_kernel_v3_manifest.yaml",
        "kernel_summary": ROOT / "evidence/p5c_bstar_kernel_v3_summary.csv",
        "primary_psd_kernel": ROOT / "evidence/p5c_bstar_kernel_v3_psd_projection.csv",
        "diagnostic_signed_kernel": ROOT / "evidence/p5c_bstar_kernel_v3_signed_orientation.csv",
        "null_kernels": ROOT / "evidence/p5c_bstar_kernel_v3_null_kernels.csv",
        "kernel_sha256": ROOT / "evidence/p5c_bstar_kernel_v3.sha256",
        "scoring_mode_freeze": ROOT / "evidence/p5c_kernel_v3_scoring_mode_freeze.csv",
        "scoring_mode_manifest": ROOT / "evidence/p5c_kernel_v3_scoring_mode_freeze.yaml",
        "scoring_mode_validation": ROOT / "evidence/p5c_kernel_v3_scoring_mode_validation.csv",
        "fold_design": ROOT / "evidence/backreaction_36_fold_design.csv",
        "null_comparators": ROOT / "evidence/backreaction_36_null_comparators.csv",
        "covariance_treatment": ROOT / "evidence/backreaction_36_covariance_treatment.csv",
        "df_policy": ROOT / "evidence/backreaction_36_df_policy.csv",
        "survival_gates": ROOT / "evidence/backreaction_36_survival_gates.csv",
        "kill_conditions": ROOT / "evidence/backreaction_36_kill_conditions.csv",
        "scorecard_script": ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v3.py",
        "base_scorecard_script": ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py",
        "build_kernel_script": ROOT / "scripts/build_p5c_bstar_kernel_v3.py",
        "freeze_scoring_mode_script": ROOT / "scripts/freeze_p5c_kernel_v3_scoring_mode.py",
    }
    for key, path in required_paths.items():
        add(f"hash_file_exists_{key}", path.exists())
        if path.exists():
            add(f"hash_matches_{key}", file_sha256(path) == manifest["hashes"][key])

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P5C_KERNEL_V3_SCORING_AUTHORIZATION_INVALID")
        print(failed.to_string(index=False))
        return 1
    print("P5C_KERNEL_V3_SCORING_AUTHORIZATION_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
