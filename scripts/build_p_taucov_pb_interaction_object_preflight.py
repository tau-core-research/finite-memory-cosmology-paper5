#!/usr/bin/env python3
"""Preflight object constructions from the frozen PB interaction coordinate."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PB_INTERACTION_OBJECT_PREFLIGHT_v1"
SOURCE_FREEZE_ID = "P_TAUCOV_PB_INTERACTION_COORDINATE_FREEZE_v1"
CLAIM = "pb_interaction_object_preflight_no_object_freeze_no_scoring"

COORD = EVIDENCE / "p_taucov_pb_interaction_coordinate.csv"
COORD_MANIFEST = EVIDENCE / "p_taucov_pb_interaction_coordinate_manifest.csv"
QCLEAN = EVIDENCE / "p_taucov_domain_compatibility_common_cleaner_matrix.csv"

OUT_OBJECT = EVIDENCE / "p_taucov_pb_interaction_object_preflight_matrix.csv"
OUT_AUDIT = EVIDENCE / "p_taucov_pb_interaction_object_preflight.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_pb_interaction_object_preflight_summary.csv"
OUT_DOC = DOCS / "p_taucov_pb_interaction_object_preflight.md"

SUPPORT_THRESHOLD = 0.20
MAX_FAMILY_SHARE = 0.50
MAX_DIAGONAL_SHARE = 0.10


def load_qclean(target_rows: list[str]) -> np.ndarray:
    df = pd.read_csv(QCLEAN)
    df = df[df["MatrixID"].astype(str).eq("PIBAL_PIPERP_PIBAL")]
    rows = list(dict.fromkeys(df["RowID"].astype(str)))
    idx = {row: i for i, row in enumerate(rows)}
    raw = np.zeros((len(rows), len(rows)), dtype=float)
    for rec in df.to_dict("records"):
        raw[idx[str(rec["RowID"])], idx[str(rec["ColumnID"])]] = float(rec["Value"])
    out = np.zeros((len(target_rows), len(target_rows)), dtype=float)
    for i, row in enumerate(target_rows):
        for j, col in enumerate(target_rows):
            out[i, j] = raw[idx[row], idx[col]]
    return out


def fro_support(q: np.ndarray, matrix: np.ndarray) -> float:
    raw = float(np.linalg.norm(matrix, ord="fro"))
    if raw == 0.0:
        return 0.0
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        cleaned = np.nan_to_num(q @ matrix @ q, nan=0.0, posinf=0.0, neginf=0.0)
    return float(np.linalg.norm(cleaned, ord="fro") / raw)


def diagonal_share(matrix: np.ndarray) -> float:
    denom = float(np.linalg.norm(matrix, ord="fro") ** 2)
    if denom == 0.0:
        return 1.0
    return float(np.sum(np.diag(matrix) ** 2) / denom)


def family_share(meta: pd.DataFrame, matrix: np.ndarray) -> float:
    total = float(np.linalg.norm(matrix, ord="fro") ** 2)
    if total == 0.0:
        return 1.0
    fam = meta["FamilyID"].astype(str).to_numpy()
    shares = []
    for fid in sorted(set(fam)):
        mask = fam == fid
        block = matrix[np.ix_(mask, mask)]
        shares.append(float(np.linalg.norm(block, ord="fro") ** 2) / total)
    return max(shares)


def normalize_matrix(matrix: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(matrix, ord="fro"))
    if norm == 0.0:
        raise RuntimeError("Cannot normalize zero object matrix.")
    return matrix / norm


def main() -> int:
    if not COORD.exists() or not COORD_MANIFEST.exists():
        raise RuntimeError("PB interaction coordinate must be frozen before object preflight.")
    manifest = pd.read_csv(COORD_MANIFEST).iloc[0]
    if not bool(manifest["CoordinateFreezeAuthorized"]):
        raise RuntimeError("PB interaction coordinate freeze is not authorized.")
    coord = pd.read_csv(COORD)
    rows = coord["EmpiricalRowID"].astype(str).tolist()
    q = load_qclean(rows)
    vector = coord["FrozenCoordinateValue"].astype(float).to_numpy()
    meta = coord[["EmpiricalRowID", "FamilyID", "ClockIndex"]].copy()

    outer = np.outer(vector, vector)
    zero_diag_outer = outer - np.diag(np.diag(outer))
    family_ids = meta["FamilyID"].astype(str).to_numpy()
    cross_family_mask = np.array(
        [[family_ids[i] != family_ids[j] for j in range(len(family_ids))] for i in range(len(family_ids))],
        dtype=float,
    )
    cross_family_outer = outer * cross_family_mask
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        cleaned_outer = np.nan_to_num(q @ outer @ q, nan=0.0, posinf=0.0, neginf=0.0)
    candidates = [
        (
            "PB_OUTER_PRODUCT_PSD",
            "PSD_COVARIANCE_CANDIDATE",
            "outer_product(frozen_PB_coordinate)",
            outer,
            True,
        ),
        (
            "PB_ZERO_DIAGONAL_OUTER_PRODUCT",
            "OFFDIAGONAL_COVARIANCE_RESPONSE_CANDIDATE",
            "outer_product(frozen_PB_coordinate) with fixed zero diagonal to exclude variance-inflation response",
            zero_diag_outer,
            True,
        ),
        (
            "PB_CROSS_FAMILY_ONLY_DIAGNOSTIC",
            "FAMILY_MASKED_DIAGNOSTIC_ONLY",
            "cross-family-only mask applied to the PB outer product; diagnostic only, not parent source",
            cross_family_outer,
            False,
        ),
        (
            "PB_QCLEAN_RESTRICTED_OUTER_PRODUCT",
            "CLEANED_DIAGNOSTIC_ONLY",
            "Q_clean outer_product(frozen_PB_coordinate) Q_clean; diagnostic only, not parent source",
            cleaned_outer,
            False,
        ),
    ]
    records = []
    matrices = []
    for object_id, object_class, provenance, raw_matrix, source_allowed in candidates:
        matrix = normalize_matrix(0.5 * (raw_matrix + raw_matrix.T))
        qsupport = fro_support(q, matrix)
        fshare = family_share(meta, matrix)
        dshare = diagonal_share(matrix)
        passes_support = qsupport >= SUPPORT_THRESHOLD
        passes_family = fshare <= MAX_FAMILY_SHARE
        passes_diag = dshare <= MAX_DIAGONAL_SHARE
        passes_overall = bool(source_allowed and passes_support and passes_family and passes_diag)
        records.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "ObjectCandidateID": object_id,
                "ObjectClass": object_class,
                "ObjectProvenance": provenance,
                "QCleanMatrixSupport": qsupport,
                "MaxFamilyBlockEnergyShare": fshare,
                "DiagonalEnergyShare": dshare,
                "PassesQCleanSupportGate": passes_support,
                "PassesFamilyBalanceGate": passes_family,
                "PassesDiagonalControlGate": passes_diag,
                "ParentSourceAllowed": source_allowed,
                "PassesOverallPreflight": passes_overall,
                "ObjectFreezeAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        )
        for i, row in enumerate(rows):
            for j, col in enumerate(rows):
                matrices.append(
                    {
                        "ProtocolID": PROTOCOL_ID,
                        "FreezeID": FREEZE_ID,
                        "ObjectCandidateID": object_id,
                        "RowID": row,
                        "ColumnID": col,
                        "Value": matrix[i, j],
                        "ObjectFreezeAuthorized": False,
                        "ScoringAuthorized": False,
                        "ClaimBoundary": CLAIM,
                    }
                )

    audit = pd.DataFrame(records).sort_values("QCleanMatrixSupport", ascending=False)
    audit.to_csv(OUT_AUDIT, index=False)
    pd.DataFrame(matrices).to_csv(OUT_OBJECT, index=False)
    passing = audit[audit["PassesOverallPreflight"]]
    best = audit.iloc[0]
    best_passing = passing.iloc[0] if len(passing) else best
    status = (
        "P_TAUCOV_PB_INTERACTION_OBJECT_PREFLIGHT_HAS_CANDIDATE_NO_SCORING"
        if len(passing)
        else "P_TAUCOV_PB_INTERACTION_OBJECT_PREFLIGHT_BLOCKED_NO_SCORING"
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "SourceFreezeID": SOURCE_FREEZE_ID,
                "ObjectCandidatesAudited": len(audit),
                "PassingObjectCandidates": len(passing),
                "BestObjectCandidateID": best["ObjectCandidateID"],
                "BestQCleanMatrixSupport": float(best["QCleanMatrixSupport"]),
                "BestPassingObjectCandidateID": best_passing["ObjectCandidateID"],
                "BestPassingQCleanMatrixSupport": float(best_passing["QCleanMatrixSupport"]) if len(passing) else 0.0,
                "SupportThreshold": SUPPORT_THRESHOLD,
                "MaxFamilyShareThreshold": MAX_FAMILY_SHARE,
                "MaxDiagonalShareThreshold": MAX_DIAGONAL_SHARE,
                "ObjectFreezeAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)

    table = "\n".join(
        f"| `{r.ObjectCandidateID}` | `{r.ObjectClass}` | `{r.QCleanMatrixSupport}` | `{r.MaxFamilyBlockEnergyShare}` | `{r.DiagonalEnergyShare}` | `{r.ParentSourceAllowed}` | `{r.PassesOverallPreflight}` |"
        for r in audit.itertuples(index=False)
    )
    OUT_DOC.write_text(
        "\n".join(
            [
                "# P-TauCov PB Interaction Object Preflight",
                "",
                f"Freeze ID: `{FREEZE_ID}`",
                "",
                f"Status: `{status}`",
                "",
                "## Purpose",
                "",
                "This packet tests whether the frozen `P*B` interaction coordinate can",
                "support a later covariance-object freeze without becoming a diagonal,",
                "single-family, or cleaner-generated shortcut.",
                "",
                "It does not authorize empirical scoring.",
                "",
                "## Candidate Results",
                "",
                "| Object candidate | class | Q-clean matrix support | max family block share | diagonal share | parent source allowed | overall preflight |",
                "|---|---|---:|---:|---:|---:|---:|",
                table,
                "",
                "## Interpretation",
                "",
                f"Best candidate: `{best['ObjectCandidateID']}` with Q-clean matrix support `{float(best['QCleanMatrixSupport'])}`.",
                "",
                f"Best admissible passing candidate: `{best_passing['ObjectCandidateID']}` with Q-clean matrix support `{float(best_passing['QCleanMatrixSupport']) if len(passing) else 0.0}`.",
                "",
                "The cleaned diagnostic is reported to quantify clean-subspace retention,",
                "but it is explicitly not an admissible parent source by itself. Only an",
                "uncleaned parent-derived object can be promoted in a later freeze packet.",
                "",
                "## Links",
                "",
                "- [`p_taucov_pb_interaction_coordinate_freeze.md`](p_taucov_pb_interaction_coordinate_freeze.md)",
                "- [`p_taucov_admissible_source_coordinate_extension.md`](p_taucov_admissible_source_coordinate_extension.md)",
                "",
                "## Claim Boundary",
                "",
                "Allowed statement:",
                "",
                "> A frozen `P*B` coordinate has been tested for object-construction readiness.",
                "",
                "Forbidden statement:",
                "",
                "> A covariance object is frozen, scoring is authorized, or Tau Core is validated.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
