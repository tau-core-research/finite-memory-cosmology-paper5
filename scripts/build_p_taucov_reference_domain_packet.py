#!/usr/bin/env python3
"""Build the concrete P-TauCov reference-domain packet from the frozen basis."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "data/p_taucov/linear/coordinate_basis.csv"
OUT_DIR = ROOT / "data/p_taucov/linear"
EVIDENCE = ROOT / "evidence"
DOC = ROOT / "docs/p_taucov_reference_domain_packet.md"

PHI0 = OUT_DIR / "phi_0.csv"
P_NULL = OUT_DIR / "p_null.csv"
P_GAUGE = OUT_DIR / "p_gauge.csv"
P_FORBIDDEN = OUT_DIR / "p_forbidden.csv"
P_RED = OUT_DIR / "p_red.csv"
MANIFEST = EVIDENCE / "p_taucov_reference_domain_manifest.yaml"
SHA256 = EVIDENCE / "p_taucov_reference_domain.sha256"
VALIDATION_SUMMARY = EVIDENCE / "p_taucov_reference_domain_packet_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PACKET_ID = "P_TAUCOV_REFERENCE_DOMAIN_PACKET_v1_MINIMAL_BASIS_PROJECTORS"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def diagonal_projector(ids: list[str], selected: set[str]) -> pd.DataFrame:
    rows = []
    for row_id in ids:
        row = {"coordinate_id": row_id}
        for col_id in ids:
            row[col_id] = 1.0 if row_id == col_id and row_id in selected else 0.0
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> int:
    if not BASIS.exists():
        raise FileNotFoundError(f"Missing coordinate basis: {BASIS}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    DOC.parent.mkdir(exist_ok=True)

    basis = pd.read_csv(BASIS)
    ids = basis["coordinate_id"].astype(str).tolist()
    if len(ids) != len(set(ids)):
        raise ValueError("coordinate_id values must be unique")

    null_ids = set(basis.loc[basis["is_null_candidate"].astype(bool), "coordinate_id"].astype(str))
    gauge_ids = set(basis.loc[basis["is_gauge_candidate"].astype(bool), "coordinate_id"].astype(str))
    forbidden_ids = set(basis.loc[basis["is_forbidden_candidate"].astype(bool), "coordinate_id"].astype(str))
    excluded_ids = null_ids | gauge_ids | forbidden_ids
    retained_ids = set(ids) - excluded_ids

    phi0 = basis[["coordinate_id", "basis_axis", "origin_value"]].copy()
    phi0.rename(columns={"origin_value": "phi_0_value"}, inplace=True)
    phi0.to_csv(PHI0, index=False)

    diagonal_projector(ids, null_ids).to_csv(P_NULL, index=False)
    diagonal_projector(ids, gauge_ids).to_csv(P_GAUGE, index=False)
    diagonal_projector(ids, forbidden_ids).to_csv(P_FORBIDDEN, index=False)
    diagonal_projector(ids, retained_ids).to_csv(P_RED, index=False)

    packet_files = [PHI0, P_NULL, P_GAUGE, P_FORBIDDEN, P_RED]
    hashes = {str(path.relative_to(ROOT)): file_sha256(path) for path in packet_files}
    SHA256.write_text("\n".join(f"{digest}  {path}" for path, digest in hashes.items()) + "\n", encoding="utf-8")

    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "PacketID": PACKET_ID,
        "PacketType": "reference_domain",
        "ReferenceStateFrozen": True,
        "ReducedDomainFrozen": True,
        "CoordinateBasisFile": str(BASIS.relative_to(ROOT)),
        "Phi0File": str(PHI0.relative_to(ROOT)),
        "PNullFile": str(P_NULL.relative_to(ROOT)),
        "PGaugeFile": str(P_GAUGE.relative_to(ROOT)),
        "PForbiddenFile": str(P_FORBIDDEN.relative_to(ROOT)),
        "PRedFile": str(P_RED.relative_to(ROOT)),
        "CoordinateCount": len(ids),
        "NullExcludedCount": len(null_ids),
        "GaugeExcludedCount": len(gauge_ids),
        "ForbiddenExcludedCount": len(forbidden_ids),
        "RetainedCount": len(retained_ids),
        "LinearPacketAuthorized": False,
        "MetricEvaluationAuthorized": False,
        "PTauCovScoringAuthorized": False,
        "OutcomeInformationUsed": False,
        "ResidualInformationUsed": False,
        "ScoreInformationUsed": False,
        "PostScoringLocalizationUsed": False,
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": "reference_domain_frozen_no_linear_matrices_no_scores",
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PacketID": PACKET_ID,
                "CoordinateCount": len(ids),
                "ReferenceStateFrozen": True,
                "ReducedDomainFrozen": True,
                "NullExcludedCount": len(null_ids),
                "GaugeExcludedCount": len(gauge_ids),
                "ForbiddenExcludedCount": len(forbidden_ids),
                "RetainedCount": len(retained_ids),
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": "reference_domain_frozen_no_linear_matrices_no_scores",
            }
        ]
    )
    summary.to_csv(VALIDATION_SUMMARY, index=False)

    DOC.write_text(
        """# P-TauCov Reference-Domain Packet

Status: concrete reference state and reduced-domain projector / no linear
matrices / no covariance response / no metric evaluation / no scoring
authorization.

This packet applies the target-blind reference-domain selection rule to the
frozen coordinate basis. `Phi_0` is the frozen coordinate-basis origin vector.
`P_null`, `P_gauge`, and `P_forbidden` are diagonal exclusion projectors built
from predeclared basis flags. `P_red` retains only the non-excluded coordinates.

## Files

```text
data/p_taucov/linear/phi_0.csv
data/p_taucov/linear/p_null.csv
data/p_taucov/linear/p_gauge.csv
data/p_taucov/linear/p_forbidden.csv
data/p_taucov/linear/p_red.csv
evidence/p_taucov_reference_domain_manifest.yaml
evidence/p_taucov_reference_domain.sha256
```

## Claim Boundary

Allowed statement:

```text
The P-TauCov reference state and reduced domain are frozen.
```

Forbidden statement:

```text
The Tau-side linear matrices, covariance response, specificity metrics, or
P-TauCov score are available.
```
""",
        encoding="utf-8",
    )

    for path in packet_files + [MANIFEST, SHA256, VALIDATION_SUMMARY, DOC]:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
