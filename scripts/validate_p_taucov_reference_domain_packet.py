#!/usr/bin/env python3
"""Validate the concrete P-TauCov reference-domain packet."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "data/p_taucov/linear/coordinate_basis.csv"
PHI0 = ROOT / "data/p_taucov/linear/phi_0.csv"
P_NULL = ROOT / "data/p_taucov/linear/p_null.csv"
P_GAUGE = ROOT / "data/p_taucov/linear/p_gauge.csv"
P_FORBIDDEN = ROOT / "data/p_taucov/linear/p_forbidden.csv"
P_RED = ROOT / "data/p_taucov/linear/p_red.csv"
MANIFEST = ROOT / "evidence/p_taucov_reference_domain_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_reference_domain.sha256"
SUMMARY = ROOT / "evidence/p_taucov_reference_domain_packet_summary.csv"
DOC = ROOT / "docs/p_taucov_reference_domain_packet.md"
OUT = ROOT / "evidence/p_taucov_reference_domain_packet_validation.csv"

REQUIRED_PATHS = [BASIS, PHI0, P_NULL, P_GAUGE, P_FORBIDDEN, P_RED, MANIFEST, SHA256, SUMMARY, DOC]


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_projector(path: Path, ids: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    expected = ["coordinate_id"] + ids
    if list(df.columns) != expected:
        raise ValueError(f"Unexpected projector columns in {path}")
    return df


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_REFERENCE_DOMAIN_PACKET_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in REQUIRED_PATHS:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if not all(path.exists() for path in REQUIRED_PATHS):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_REFERENCE_DOMAIN_PACKET_BLOCKED_MISSING_FILES")
        return 0

    basis = pd.read_csv(BASIS)
    ids = basis["coordinate_id"].astype(str).tolist()
    add("coordinate_ids_unique", len(ids) == len(set(ids)))

    phi0 = pd.read_csv(PHI0)
    add("phi0_rows_match_basis", set(phi0["coordinate_id"].astype(str)) == set(ids))
    add("phi0_values_match_basis_origin", phi0["phi_0_value"].astype(float).tolist() == basis["origin_value"].astype(float).tolist())

    p_null = read_projector(P_NULL, ids)
    p_gauge = read_projector(P_GAUGE, ids)
    p_forbidden = read_projector(P_FORBIDDEN, ids)
    p_red = read_projector(P_RED, ids)
    add("projector_rows_match_basis", all(list(df["coordinate_id"].astype(str)) == ids for df in [p_null, p_gauge, p_forbidden, p_red]))

    for i, cid in enumerate(ids):
        null_expected = bool(basis.loc[i, "is_null_candidate"])
        gauge_expected = bool(basis.loc[i, "is_gauge_candidate"])
        forbidden_expected = bool(basis.loc[i, "is_forbidden_candidate"])
        retained_expected = not (null_expected or gauge_expected or forbidden_expected)
        add(f"diag_null_{cid}", float(p_null.loc[i, cid]) == (1.0 if null_expected else 0.0))
        add(f"diag_gauge_{cid}", float(p_gauge.loc[i, cid]) == (1.0 if gauge_expected else 0.0))
        add(f"diag_forbidden_{cid}", float(p_forbidden.loc[i, cid]) == (1.0 if forbidden_expected else 0.0))
        add(f"diag_red_{cid}", float(p_red.loc[i, cid]) == (1.0 if retained_expected else 0.0))

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    add("manifest_reference_frozen", manifest.get("ReferenceStateFrozen") is True)
    add("manifest_domain_frozen", manifest.get("ReducedDomainFrozen") is True)
    add("manifest_no_linear_packet", manifest.get("LinearPacketAuthorized") is False)
    add("manifest_no_metric_eval", manifest.get("MetricEvaluationAuthorized") is False)
    add("manifest_no_scoring", manifest.get("PTauCovScoringAuthorized") is False)
    add("manifest_no_outcome", manifest.get("OutcomeInformationUsed") is False)
    add("manifest_no_residual", manifest.get("ResidualInformationUsed") is False)
    add("manifest_no_score", manifest.get("ScoreInformationUsed") is False)

    hash_lines = [line.strip().split(maxsplit=1) for line in SHA256.read_text(encoding="utf-8").splitlines() if line.strip()]
    hash_map = {path: digest for digest, path in hash_lines}
    for path in [PHI0, P_NULL, P_GAUGE, P_FORBIDDEN, P_RED]:
        rel = str(path.relative_to(ROOT))
        add(f"sha256_{rel}", hash_map.get(rel) == file_sha256(path))

    summary = pd.read_csv(SUMMARY)
    add("summary_reference_frozen", bool(summary["ReferenceStateFrozen"].iloc[0]))
    add("summary_domain_frozen", bool(summary["ReducedDomainFrozen"].iloc[0]))
    add("summary_no_scoring", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))

    text = DOC.read_text(encoding="utf-8")
    for phrase in [
        "reference state and reduced-domain projector",
        "P_red",
        "no covariance response",
        "The P-TauCov reference state and reduced domain are frozen",
        "P-TauCov score are available",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_REFERENCE_DOMAIN_PACKET_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_REFERENCE_DOMAIN_PACKET_VALID_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
