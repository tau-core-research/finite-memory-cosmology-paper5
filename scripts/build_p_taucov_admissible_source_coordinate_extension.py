#!/usr/bin/env python3
"""Define and audit target-blind admissible source-coordinate extensions."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_ADMISSIBLE_SOURCE_COORDINATE_EXTENSION_v1"
CLAIM = "admissible_source_coordinate_extension_no_coordinate_freeze_no_scoring"

EMBEDDING = EVIDENCE / "p_taucov_tccs_parent_score_embedding_matrix.csv"
QCLEAN = EVIDENCE / "p_taucov_domain_compatibility_common_cleaner_matrix.csv"
DOMAIN_METRIC_SUMMARY = EVIDENCE / "p_taucov_domain_metric_candidate_audit_summary.csv"

OUT_RULE = EVIDENCE / "p_taucov_admissible_source_coordinate_extension_rule.csv"
OUT_AUDIT = EVIDENCE / "p_taucov_admissible_source_coordinate_extension_audit.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_admissible_source_coordinate_extension_summary.csv"
OUT_DOC = DOCS / "p_taucov_admissible_source_coordinate_extension.md"

SUPPORT_THRESHOLD = 0.20
MAX_FAMILY_SHARE = 0.50
MAX_DIAGONAL_SHARE = 0.10


def load_embedding() -> tuple[list[str], list[str], pd.DataFrame, np.ndarray]:
    df = pd.read_csv(EMBEDDING)
    rows = list(dict.fromkeys(df["EmpiricalRowID"].astype(str)))
    coords = list(dict.fromkeys(df["TauCoordinate"].astype(str)))
    ridx = {row: i for i, row in enumerate(rows)}
    cidx = {coord: i for i, coord in enumerate(coords)}
    mat = np.zeros((len(rows), len(coords)), dtype=float)
    for rec in df.to_dict("records"):
        mat[ridx[str(rec["EmpiricalRowID"])], cidx[str(rec["TauCoordinate"])]] = float(rec["EmbeddingValue"])
    meta = df.drop_duplicates("EmpiricalRowID").set_index("EmpiricalRowID").loc[rows].reset_index()
    return rows, coords, meta, mat


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


def normalize(vector: np.ndarray) -> np.ndarray:
    centered = vector - float(np.mean(vector))
    norm = float(np.linalg.norm(centered))
    if norm == 0.0:
        return centered
    return centered / norm


def support(q: np.ndarray, vector: np.ndarray) -> float:
    raw = float(np.linalg.norm(vector))
    if raw == 0.0:
        return 0.0
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        projected = np.nan_to_num(q @ vector, nan=0.0, posinf=0.0, neginf=0.0)
    return float(np.linalg.norm(projected) / raw)


def family_energy_share(meta: pd.DataFrame, vector: np.ndarray) -> float:
    energy = vector * vector
    total = float(np.sum(energy))
    if total == 0.0:
        return 1.0
    tmp = pd.DataFrame({"FamilyID": meta["FamilyID"].astype(str), "Energy": energy})
    return float(tmp.groupby("FamilyID")["Energy"].sum().max() / total)


def diagonal_share_from_outer(vector: np.ndarray) -> float:
    kernel = np.outer(vector, vector)
    denom = float(np.linalg.norm(kernel, ord="fro") ** 2)
    if denom == 0.0:
        return 1.0
    return float(np.sum(np.diag(kernel) ** 2) / denom)


def candidate_vectors(coords: list[str], emb: np.ndarray) -> list[tuple[str, str, str, np.ndarray]]:
    cidx = {coord: i for i, coord in enumerate(coords)}
    phi = emb[:, cidx["TEMPLATE_PHI_PARENT_SOURCE"]]
    b = emb[:, cidx["TEMPLATE_B_BRANCH_RESPONSE"]]
    p = emb[:, cidx["TEMPLATE_P_MORPH_PROJECTION"]]
    scale = emb[:, cidx["TEMPLATE_COORD_SCALE_UNIT"]]
    observing = emb[:, cidx["TEMPLATE_EXT_OBSERVING_CONTEXT"]]
    return [
        (
            "COORD_PB_INTERACTION",
            "INTERACTION_COORDINATE",
            "Projection-branch coupling term derived from the parent P*B interaction.",
            p * b,
        ),
        (
            "COORD_PPHI_INTERACTION",
            "INTERACTION_COORDINATE",
            "Projection-source coupling term derived from the parent P*Phi interaction.",
            p * phi,
        ),
        (
            "COORD_B2_BRANCH_COUNTERTERM",
            "INTERACTION_COORDINATE",
            "Branch quadratic counterterm derived from the parent B^2 branch sector.",
            b * b,
        ),
        (
            "COORD_P_BRANCH_SOURCE_CONTRAST",
            "CURVATURE_COORDINATE",
            "Projection-weighted branch/source contrast P*(B-Phi).",
            p * (b - phi),
        ),
        (
            "COORD_SCALE_OBSERVER_CONTEXT",
            "SOURCE_CONTEXT_COORDINATE",
            "Declared scale/context interaction from already frozen coordinate axes.",
            scale * observing,
        ),
    ]


def write_rule() -> None:
    rows = [
        ("ASC-R1_PARENT_PROVENANCE", "required", "Coordinate must be derived from a declared parent action, Hessian, commutator, boundary, spectral-domain, or external provenance term."),
        ("ASC-R2_TARGET_BLINDNESS", "required", "No target residual, score outcome, fitted alpha behavior, winning null, or post-score information may enter coordinate construction."),
        ("ASC-R3_ALLOWED_CLASSES", "required", "Allowed classes are INTERACTION_COORDINATE, CURVATURE_COORDINATE, SPECTRAL_DOMAIN_COORDINATE, and carefully quarantined SOURCE_CONTEXT_COORDINATE."),
        ("ASC-R4_FORBID_DIRECT_LABEL_PROXY", "forbidden_shortcut", "Family labels, morphology targets, projection-null labels, or source labels may not be promoted as active primary coordinates."),
        ("ASC-R5_QCLEAN_PREFLIGHT", f">={SUPPORT_THRESHOLD}", "The candidate must pass common-clean support before any scorecard or covariance-survival language."),
        ("ASC-R6_BALANCE_PREFLIGHT", f"<={MAX_FAMILY_SHARE}", "No single family, clock, or context block may dominate pre-score coordinate energy."),
        ("ASC-R7_DIAGONAL_CONTROL", f"<={MAX_DIAGONAL_SHARE}", "Outer-product use must not reduce to diagonal variance inflation."),
        ("ASC-R8_SCORING_FIREWALL", "required", "Passing this rule may authorize a later freeze packet only; it does not authorize empirical scoring by itself."),
    ]
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "RuleID": rid,
                "Policy": policy,
                "Meaning": meaning,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
            for rid, policy, meaning in rows
        ]
    ).to_csv(OUT_RULE, index=False)


def main() -> int:
    if not DOMAIN_METRIC_SUMMARY.exists():
        raise RuntimeError("Domain metric audit must exist before source-coordinate extension.")
    write_rule()
    rows, coords, meta, emb = load_embedding()
    q = load_qclean(rows)
    records = []
    for coord_id, coord_class, provenance, raw in candidate_vectors(coords, emb):
        vector = normalize(raw)
        qsupport = support(q, vector)
        fam_share = family_energy_share(meta, vector)
        diag_share = diagonal_share_from_outer(vector)
        passes_support = qsupport >= SUPPORT_THRESHOLD
        passes_family = fam_share <= MAX_FAMILY_SHARE
        passes_diag = diag_share <= MAX_DIAGONAL_SHARE
        records.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "CoordinateCandidateID": coord_id,
                "CandidateClass": coord_class,
                "ParentProvenance": provenance,
                "QCleanSupport": qsupport,
                "MaxFamilyEnergyShare": fam_share,
                "DiagonalEnergyShareIfOuterProduct": diag_share,
                "PassesQCleanSupportGate": passes_support,
                "PassesFamilyBalanceGate": passes_family,
                "PassesDiagonalControlGate": passes_diag,
                "CoordinateFreezeAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        )
    audit = pd.DataFrame(records).sort_values("QCleanSupport", ascending=False)
    audit.to_csv(OUT_AUDIT, index=False)
    passing = audit[
        audit["PassesQCleanSupportGate"]
        & audit["PassesFamilyBalanceGate"]
        & audit["PassesDiagonalControlGate"]
    ]
    best = audit.iloc[0]
    status = (
        "P_TAUCOV_ADMISSIBLE_SOURCE_COORDINATE_EXTENSION_HAS_PREFLIGHT_COORDINATE_NO_SCORING"
        if len(passing)
        else "P_TAUCOV_ADMISSIBLE_SOURCE_COORDINATE_EXTENSION_NO_PASSING_COORDINATE_NO_SCORING"
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "CandidatesAudited": len(audit),
                "PassingCandidates": len(passing),
                "BestCandidateID": best["CoordinateCandidateID"],
                "BestQCleanSupport": float(best["QCleanSupport"]),
                "BestMaxFamilyEnergyShare": float(best["MaxFamilyEnergyShare"]),
                "SupportThreshold": SUPPORT_THRESHOLD,
                "MaxFamilyShareThreshold": MAX_FAMILY_SHARE,
                "MaxDiagonalShareThreshold": MAX_DIAGONAL_SHARE,
                "CoordinateFreezeAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)

    table = "\n".join(
        f"| `{r.CoordinateCandidateID}` | `{r.CandidateClass}` | `{r.QCleanSupport}` | `{r.MaxFamilyEnergyShare}` | `{r.DiagonalEnergyShareIfOuterProduct}` | `{r.PassesQCleanSupportGate}` | `{r.PassesFamilyBalanceGate}` | `{r.PassesDiagonalControlGate}` | `{r.PassesQCleanSupportGate and r.PassesFamilyBalanceGate and r.PassesDiagonalControlGate}` |"
        for r in audit.itertuples(index=False)
    )
    OUT_DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Admissible Source-Coordinate Extension",
                "",
                f"Freeze ID: `{FREEZE_ID}`",
                "",
                f"Status: `{status}`",
                "",
                "## Why This Gate Exists",
                "",
                "The domain-metric audit showed that changing the metric on the current",
                "eight-coordinate embedding is not enough. The next admissible route must",
                "therefore add a richer parent-domain/source coordinate before any new",
                "P-TauCov object can be frozen.",
                "",
                "This packet defines which coordinate extensions are admissible and audits",
                "a first small set of target-blind nonlinear candidates derived from the",
                "already declared parent action/source structure.",
                "",
                "## Admissibility Rule",
                "",
                "- The coordinate must have parent-domain provenance.",
                "- It must not use target residuals, score outcomes, fitted alpha behavior, or winning nulls.",
                "- It must not be a direct family, morphology, or projection-null label proxy.",
                "- It must pass Q-clean support, family-balance, and diagonal-control preflight before any scoring packet.",
                "- This packet never authorizes empirical scoring by itself.",
                "",
                "## Candidate Preflight",
                "",
                "| Candidate | class | Q-clean support | max family energy share | diagonal share if outer product | support gate | family gate | diagonal gate | overall preflight |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|",
                table,
                "",
                "## Interpretation",
                "",
                f"Best candidate: `{best['CoordinateCandidateID']}` with Q-clean support `{float(best['QCleanSupport'])}`.",
                "",
                "A passing candidate would only become a candidate for a later coordinate",
                "freeze packet. It would not establish a signal and would not authorize a",
                "survival claim.",
                "",
                "## Links",
                "",
                "- [`p_taucov_parent_domain_curvature_source_requirement.md`](p_taucov_parent_domain_curvature_source_requirement.md)",
                "- [`p_taucov_domain_metric_update_rule.md`](p_taucov_domain_metric_update_rule.md)",
                "- [`p_taucov_domain_metric_candidate_audit.md`](p_taucov_domain_metric_candidate_audit.md)",
                "",
                "## Claim Boundary",
                "",
                "Allowed statement:",
                "",
                "> Target-blind parent-derived coordinate extensions have been screened for Q-clean support.",
                "",
                "Forbidden statement:",
                "",
                "> A new Tau covariance object is frozen, scoring is authorized, or Tau Core is validated.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
