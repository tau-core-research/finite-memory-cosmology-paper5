#!/usr/bin/env python3
"""Build the final P5C v3 scoring-authorization manifest."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
SCRIPTS = ROOT / "scripts"

OUT_YAML = EVIDENCE / "p5c_kernel_v3_final_manifest.yaml"
OUT_CSV = EVIDENCE / "p5c_kernel_v3_scoring_authorization.csv"
OUT_DOC = DOCS / "p5c_kernel_v3_final_manifest.md"
OUT_SHA = EVIDENCE / "p5c_kernel_v3_final_manifest.sha256"

PROTOCOL_ID = "P5C_BSTAR_COVARIANCE_OPERATOR_KERNEL_PROTOCOL_v1"
AUDIT_ID = "P5C_KERNEL_V3_FINAL_SCORING_AUTHORIZATION"
PRIMARY_KERNEL_ID = "K_BSTAR_P5C_v3_RESIDUAL_COMPLEX_ORIENTATION_PSD_PROJECTION"
DIAGNOSTIC_KERNEL_ID = "K_BSTAR_P5C_v3_RESIDUAL_COMPLEX_ORIENTATION"
STATUS = "P5C_KERNEL_V3_SCORING_AUTHORIZED"
CLAIM_BOUNDARY = "p5c_kernel_v3_final_manifest_authorizes_scoring_not_survival"

REQUIRED_FILES = {
    "kernel_manifest": EVIDENCE / "p5c_bstar_kernel_v3_manifest.yaml",
    "kernel_summary": EVIDENCE / "p5c_bstar_kernel_v3_summary.csv",
    "primary_psd_kernel": EVIDENCE / "p5c_bstar_kernel_v3_psd_projection.csv",
    "diagnostic_signed_kernel": EVIDENCE / "p5c_bstar_kernel_v3_signed_orientation.csv",
    "null_kernels": EVIDENCE / "p5c_bstar_kernel_v3_null_kernels.csv",
    "kernel_sha256": EVIDENCE / "p5c_bstar_kernel_v3.sha256",
    "scoring_mode_freeze": EVIDENCE / "p5c_kernel_v3_scoring_mode_freeze.csv",
    "scoring_mode_manifest": EVIDENCE / "p5c_kernel_v3_scoring_mode_freeze.yaml",
    "scoring_mode_validation": EVIDENCE / "p5c_kernel_v3_scoring_mode_validation.csv",
    "fold_design": EVIDENCE / "backreaction_36_fold_design.csv",
    "null_comparators": EVIDENCE / "backreaction_36_null_comparators.csv",
    "covariance_treatment": EVIDENCE / "backreaction_36_covariance_treatment.csv",
    "df_policy": EVIDENCE / "backreaction_36_df_policy.csv",
    "survival_gates": EVIDENCE / "backreaction_36_survival_gates.csv",
    "kill_conditions": EVIDENCE / "backreaction_36_kill_conditions.csv",
    "scorecard_script": SCRIPTS / "run_p5c_kernel_covariance_scorecard_v3.py",
    "base_scorecard_script": SCRIPTS / "run_p5c_kernel_covariance_scorecard_v0.py",
    "build_kernel_script": SCRIPTS / "build_p5c_bstar_kernel_v3.py",
    "freeze_scoring_mode_script": SCRIPTS / "freeze_p5c_kernel_v3_scoring_mode.py",
}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    missing = [name for name, path in REQUIRED_FILES.items() if not path.exists()]
    require(not missing, f"missing required files: {missing}")

    kernel_manifest = yaml.safe_load(REQUIRED_FILES["kernel_manifest"].read_text(encoding="utf-8"))
    kernel_summary = pd.read_csv(REQUIRED_FILES["kernel_summary"]).iloc[0]
    scoring_mode = pd.read_csv(REQUIRED_FILES["scoring_mode_freeze"]).iloc[0]
    validation = pd.read_csv(REQUIRED_FILES["scoring_mode_validation"])

    require(kernel_manifest["pre_score_status"] == "FREEZE_READY", "kernel pre-score status mismatch")
    require(bool(kernel_manifest["target_residual_used"]) is False, "kernel target residual used")
    require(bool(kernel_manifest["score_used"]) is False, "kernel score used")
    require(bool(kernel_manifest["scoring_authorized_by_this_artifact"]) is False, "kernel freeze self-authorized")
    require(kernel_summary["PreScoreStatus"] == "FREEZE_READY", "kernel summary status mismatch")
    require(bool(kernel_summary["TargetResidualUsed"]) is False, "kernel summary target residual used")
    require(bool(kernel_summary["ScoreUsed"]) is False, "kernel summary score used")

    require(scoring_mode["Status"] == "SCORING_MODE_FREEZE_READY", "scoring mode status mismatch")
    require(scoring_mode["PrimaryScoringMode"] == "PSD_COVARIANCE_DEFORMATION", "primary mode mismatch")
    require(scoring_mode["SecondaryMode"] == "SIGNED_OPERATOR_CONTRAST_DIAGNOSTIC_ONLY", "secondary mode mismatch")
    require(bool(scoring_mode["TargetResidualUsed"]) is False, "scoring-mode target residual used")
    require(bool(scoring_mode["ScoreUsed"]) is False, "scoring-mode score used")
    require(bool(scoring_mode["ScoringAuthorizedByThisArtifact"]) is False, "scoring mode self-authorized")
    require(validation["Status"].eq("PASS").all(), "scoring-mode validation has failures")

    hashes = {name: file_sha256(path) for name, path in REQUIRED_FILES.items()}
    record = {
        "ProtocolID": PROTOCOL_ID,
        "AuditID": AUDIT_ID,
        "Status": STATUS,
        "ScoringAuthorized": True,
        "PrimaryKernelID": PRIMARY_KERNEL_ID,
        "PrimaryMode": "PSD_COVARIANCE_DEFORMATION",
        "DiagnosticKernelID": DIAGNOSTIC_KERNEL_ID,
        "DiagnosticMode": "SIGNED_OPERATOR_CONTRAST_DIAGNOSTIC_ONLY",
        "DiagnosticSurvivalClaimAllowed": False,
        "KernelFreezeValid": True,
        "ScoringModeFreezeValid": True,
        "FoldsUnchanged": True,
        "NullsUnchanged": True,
        "CovariancePolicyUnchanged": True,
        "DFPolicyUnchanged": True,
        "SurvivalKillGatesUnchanged": True,
        "TargetResidualUsedInFreeze": False,
        "ScoreUsedInFreeze": False,
        "PrimaryModeSwitchAfterScoringAllowed": False,
        "SecondaryPromotionAllowed": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    pd.DataFrame([record]).to_csv(OUT_CSV, index=False)
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "audit_id": AUDIT_ID,
        "status": STATUS,
        "scoring_authorized": True,
        "primary": {
            "kernel_id": PRIMARY_KERNEL_ID,
            "mode": "PSD_COVARIANCE_DEFORMATION",
            "survival_claim_allowed": True,
        },
        "diagnostic": {
            "kernel_id": DIAGNOSTIC_KERNEL_ID,
            "mode": "SIGNED_OPERATOR_CONTRAST_DIAGNOSTIC_ONLY",
            "survival_claim_allowed": False,
        },
        "required_conditions": record,
        "hashes": hashes,
        "forbidden": [
            "secondary diagnostic promoted to survival",
            "primary mode switched after scoring",
            "PSD/signed comparison used after scoring to choose the final claim",
            "target residual or score used in kernel/scoring-mode selection",
        ],
        "next_allowed_command": "python3 scripts/run_p5c_kernel_covariance_scorecard_v3.py",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    OUT_YAML.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    OUT_DOC.write_text(
        "\n".join(
            [
                "# P5C Kernel v3 Final Manifest",
                "",
                f"Status: `{STATUS}`",
                "",
                "This manifest authorizes the v3 primary PSD covariance-deformation scorecard.",
                "It does not claim survival and does not contain score results.",
                "",
                "## Primary",
                "",
                f"- kernel: `{PRIMARY_KERNEL_ID}`",
                "- mode: `PSD_COVARIANCE_DEFORMATION`",
                "",
                "## Diagnostic Only",
                "",
                f"- kernel: `{DIAGNOSTIC_KERNEL_ID}`",
                "- mode: `SIGNED_OPERATOR_CONTRAST_DIAGNOSTIC_ONLY`",
                "- survival claim allowed: `false`",
                "",
                "## Authorization",
                "",
                "- kernel freeze valid: `true`",
                "- scoring mode freeze valid: `true`",
                "- folds/nulls/covariance/df/survival/kill policies fixed: `true`",
                "- target residual used in freeze: `false`",
                "- score used in freeze: `false`",
                "",
                "## Forbidden",
                "",
                "- promoting the signed diagnostic to survival;",
                "- switching the primary mode after scoring;",
                "- using PSD/signed comparison after scoring to choose the final claim.",
                "",
                "## Next Allowed Command",
                "",
                "```bash",
                "python3 scripts/run_p5c_kernel_covariance_scorecard_v3.py",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    OUT_SHA.write_text(f"{file_sha256(OUT_YAML)}  {OUT_YAML.name}\n", encoding="utf-8")
    print(STATUS)
    print("next=python3 scripts/run_p5c_kernel_covariance_scorecard_v3.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
