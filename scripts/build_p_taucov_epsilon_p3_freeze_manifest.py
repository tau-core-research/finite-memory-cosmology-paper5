#!/usr/bin/env python3
"""Freeze the epsilon-P3 P-TauCov specificity candidate after target-blind pass."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_epsilon_p3_freeze_manifest.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_freeze_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_freeze_manifest.sha256"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_freeze_manifest_summary.csv"
VALIDATION_IN = ROOT / "evidence/p_taucov_epsilon_p3_specificity_prescore_validation.csv"
PRESCORE_SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_specificity_prescore_summary.csv"
PRESCORE = ROOT / "evidence/p_taucov_epsilon_p3_specificity_prescore.csv"
MODEL = ROOT / "evidence/p_taucov_epsilon_p3_model_packet.yaml"
P3_OPERATOR = ROOT / "data/p_taucov/linear/P3_core_mixing_operator.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EPSILON_P3_FREEZE_v1"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bool_from_csv(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def main() -> int:
    DOC.parent.mkdir(exist_ok=True)
    MANIFEST.parent.mkdir(exist_ok=True)
    required = [VALIDATION_IN, PRESCORE_SUMMARY, PRESCORE, MODEL, P3_OPERATOR]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing epsilon-P3 freeze inputs: " + ", ".join(str(p.relative_to(ROOT)) for p in missing))

    validation = pd.read_csv(VALIDATION_IN)
    prescore_summary = pd.read_csv(PRESCORE_SUMMARY)
    prescore = pd.read_csv(PRESCORE)
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8")) or {}

    validation_passed = bool(validation["Passed"].map(bool_from_csv).all())
    prescore_status = str(prescore_summary["Status"].iloc[0])
    all_metrics_passed = bool(prescore["Pass"].map(bool_from_csv).all())
    no_target = not bool(prescore["UsesTargetResiduals"].map(bool_from_csv).any())
    no_p5c = not bool(prescore["UsesP5Cv3Outcome"].map(bool_from_csv).any())
    no_scoring = model.get("PTauCovScoringAuthorized") is False
    freeze_allowed = validation_passed and prescore_status == "PASS_NOT_FROZEN" and all_metrics_passed and no_target and no_p5c and no_scoring

    input_files = {
        "p3_operator": str(P3_OPERATOR.relative_to(ROOT)),
        "model_packet": str(MODEL.relative_to(ROOT)),
        "specificity_prescore": str(PRESCORE.relative_to(ROOT)),
        "specificity_prescore_summary": str(PRESCORE_SUMMARY.relative_to(ROOT)),
        "specificity_prescore_validation": str(VALIDATION_IN.relative_to(ROOT)),
    }
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "FreezeID": FREEZE_ID,
        "FrozenCandidate": "epsilon_P3_core_mixing",
        "FreezeStatus": "FROZEN_SPECIFICITY_CANDIDATE_NO_SCORING" if freeze_allowed else "BLOCKED",
        "CandidateFrozen": bool(freeze_allowed),
        "PrimaryRoute": "epsilon_P_projection_response",
        "ProjectionOperator": "P3_core_mixing_operator",
        "lambda_B": 0,
        "epsilon_P": 1,
        "SpecificityPrescoreStatus": prescore_status,
        "SpecificityMetricsPassed": bool(all_metrics_passed),
        "TargetResidualsUsed": False,
        "P5CV3OutcomeUsed": False,
        "PTauCovScoringAuthorized": False,
        "ScoringAuthorizationArtifactExists": False,
        "AllowedNextStep": "build_scoring_authorization_protocol_only_after_folds_nulls_covariance_df_survival_gates_are_frozen",
        "ForbiddenNextStep": "run_empirical_scoring_or_claim_tau_signal_from_this_freeze",
        "InputFiles": input_files,
        "InputSHA256": {key: file_sha256(ROOT / rel) for key, rel in input_files.items()},
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": "epsilon_p3_specificity_candidate_frozen_no_empirical_scoring_no_tau_signal_claim",
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA256.write_text(f"{file_sha256(MANIFEST)}  {MANIFEST.relative_to(ROOT)}\n", encoding="utf-8")

    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "FreezeStatus": manifest["FreezeStatus"],
                "CandidateFrozen": manifest["CandidateFrozen"],
                "SpecificityPrescoreStatus": prescore_status,
                "MetricsPassed": "6/6" if all_metrics_passed else f"{int(prescore['Pass'].map(bool_from_csv).sum())}/6",
                "PTauCovScoringAuthorized": False,
                "NextStep": manifest["AllowedNextStep"],
                "ClaimBoundary": manifest["ClaimBoundary"],
            }
        ]
    ).to_csv(SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Epsilon-P3 Freeze Manifest

Status: `{'FROZEN_SPECIFICITY_CANDIDATE_NO_SCORING' if freeze_allowed else 'BLOCKED'}`.

This manifest freezes the target-blind epsilon-P3 candidate after the
specificity prescore passed all six structural gates.

## Frozen Candidate

```text
Route: epsilon_P projection response
Operator: P3 core-mixing
lambda_B = 0
epsilon_P = 1
T_tau = A_Phi + A_B L0_B^+ R_B + epsilon_P P3
delta_C_tau = T_tau T_tau^T
```

## Specificity Result

```text
SpecificityPrescoreStatus: {prescore_status}
MetricsPassed: {'6/6' if all_metrics_passed else 'not_all_passed'}
TargetResidualsUsed: false
P5CV3OutcomeUsed: false
PTauCovScoringAuthorized: false
```

## Claim Boundary

Allowed statement:

```text
The epsilon-P3 candidate is frozen as a target-blind P-TauCov specificity
candidate.
```

Forbidden statement:

```text
The epsilon-P3 candidate has produced an empirical P-TauCov score, survival
result, or Tau-specific observational signal.
```

The next step may only be a separate scoring-authorization protocol that freezes
folds, nulls, covariance policy, degrees-of-freedom policy, and survival/kill
criteria before any empirical scoring is run.
""",
        encoding="utf-8",
    )

    for path in [DOC, MANIFEST, SHA256, SUMMARY]:
        print(f"Wrote {path}")
    if not freeze_allowed:
        print("P_TAUCOV_EPSILON_P3_FREEZE_BLOCKED")
        return 1
    print("P_TAUCOV_EPSILON_P3_FREEZE_FROZEN_SPECIFICITY_CANDIDATE_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
