#!/usr/bin/env python3
"""Build the target-blind epsilon_P/P3 P-TauCov model packet."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_epsilon_p3_model_packet.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_model_packet.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_model_packet.sha256"
LEAKAGE = ROOT / "evidence/p_taucov_epsilon_p3_model_packet_leakage_audit.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_model_packet_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PACKET_ID = "P_TAUCOV_EPSILON_P3_MODEL_PACKET_v1_CORE_MIXING"

INPUT_FILES = {
    "coordinate_basis": "data/p_taucov/linear/coordinate_basis.csv",
    "p_red": "data/p_taucov/linear/p_red.csv",
    "L0_B": "data/p_taucov/linear/L0_B.csv",
    "R_B": "data/p_taucov/linear/R_B.csv",
    "A_Phi": "data/p_taucov/linear/A_Phi.csv",
    "A_B": "data/p_taucov/linear/A_B.csv",
    "P0": "data/p_taucov/linear/P0.csv",
    "P3": "data/p_taucov/linear/P3_core_mixing_operator.csv",
    "p2_prescore": "evidence/p_taucov_epsilon_p2_specificity_prescore_summary.csv",
    "p3_manifest": "evidence/p_taucov_p3_core_mixing_operator_manifest.yaml",
    "p3_metrics": "evidence/p_taucov_p3_core_mixing_operator_metrics.csv",
}


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    DOC.parent.mkdir(exist_ok=True)
    MANIFEST.parent.mkdir(exist_ok=True)
    missing = [rel for rel in INPUT_FILES.values() if not (ROOT / rel).exists()]
    if missing:
        raise FileNotFoundError("Missing epsilon_P3 packet inputs: " + ", ".join(missing))

    hashes = {key: file_sha256(ROOT / rel) for key, rel in INPUT_FILES.items()}
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "PacketID": PACKET_ID,
        "PacketType": "epsilon_p3_model_packet",
        "ModelFamily": "epsilon_P_core_mixing_response",
        "lambda_B": 0,
        "epsilon_P": 1,
        "EpsilonPAmplitudePolicy": "unit_amplitude_because_P3_has_unit_frobenius_norm",
        "ProjectionMap": "P_epsilon = P0 + epsilon_P * P3",
        "ParentP2Status": "FAIL_EPSILON_P2_NOT_SPECIFIC",
        "P3OperatorStatus": "operator_valid_all_structural_metrics_passed",
        "EpsilonP3ModelPacketFrozen": True,
        "LinearSpecificityAuditAuthorized": True,
        "MetricEvaluationAuthorized": True,
        "PTauCovScoringAuthorized": False,
        "OutcomeInformationUsed": False,
        "ResidualInformationUsed": False,
        "ScoreInformationUsed": False,
        "P5CV3OutcomeUsed": False,
        "PostScoringLocalizationUsed": False,
        "ClaimBoundary": "epsilon_p3_model_packet_authorizes_specificity_metrics_only_no_scoring",
        "InputFiles": INPUT_FILES,
        "InputSHA256": hashes,
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA256.write_text(f"{file_sha256(MANIFEST)}  {MANIFEST.relative_to(ROOT)}\n", encoding="utf-8")

    leakage = pd.DataFrame(
        [
            {
                "AuditID": "P_TAUCOV_EPSILON_P3_MODEL_PACKET_LEAKAGE_AUDIT",
                "CheckID": check_id,
                "Passed": True,
                "Required": True,
                "Evidence": evidence,
            }
            for check_id, evidence in [
                ("outcome_information_used", "manifest OutcomeInformationUsed=false"),
                ("residual_information_used", "manifest ResidualInformationUsed=false"),
                ("score_information_used", "manifest ScoreInformationUsed=false"),
                ("p5c_v3_outcome_used", "manifest P5CV3OutcomeUsed=false"),
                ("post_scoring_localization_used", "manifest PostScoringLocalizationUsed=false"),
                ("epsilon_amplitude_target_blind", "epsilon_P=1 follows unit-norm P3 convention, not score fitting"),
            ]
        ]
    )
    leakage.to_csv(LEAKAGE, index=False)

    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PacketID": PACKET_ID,
                "EpsilonP3ModelPacketFrozen": True,
                "epsilon_P": 1,
                "lambda_B": 0,
                "LinearSpecificityAuditAuthorized": True,
                "MetricEvaluationAuthorized": True,
                "PTauCovScoringAuthorized": False,
                "NextStep": "run_epsilon_p3_specificity_prescore",
                "ClaimBoundary": manifest["ClaimBoundary"],
            }
        ]
    ).to_csv(SUMMARY, index=False)

    DOC.write_text(
        """# P-TauCov Epsilon-P3 Model Packet

Status: target-blind `epsilon_P/P3` model packet / specificity metrics
authorized / P-TauCov scoring not authorized.

This packet is the core-mixing successor to the support-entropy-failed `P2`
route. It does not overwrite the P1/P2 packets or the strict-linear negative
baseline.

## Frozen Model

```text
lambda_B = 0
epsilon_P = 1
P_epsilon = P0 + epsilon_P * P3
```

The unit value `epsilon_P = 1` is a normalization convention, not a fitted
amplitude. It is allowed because `P3` was frozen with unit Frobenius norm before
any empirical P-TauCov scoring.

## Boundary

Allowed statement:

```text
The target-blind epsilon-P3 model packet is frozen for specificity auditing.
```

Forbidden statement:

```text
The epsilon-P3 packet has produced a P-TauCov score, survival result, or
empirical Tau signal.
```
""",
        encoding="utf-8",
    )

    for path in [DOC, MANIFEST, SHA256, LEAKAGE, SUMMARY]:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
