#!/usr/bin/env python3
"""Build final authorization manifest for PB zero-diagonal scorecard."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

INPUTS = {
    "object_manifest": EVIDENCE / "p_taucov_pb_zero_diagonal_object_manifest.csv",
    "object_validation": EVIDENCE / "p_taucov_pb_zero_diagonal_object_validation.csv",
    "scorecard_script_freeze": EVIDENCE / "p_taucov_pb_zero_diagonal_scorecard_script_freeze_summary.csv",
    "fold_policy": EVIDENCE / "p_taucov_pb_zero_diagonal_fold_policy_summary.csv",
    "null_comparators": EVIDENCE / "p_taucov_pb_zero_diagonal_null_comparators_summary.csv",
    "df_covariance_policy": EVIDENCE / "p_taucov_pb_zero_diagonal_df_covariance_policy_summary.csv",
    "survival_kill_gates": EVIDENCE / "p_taucov_pb_zero_diagonal_survival_kill_gates_summary.csv",
    "scoring_firewall": EVIDENCE / "p_taucov_pb_zero_diagonal_scoring_firewall_summary.csv",
}
REQUIRED = {
    "object_matrix": EVIDENCE / "p_taucov_pb_zero_diagonal_object_matrix.csv",
    "scorecard_script": ROOT / "scripts/run_p_taucov_pb_zero_diagonal_scorecard.py",
}

MANIFEST = EVIDENCE / "p_taucov_pb_zero_diagonal_final_manifest.yaml"
SHA256 = EVIDENCE / "p_taucov_pb_zero_diagonal_final_manifest.sha256"
SUMMARY = EVIDENCE / "p_taucov_pb_zero_diagonal_final_manifest_summary.csv"
DOC = DOCS / "p_taucov_pb_zero_diagonal_final_manifest.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
MANIFEST_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_FINAL_MANIFEST_v1"
CLAIM_BOUNDARY = "pb_zero_diagonal_final_manifest_primary_scorecard_only_no_survival_claim"

EXPECTED = {
    "object_manifest": "P_TAUCOV_PB_ZERO_DIAGONAL_OBJECT_FROZEN_NO_SCORING",
    "scorecard_script_freeze": "P_TAUCOV_PB_ZERO_DIAGONAL_SCORECARD_SCRIPT_FROZEN_NO_SCORING",
    "fold_policy": "P_TAUCOV_PB_ZERO_DIAGONAL_FOLD_POLICY_FROZEN_NO_SCORING",
    "null_comparators": "P_TAUCOV_PB_ZERO_DIAGONAL_NULL_COMPARATORS_FROZEN_NO_SCORING",
    "df_covariance_policy": "P_TAUCOV_PB_ZERO_DIAGONAL_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING",
    "survival_kill_gates": "P_TAUCOV_PB_ZERO_DIAGONAL_SURVIVAL_KILL_GATES_FROZEN_NO_SCORING",
    "scoring_firewall": "P_TAUCOV_PB_ZERO_DIAGONAL_SCORING_AUTHORIZATION_READY",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def status(path: Path) -> str:
    return str(pd.read_csv(path).iloc[0]["Status"])


def validation_passes(path: Path) -> bool:
    if not path.exists():
        return False
    df = pd.read_csv(path)
    return bool(df.loc[df["Required"], "Passed"].all())


def main() -> int:
    missing_inputs = [key for key, path in INPUTS.items() if not path.exists()]
    missing_required = [key for key, path in REQUIRED.items() if not path.exists()]
    statuses = {
        key: status(path)
        for key, path in INPUTS.items()
        if path.exists() and key != "object_validation"
    }
    all_statuses_ok = all(statuses.get(key) == expected for key, expected in EXPECTED.items())
    validation_ok = validation_passes(INPUTS["object_validation"])
    authorizable = not missing_inputs and not missing_required and all_statuses_ok and validation_ok
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "ManifestID": MANIFEST_ID,
        "Status": "P_TAUCOV_PB_ZERO_DIAGONAL_PRIMARY_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM" if authorizable else "P_TAUCOV_PB_ZERO_DIAGONAL_FINAL_MANIFEST_BLOCKED",
        "PTauCovScoringAuthorized": bool(authorizable),
        "AuthorizedScope": "pb_zero_diagonal_primary_covariance_scorecard_only",
        "AuthorizedScorecard": str(REQUIRED["scorecard_script"].relative_to(ROOT)),
        "SurvivalClaimAuthorized": False,
        "MeasurementValidationAuthorized": False,
        "TauCoreValidationClaimAuthorized": False,
        "NullSurvivalSuiteAuthorized": False,
        "InputFiles": {key: str(path.relative_to(ROOT)) for key, path in INPUTS.items()},
        "RequiredFiles": {key: str(path.relative_to(ROOT)) for key, path in REQUIRED.items()},
        "InputStatus": statuses,
        "ObjectValidationPasses": bool(validation_ok),
        "InputSHA256": {key: sha256(path) for key, path in INPUTS.items() if path.exists()},
        "RequiredSHA256": {key: sha256(path) for key, path in REQUIRED.items() if path.exists()},
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
        "\n".join(
            [
                "# P-TauCov PB Zero-Diagonal Final Manifest",
                "",
                f"Status: `{manifest['Status']}`.",
                "",
                f"- scoring authorized: `{bool(authorizable)}`",
                "- survival claim authorized: `False`",
                "- measurement validation authorized: `False`",
                "- Tau Core validation claim authorized: `False`",
                f"- authorized scope: `{manifest['AuthorizedScope']}`",
                "",
                "This manifest authorizes only the PB zero-diagonal primary covariance",
                "scorecard entrypoint. It does not authorize survival language, null-",
                "survival language, measurement validation, or a Tau Core validation claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(manifest["Status"])
    return 0 if authorizable else 1


if __name__ == "__main__":
    raise SystemExit(main())
