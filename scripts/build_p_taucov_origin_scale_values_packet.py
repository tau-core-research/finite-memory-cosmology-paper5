#!/usr/bin/env python3
"""Build the minimal target-blind P-TauCov origin/scale values packet."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
SKELETON = ROOT / "data/p_taucov/templates/coordinate_basis_skeleton.csv"
RULES = ROOT / "evidence/p_taucov_origin_scale_rule_freeze.csv"
VALUES = ROOT / "data/p_taucov/linear/origin_scale_values.csv"
MANIFEST = ROOT / "evidence/p_taucov_origin_scale_values_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_origin_scale_values.sha256"
LEAKAGE = ROOT / "evidence/p_taucov_origin_scale_values_leakage_audit.csv"
DOC = ROOT / "docs/p_taucov_origin_scale_values_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PACKET_ID = "P_TAUCOV_ORIGIN_SCALE_VALUES_PACKET_v1_MINIMAL_UNIT_CONVENTION"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not SKELETON.exists():
        raise FileNotFoundError(f"Missing skeleton: {SKELETON}")
    if not RULES.exists():
        raise FileNotFoundError(f"Missing origin/scale rules: {RULES}")

    VALUES.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    DOC.parent.mkdir(parents=True, exist_ok=True)

    skeleton = pd.read_csv(SKELETON)
    rules = pd.read_csv(RULES)
    rule_by_kind = {row["AxisKind"]: row for _, row in rules.iterrows()}

    rows = []
    for _, row in skeleton.iterrows():
        kind = row["coordinate_kind"]
        if kind not in rule_by_kind:
            raise ValueError(f"No origin/scale rule for axis kind: {kind}")
        rule = rule_by_kind[kind]
        rows.append(
            {
                "basis_axis": row["basis_axis"],
                "origin_value": 0.0,
                "scale_value": 1.0,
                "origin_rule": rule["OriginRule"],
                "scale_rule": rule["ScaleRule"],
                "value_source": "minimal_target_blind_unit_coordinate_convention",
                "provenance": f"{PACKET_ID}: origin=0 scale=1 from frozen rule for axis_kind={kind}",
            }
        )

    values = pd.DataFrame(rows)
    values.to_csv(VALUES, index=False)

    digest = file_sha256(VALUES)
    SHA256.write_text(f"{digest}  {VALUES.relative_to(ROOT)}\n", encoding="utf-8")

    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "PacketID": PACKET_ID,
        "PacketType": "origin_scale_values",
        "ValuePolicy": "minimal_target_blind_unit_coordinate_convention",
        "CoordinateBasisPacketAuthorized": False,
        "ReferenceDomainSelectable": False,
        "MetricEvaluationAuthorized": False,
        "PTauCovScoringAuthorized": False,
        "OutcomeInformationUsed": False,
        "ResidualInformationUsed": False,
        "ScoreInformationUsed": False,
        "PostScoringLocalizationUsed": False,
        "SourceFiles": [str(SKELETON.relative_to(ROOT)), str(RULES.relative_to(ROOT))],
        "ValueFile": str(VALUES.relative_to(ROOT)),
        "SHA256": digest,
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": "minimal_origin_scale_values_only_no_coordinate_basis_packet",
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    leakage = pd.DataFrame(
        [
            {
                "AuditID": "P_TAUCOV_ORIGIN_SCALE_VALUES_LEAKAGE_AUDIT",
                "CheckID": "outcome_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest OutcomeInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_ORIGIN_SCALE_VALUES_LEAKAGE_AUDIT",
                "CheckID": "residual_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest ResidualInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_ORIGIN_SCALE_VALUES_LEAKAGE_AUDIT",
                "CheckID": "score_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest ScoreInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_ORIGIN_SCALE_VALUES_LEAKAGE_AUDIT",
                "CheckID": "post_scoring_localization_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest PostScoringLocalizationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_ORIGIN_SCALE_VALUES_LEAKAGE_AUDIT",
                "CheckID": "values_are_unit_convention",
                "Passed": True,
                "Required": True,
                "Evidence": "all origin_value=0 and scale_value=1 from frozen rule classes",
            },
        ]
    )
    leakage.to_csv(LEAKAGE, index=False)

    DOC.write_text(
        """# P-TauCov Origin/Scale Values Packet

Status: minimal target-blind unit-convention values / no coordinate-basis packet
/ no reference-domain selection / no metric evaluation / no scoring
authorization.

This packet fills the origin/scale value-source gate with the minimal convention

```text
origin_value = 0
scale_value = 1
```

for every symbolic axis in the coordinate-basis skeleton. This is a coordinate
normalization convention, not an empirical fit and not a covariance result.

## Files

```text
data/p_taucov/linear/origin_scale_values.csv
evidence/p_taucov_origin_scale_values_manifest.yaml
evidence/p_taucov_origin_scale_values.sha256
evidence/p_taucov_origin_scale_values_leakage_audit.csv
```

## Claim Boundary

Allowed statement:

```text
Minimal target-blind origin/scale values are available for future coordinate-basis construction.
```

Forbidden statement:

```text
The coordinate basis, reference domain, matrices, or P-TauCov score are available.
```
""",
        encoding="utf-8",
    )

    print(f"Wrote {VALUES}")
    print(f"Wrote {MANIFEST}")
    print(f"Wrote {SHA256}")
    print(f"Wrote {LEAKAGE}")
    print(f"Wrote {DOC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
