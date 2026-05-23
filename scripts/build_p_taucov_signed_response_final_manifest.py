#!/usr/bin/env python3
"""Build final manifest for P-TauCov signed-response scorecard scope."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "signed_protocol": ROOT / "evidence/p_taucov_signed_response_protocol_summary.csv",
    "signed_statistic": ROOT / "evidence/p_taucov_signed_response_statistic_summary.csv",
    "signed_null_policy": ROOT / "evidence/p_taucov_signed_response_null_policy_summary.csv",
    "signed_aggregation_policy": ROOT / "evidence/p_taucov_signed_response_aggregation_policy_summary.csv",
    "signed_map": ROOT / "evidence/p_taucov_branch_localized_map_summary.csv",
}
MANIFEST = ROOT / "evidence/p_taucov_signed_response_final_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_signed_response_final_manifest.sha256"
SUMMARY = ROOT / "evidence/p_taucov_signed_response_final_manifest_summary.csv"
DOC = ROOT / "docs/p_taucov_signed_response_final_manifest.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
MANIFEST_ID = "P_TAUCOV_SIGNED_RESPONSE_FINAL_MANIFEST_v1"
CLAIM_BOUNDARY = "signed_response_final_manifest_alignment_scope_no_survival_claim"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def status(path: Path) -> str:
    return str(pd.read_csv(path).iloc[0]["Status"])


def main() -> int:
    expected = {
        "signed_protocol": "P_TAUCOV_SIGNED_RESPONSE_PROTOCOL_FROZEN_READY_FOR_MANIFEST_NO_SCORING",
        "signed_statistic": "P_TAUCOV_SIGNED_RESPONSE_STATISTIC_FROZEN_NO_SCORING",
        "signed_null_policy": "P_TAUCOV_SIGNED_RESPONSE_NULL_POLICY_FROZEN_NO_SCORING",
        "signed_aggregation_policy": "P_TAUCOV_SIGNED_RESPONSE_AGGREGATION_POLICY_FROZEN_NO_SCORING",
        "signed_map": "P_TAUCOV_BRANCH_LOCALIZED_MAP_FROZEN_SIGNED_NO_SCORING",
    }
    missing = [key for key, path in INPUTS.items() if not path.exists()]
    statuses = {key: status(path) for key, path in INPUTS.items() if path.exists()}
    authorizable = not missing and all(statuses.get(key) == value for key, value in expected.items())
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "ManifestID": MANIFEST_ID,
        "Status": "P_TAUCOV_SIGNED_RESPONSE_ALIGNMENT_SCORECARD_AUTHORIZED_NO_SURVIVAL_CLAIM" if authorizable else "P_TAUCOV_SIGNED_RESPONSE_FINAL_MANIFEST_BLOCKED",
        "SignedResponseScoringAuthorized": bool(authorizable),
        "AuthorizedScope": "signed_response_alignment_scorecard_only",
        "CovarianceSurvivalClaimAuthorized": False,
        "TauCoreValidationClaimAuthorized": False,
        "MeasurementValidationAuthorized": False,
        "InputFiles": {key: str(path.relative_to(ROOT)) for key, path in INPUTS.items()},
        "InputStatus": statuses,
        "InputSHA256": {key: sha256(path) for key, path in INPUTS.items() if path.exists()},
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
                "SignedResponseScoringAuthorized": bool(authorizable),
                "CovarianceSurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "MeasurementValidationAuthorized": False,
                "AuthorizedScope": manifest["AuthorizedScope"],
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Signed-Response Final Manifest",
                "",
                f"Status: `{manifest['Status']}`.",
                "",
                f"- signed-response scoring authorized: `{bool(authorizable)}`",
                "- covariance survival claim authorized: `False`",
                "- Tau Core validation claim authorized: `False`",
                "- measurement validation authorized: `False`",
                f"- authorized scope: `{manifest['AuthorizedScope']}`",
                "",
                "This manifest can authorize only the signed alignment scorecard",
                "scope. It does not authorize covariance-survival language.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(manifest["Status"])
    return 0 if authorizable else 1


if __name__ == "__main__":
    raise SystemExit(main())
