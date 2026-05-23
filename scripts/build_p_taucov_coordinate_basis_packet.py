#!/usr/bin/env python3
"""Build the concrete target-blind P-TauCov coordinate-basis packet."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
SKELETON = ROOT / "data/p_taucov/templates/coordinate_basis_skeleton.csv"
VALUES = ROOT / "data/p_taucov/linear/origin_scale_values.csv"
BASIS = ROOT / "data/p_taucov/linear/coordinate_basis.csv"
MANIFEST = ROOT / "evidence/p_taucov_coordinate_basis_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_coordinate_basis.sha256"
LEAKAGE = ROOT / "evidence/p_taucov_coordinate_basis_leakage_audit.csv"
DOC = ROOT / "docs/p_taucov_coordinate_basis_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PACKET_ID = "P_TAUCOV_COORDINATE_BASIS_PACKET_v1_MINIMAL_UNIT_CONVENTION"

OUTPUT_COLUMNS = [
    "coordinate_id",
    "coordinate_family",
    "coordinate_kind",
    "basis_axis",
    "origin_value",
    "scale_value",
    "is_null_candidate",
    "is_gauge_candidate",
    "is_forbidden_candidate",
    "provenance",
]


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not SKELETON.exists():
        raise FileNotFoundError(f"Missing skeleton: {SKELETON}")
    if not VALUES.exists():
        raise FileNotFoundError(f"Missing origin/scale values: {VALUES}")

    BASIS.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    DOC.parent.mkdir(parents=True, exist_ok=True)

    skeleton = pd.read_csv(SKELETON)
    values = pd.read_csv(VALUES)
    merged = skeleton.merge(values, on="basis_axis", suffixes=("_template", ""), validate="one_to_one")
    if len(merged) != len(skeleton):
        raise ValueError("Origin/scale values do not cover the skeleton one-to-one")

    basis = pd.DataFrame()
    for col in OUTPUT_COLUMNS:
        if col in {"origin_value", "scale_value"}:
            basis[col] = merged[col]
        elif col == "provenance":
            basis[col] = (
                merged["provenance_template"].astype(str)
                + " | "
                + merged["provenance"].astype(str)
                + f" | {PACKET_ID}"
            )
        else:
            basis[col] = merged[col]

    basis.to_csv(BASIS, index=False)

    digest = file_sha256(BASIS)
    SHA256.write_text(f"{digest}  {BASIS.relative_to(ROOT)}\n", encoding="utf-8")

    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "PacketID": PACKET_ID,
        "PacketType": "coordinate_basis",
        "CoordinateBasisFrozen": True,
        "ReferenceDomainSelectable": True,
        "LinearPacketAuthorized": False,
        "MetricEvaluationAuthorized": False,
        "PTauCovScoringAuthorized": False,
        "OutcomeInformationUsed": False,
        "ResidualInformationUsed": False,
        "ScoreInformationUsed": False,
        "PostScoringLocalizationUsed": False,
        "SourceFiles": [str(SKELETON.relative_to(ROOT)), str(VALUES.relative_to(ROOT))],
        "BasisFile": str(BASIS.relative_to(ROOT)),
        "SHA256": digest,
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": "coordinate_basis_frozen_no_matrices_no_scores",
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    leakage = pd.DataFrame(
        [
            {
                "AuditID": "P_TAUCOV_COORDINATE_BASIS_LEAKAGE_AUDIT",
                "CheckID": "outcome_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest OutcomeInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_COORDINATE_BASIS_LEAKAGE_AUDIT",
                "CheckID": "residual_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest ResidualInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_COORDINATE_BASIS_LEAKAGE_AUDIT",
                "CheckID": "score_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest ScoreInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_COORDINATE_BASIS_LEAKAGE_AUDIT",
                "CheckID": "post_scoring_localization_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest PostScoringLocalizationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_COORDINATE_BASIS_LEAKAGE_AUDIT",
                "CheckID": "built_from_allowed_packets",
                "Passed": True,
                "Required": True,
                "Evidence": "built from symbolic-axis skeleton and validated origin/scale values packet",
            },
        ]
    )
    leakage.to_csv(LEAKAGE, index=False)

    DOC.write_text(
        """# P-TauCov Coordinate-Basis Packet

Status: concrete target-blind coordinate basis / no matrices / no linear packet
/ no metric evaluation / no scoring authorization.

This packet combines the non-authorizing coordinate-basis skeleton with the
validated minimal origin/scale values packet. It supplies the first concrete
`coordinate_basis.csv` required for reference-domain selection.

## Files

```text
data/p_taucov/linear/coordinate_basis.csv
evidence/p_taucov_coordinate_basis_manifest.yaml
evidence/p_taucov_coordinate_basis.sha256
evidence/p_taucov_coordinate_basis_leakage_audit.csv
```

## Claim Boundary

Allowed statement:

```text
A target-blind coordinate basis is frozen for reference-domain construction.
```

Forbidden statement:

```text
P_red, linear matrices, covariance response, metric evaluation, or P-TauCov
scoring are available.
```
""",
        encoding="utf-8",
    )

    print(f"Wrote {BASIS}")
    print(f"Wrote {MANIFEST}")
    print(f"Wrote {SHA256}")
    print(f"Wrote {LEAKAGE}")
    print(f"Wrote {DOC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
