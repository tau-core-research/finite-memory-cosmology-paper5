#!/usr/bin/env python3
"""Build final manifest for expanded parent-operator P-TauCov scorecard."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "expanded_domain": ROOT / "evidence/p_taucov_expanded_parent_operator_domain_summary.csv",
    "expanded_source": ROOT / "evidence/p_taucov_expanded_parent_operator_source_summary.csv",
    "expanded_psd_preflight": ROOT / "evidence/p_taucov_expanded_parent_operator_psd_preflight_summary.csv",
    "scorecard_script_freeze": ROOT / "evidence/p_taucov_expanded_parent_operator_scorecard_script_freeze_summary.csv",
    "fold_policy": ROOT / "evidence/p_taucov_expanded_parent_operator_fold_policy_summary.csv",
    "null_comparators": ROOT / "evidence/p_taucov_expanded_parent_operator_null_comparators_summary.csv",
    "df_covariance_policy": ROOT / "evidence/p_taucov_expanded_parent_operator_df_covariance_policy_summary.csv",
    "survival_kill_gates": ROOT / "evidence/p_taucov_expanded_parent_operator_survival_kill_gates_summary.csv",
    "scoring_firewall": ROOT / "evidence/p_taucov_expanded_parent_operator_scoring_firewall_summary.csv",
}
CANDIDATE = ROOT / "evidence/p_taucov_expanded_parent_operator_psd_candidate.csv"
SOURCE = ROOT / "evidence/p_taucov_expanded_parent_operator_source_matrix.csv"
DOMAIN = ROOT / "evidence/p_taucov_expanded_parent_operator_domain_coordinates.csv"
SCORECARD_SCRIPT = ROOT / "scripts/run_p_taucov_expanded_parent_operator_scorecard.py"

MANIFEST = ROOT / "evidence/p_taucov_expanded_parent_operator_final_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_expanded_parent_operator_final_manifest.sha256"
SUMMARY = ROOT / "evidence/p_taucov_expanded_parent_operator_final_manifest_summary.csv"
DOC = ROOT / "docs/p_taucov_expanded_parent_operator_final_manifest.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
MANIFEST_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_FINAL_MANIFEST_v1"
CLAIM_BOUNDARY = "expanded_parent_operator_final_manifest_primary_scorecard_only_no_survival_claim"

EXPECTED = {
    "expanded_domain": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_DOMAIN_READY_NO_OBJECT_NO_SCORING",
    "expanded_source": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SOURCE_READY_NO_SCORING",
    "expanded_psd_preflight": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PSD_PREFLIGHT_PASS_NO_SCORING",
    "scorecard_script_freeze": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORECARD_SCRIPT_FROZEN_NO_SCORING",
    "fold_policy": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_FOLD_POLICY_FROZEN_NO_SCORING",
    "null_comparators": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_NULL_COMPARATORS_FROZEN_NO_SCORING",
    "df_covariance_policy": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING",
    "survival_kill_gates": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SURVIVAL_KILL_GATES_FROZEN_NO_SCORING",
    "scoring_firewall": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORING_BLOCKED_FREEZE_REQUIRED",
}


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
    required_files = {
        "candidate": CANDIDATE,
        "source_matrix": SOURCE,
        "domain_coordinates": DOMAIN,
        "scorecard_script": SCORECARD_SCRIPT,
    }
    missing_required = [key for key, path in required_files.items() if not path.exists()]
    statuses = {key: status(path) for key, path in INPUTS.items() if path.exists()}
    all_statuses_ok = all(statuses.get(key) == expected for key, expected in EXPECTED.items())
    authorizable = not missing and not missing_required and all_statuses_ok
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "ManifestID": MANIFEST_ID,
        "Status": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PRIMARY_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM" if authorizable else "P_TAUCOV_EXPANDED_PARENT_OPERATOR_FINAL_MANIFEST_BLOCKED",
        "PTauCovScoringAuthorized": bool(authorizable),
        "AuthorizedScope": "expanded_parent_operator_primary_covariance_scorecard_only",
        "AuthorizedScorecard": str(SCORECARD_SCRIPT.relative_to(ROOT)),
        "SurvivalClaimAuthorized": False,
        "MeasurementValidationAuthorized": False,
        "TauCoreValidationClaimAuthorized": False,
        "NullSurvivalSuiteAuthorized": False,
        "InputFiles": {key: str(path.relative_to(ROOT)) for key, path in INPUTS.items()},
        "RequiredFiles": {key: str(path.relative_to(ROOT)) for key, path in required_files.items()},
        "InputStatus": statuses,
        "InputSHA256": {key: sha256(path) for key, path in INPUTS.items() if path.exists()},
        "RequiredSHA256": {key: sha256(path) for key, path in required_files.items() if path.exists()},
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
                "TauCoreValidationClaimAuthorized": False,
                "AuthorizedScope": manifest["AuthorizedScope"],
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        f"""# P-TauCov Expanded Parent-Operator Final Manifest

Status: `{manifest['Status']}`.

- scoring authorized: `{bool(authorizable)}`
- survival claim authorized: `False`
- measurement validation authorized: `False`
- Tau Core validation claim authorized: `False`
- authorized scope: `{manifest['AuthorizedScope']}`

This manifest authorizes only the primary expanded parent-operator covariance
scorecard entrypoint. It does not authorize survival language, null-survival
language, measurement validation, or a Tau Core validation claim.
""",
        encoding="utf-8",
    )
    print(manifest["Status"])
    return 0 if authorizable else 1


if __name__ == "__main__":
    raise SystemExit(main())
