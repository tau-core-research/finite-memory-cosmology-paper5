#!/usr/bin/env python3
"""Build final manifest for parent-action P-TauCov scorecard authorization."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "parent_action_packet": ROOT / "evidence/p_taucov_candidate_full_parent_action_packet_summary.csv",
    "scorecard_script_freeze": ROOT / "evidence/p_taucov_parent_action_scorecard_script_freeze_summary.csv",
    "fold_policy": ROOT / "evidence/p_taucov_parent_action_fold_policy_summary.csv",
    "null_comparators": ROOT / "evidence/p_taucov_parent_action_null_comparators_summary.csv",
    "survival_kill_gates": ROOT / "evidence/p_taucov_parent_action_survival_kill_gates_summary.csv",
    "df_covariance_policy": ROOT / "evidence/p_taucov_parent_action_df_covariance_policy_summary.csv",
}
SCORECARD_SCRIPT = ROOT / "scripts/run_p_taucov_parent_action_scorecard.py"
MANIFEST = ROOT / "evidence/p_taucov_parent_action_final_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_parent_action_final_manifest.sha256"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_final_manifest_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_final_manifest.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
MANIFEST_ID = "P_TAUCOV_PARENT_ACTION_FINAL_MANIFEST_v1"
CLAIM_BOUNDARY = "parent_action_final_manifest_primary_scorecard_only_no_survival_claim"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def status(path: Path) -> str:
    return str(pd.read_csv(path).iloc[0]["Status"])


def main() -> int:
    missing = [key for key, path in INPUTS.items() if not path.exists()]
    script_exists = SCORECARD_SCRIPT.exists()
    expected = {
        "parent_action_packet": "P_TAUCOV_CANDIDATE_FULL_PARENT_ACTION_PACKET_PASS_NO_SCORING",
        "scorecard_script_freeze": "P_TAUCOV_PARENT_ACTION_SCORECARD_SCRIPT_FROZEN_NO_SCORING",
        "fold_policy": "P_TAUCOV_PARENT_ACTION_FOLD_POLICY_FROZEN_NO_SCORING",
        "null_comparators": "P_TAUCOV_PARENT_ACTION_NULL_COMPARATORS_FROZEN_NO_SCORING",
        "survival_kill_gates": "P_TAUCOV_PARENT_ACTION_SURVIVAL_KILL_GATES_FROZEN_NO_SCORING",
        "df_covariance_policy": "P_TAUCOV_PARENT_ACTION_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING",
    }
    statuses = {key: status(path) for key, path in INPUTS.items() if path.exists()}
    all_statuses_ok = all(statuses.get(key) == value for key, value in expected.items())
    authorizable = not missing and script_exists and all_statuses_ok
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "ManifestID": MANIFEST_ID,
        "Status": "P_TAUCOV_PARENT_ACTION_PRIMARY_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM" if authorizable else "P_TAUCOV_PARENT_ACTION_FINAL_MANIFEST_BLOCKED",
        "PTauCovScoringAuthorized": bool(authorizable),
        "AuthorizedScope": "parent_action_primary_covariance_scorecard_only",
        "AuthorizedScorecard": str(SCORECARD_SCRIPT.relative_to(ROOT)),
        "SurvivalClaimAuthorized": False,
        "MeasurementValidationAuthorized": False,
        "NullSurvivalSuiteAuthorized": False,
        "InputFiles": {key: str(path.relative_to(ROOT)) for key, path in INPUTS.items()},
        "InputStatus": statuses,
        "InputSHA256": {key: sha256(path) for key, path in INPUTS.items() if path.exists()},
        "ScorecardSHA256": sha256(SCORECARD_SCRIPT) if script_exists else "",
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA256.write_text(f"{sha256(MANIFEST)}  {MANIFEST.relative_to(ROOT)}\n", encoding="utf-8")
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "ManifestID": MANIFEST_ID,
                "Status": manifest["Status"],
                "PTauCovScoringAuthorized": bool(authorizable),
                "SurvivalClaimAuthorized": False,
                "MeasurementValidationAuthorized": False,
                "AuthorizedScope": manifest["AuthorizedScope"],
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Parent-Action Final Manifest",
                "",
                f"Status: `{manifest['Status']}`.",
                "",
                f"- scoring authorized: `{bool(authorizable)}`",
                "- survival claim authorized: `False`",
                "- measurement validation authorized: `False`",
                f"- authorized scope: `{manifest['AuthorizedScope']}`",
                "",
                "This manifest authorizes only the primary parent-action covariance",
                "scorecard scope. It does not authorize survival language or a Tau",
                "Core validation claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(manifest["Status"])
    return 0 if authorizable else 1


if __name__ == "__main__":
    raise SystemExit(main())
