#!/usr/bin/env python3
"""Build final no-scoring manifest for the P3 balanced P-TauCov object."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "balance_projector_summary": ROOT / "evidence/p_taucov_clock_family_balance_projector_summary.csv",
    "balance_projector_matrix": ROOT / "evidence/p_taucov_clock_family_balance_projector_matrix.csv",
    "balance_projector_validation": ROOT / "evidence/p_taucov_clock_family_balance_projector_validation.csv",
    "p3_operator_manifest": ROOT / "evidence/p_taucov_p3_core_mixing_operator_manifest.yaml",
    "p3_operator_metrics": ROOT / "evidence/p_taucov_p3_core_mixing_operator_metrics.csv",
    "p3_balanced_preflight_matrix": ROOT / "evidence/p_taucov_p3_balanced_preflight_matrix.csv",
    "p3_balanced_preflight_summary": ROOT / "evidence/p_taucov_p3_balanced_preflight_summary.csv",
    "p3_balanced_preflight_validation": ROOT / "evidence/p_taucov_p3_balanced_preflight_validation.csv",
    "p3_balanced_readiness_summary": ROOT / "evidence/p_taucov_p3_balanced_readiness_summary.csv",
    "p3_balanced_readiness_validation": ROOT / "evidence/p_taucov_p3_balanced_readiness_validation.csv",
}
MANIFEST = ROOT / "evidence/p_taucov_p3_balanced_final_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_p3_balanced_final_manifest.sha256"
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_final_manifest_summary.csv"
DOC = ROOT / "docs/p_taucov_p3_balanced_final_manifest.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
MANIFEST_ID = "P_TAUCOV_P3_BALANCED_FINAL_MANIFEST_v1"
STATUS_READY = "P_TAUCOV_P3_BALANCED_OBJECT_FROZEN_NO_SCORING_AUTHORIZATION"
STATUS_BLOCKED = "P_TAUCOV_P3_BALANCED_FINAL_MANIFEST_BLOCKED"
CLAIM_BOUNDARY = "p3_balanced_final_manifest_frozen_object_no_scoring"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    df = pd.read_csv(path)
    return str(df.iloc[0]["Status"]) if "Status" in df.columns else "NO_STATUS_COLUMN"


def validation_pass(path: Path) -> bool:
    if not path.exists():
        return False
    df = pd.read_csv(path)
    return bool(df[df["Required"].astype(bool)]["Passed"].astype(bool).all())


def main() -> int:
    required_statuses = {
        "balance_projector_summary": "P_TAUCOV_BALANCE_PROJECTOR_FROZEN_NO_CANDIDATE_NO_SCORING",
        "p3_balanced_preflight_summary": "P_TAUCOV_P3_BALANCED_PREFLIGHT_READY_NO_CANDIDATE_NO_SCORING",
        "p3_balanced_readiness_summary": "P_TAUCOV_P3_BALANCED_READY_FOR_MANIFEST_NO_SCORING",
    }
    required_validations = [
        "balance_projector_validation",
        "p3_balanced_preflight_validation",
        "p3_balanced_readiness_validation",
    ]
    exists_ok = all(path.exists() for path in INPUTS.values())
    statuses = {key: csv_status(path) for key, path in INPUTS.items() if key.endswith("_summary")}
    status_ok = all(statuses.get(key) == expected for key, expected in required_statuses.items())
    validation_ok = all(validation_pass(INPUTS[key]) for key in required_validations)
    frozen = bool(exists_ok and status_ok and validation_ok)

    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "ManifestID": MANIFEST_ID,
        "Status": STATUS_READY if frozen else STATUS_BLOCKED,
        "FrozenObject": "P3_BALANCED_PREFLIGHT_OFFDIAGONAL_OBJECT",
        "ObjectFrozen": frozen,
        "CandidateConstructed": False,
        "ScoringAuthorized": False,
        "CovarianceSurvivalClaimAuthorized": False,
        "TauCoreValidationClaimAuthorized": False,
        "MeasurementValidationAuthorized": False,
        "AuthorizedScope": "frozen_balanced_object_package_only_no_scoring",
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
                "ObjectFrozen": frozen,
                "CandidateConstructed": False,
                "ScoringAuthorized": False,
                "CovarianceSurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "MeasurementValidationAuthorized": False,
                "AuthorizedScope": manifest["AuthorizedScope"],
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        f"""# P-TauCov P3 Balanced Final Manifest

Manifest ID: `{MANIFEST_ID}`

Status:

`{manifest["Status"]}`

## Scope

This manifest freezes the balanced P3 preflight object and its supporting
balance-projector/readiness artifacts.

It does not authorize empirical scoring.

## Frozen Object

```text
FrozenObject = {manifest["FrozenObject"]}
AuthorizedScope = {manifest["AuthorizedScope"]}
ObjectFrozen = {frozen}
```

## Claim Boundary

Allowed statement:

> A target-blind, clock/family-balanced P3 parent-side object has been frozen for future protocol work.

Forbidden statement:

> The frozen P3 balanced object has produced a Tau signal, passed empirical scoring, or validated Tau Core.
""",
        encoding="utf-8",
    )
    print(manifest["Status"])
    return 0 if frozen else 1


if __name__ == "__main__":
    raise SystemExit(main())
