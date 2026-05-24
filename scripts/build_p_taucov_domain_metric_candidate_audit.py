#!/usr/bin/env python3
"""Audit target-blind domain-metric candidates after Q-clean support failure."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_DOMAIN_METRIC_CANDIDATE_AUDIT_v1"
CLAIM = "domain_metric_candidate_audit_no_metric_freeze_no_scoring"

EMBEDDING = EVIDENCE / "p_taucov_tccs_parent_score_embedding_matrix.csv"
QCLEAN = EVIDENCE / "p_taucov_domain_compatibility_common_cleaner_matrix.csv"
HESSIAN = EVIDENCE / "p_taucov_projection_essentiality_parent_action_hessian.csv"
RULE_SUMMARY = EVIDENCE / "p_taucov_domain_metric_update_rule_summary.csv"

OUT_CANDIDATES = EVIDENCE / "p_taucov_domain_metric_candidate_audit.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_domain_metric_candidate_audit_summary.csv"
OUT_DOC = DOCS / "p_taucov_domain_metric_candidate_audit.md"

ACTIVE_BRANCH_COORDS = ["TEMPLATE_PHI_PARENT_SOURCE", "TEMPLATE_B_BRANCH_RESPONSE"]
ACTIVE_COORDS = ["TEMPLATE_PHI_PARENT_SOURCE", "TEMPLATE_B_BRANCH_RESPONSE", "TEMPLATE_P_MORPH_PROJECTION"]
SUPPORT_THRESHOLD = 0.20
COND_MAX = 1e8


def load_embedding() -> tuple[list[str], list[str], np.ndarray]:
    df = pd.read_csv(EMBEDDING)
    rows = list(dict.fromkeys(df["EmpiricalRowID"].astype(str)))
    coords = list(dict.fromkeys(df["TauCoordinate"].astype(str)))
    ridx = {row: i for i, row in enumerate(rows)}
    cidx = {coord: i for i, coord in enumerate(coords)}
    mat = np.zeros((len(rows), len(coords)), dtype=float)
    for rec in df.to_dict("records"):
        mat[ridx[str(rec["EmpiricalRowID"])], cidx[str(rec["TauCoordinate"])]] = float(rec["EmbeddingValue"])
    return rows, coords, mat


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


def load_hessian(coords: list[str]) -> np.ndarray:
    df = pd.read_csv(HESSIAN)
    idx = {coord: i for i, coord in enumerate(coords)}
    mat = np.zeros((len(coords), len(coords)), dtype=float)
    for rec in df.to_dict("records"):
        r = str(rec["RowCoordinate"])
        c = str(rec["ColumnCoordinate"])
        if r in idx and c in idx:
            mat[idx[r], idx[c]] = float(rec["Value"])
    return 0.5 * (mat + mat.T)


def psd_sqrt(metric: np.ndarray) -> tuple[np.ndarray, float, float]:
    metric = 0.5 * (metric + metric.T)
    eigvals, eigvecs = np.linalg.eigh(metric)
    eigvals = np.clip(eigvals, 0.0, None)
    positive = eigvals[eigvals > 1e-12]
    condition = float(positive.max() / positive.min()) if len(positive) else float("inf")
    sqrt = eigvecs @ np.diag(np.sqrt(eigvals)) @ eigvecs.T
    rank = float(len(positive))
    return sqrt, condition, rank


def normalize_trace(metric: np.ndarray) -> np.ndarray:
    trace = float(np.trace(metric))
    if trace <= 0.0:
        return metric
    return metric * (metric.shape[0] / trace)


def candidate_metrics(coords: list[str], hessian: np.ndarray) -> list[tuple[str, str, np.ndarray]]:
    n = len(coords)
    identity = np.eye(n)
    active = np.zeros((n, n), dtype=float)
    cidx = {coord: i for i, coord in enumerate(coords)}
    for coord in ACTIVE_COORDS:
        active[cidx[coord], cidx[coord]] = 1.0

    abs_h = np.abs(hessian)
    h2 = hessian @ hessian.T
    active_abs_h = active @ abs_h @ active
    active_h2 = active @ h2 @ active

    # The tiny ridge is a declared numerical conditioning convention, not a
    # score-tuned parameter. It only keeps square roots defined.
    ridge = 1e-9 * np.eye(n)
    return [
        ("IDENTITY_UNIT_DOMAIN_METRIC", "baseline_unit_metric_from_coordinate_convention", identity),
        ("PARENT_HESSIAN_ABS_COUPLING_METRIC", "absolute_projection_essentiality_hessian_coupling_graph", normalize_trace(abs_h + ridge)),
        ("PARENT_HESSIAN_PSD_SQUARE_METRIC", "H H^T from projection_essentiality_parent_action_hessian", normalize_trace(h2 + ridge)),
        ("ACTIVE_SECTOR_ABS_COUPLING_METRIC", "active Phi-B-P absolute coupling graph only", normalize_trace(active_abs_h + ridge)),
        ("ACTIVE_SECTOR_PSD_SQUARE_METRIC", "active Phi-B-P H H^T only", normalize_trace(active_h2 + ridge)),
    ]


def support(q: np.ndarray, vector: np.ndarray) -> float:
    raw = float(np.linalg.norm(vector))
    if raw == 0.0:
        return 0.0
    return float(np.linalg.norm(q @ vector) / raw)


def main() -> int:
    if not RULE_SUMMARY.exists():
        raise RuntimeError("Domain metric update rule must be defined before candidate audit.")
    rows, coords, emb = load_embedding()
    q = load_qclean(rows)
    hessian = load_hessian(coords)
    cidx = {coord: i for i, coord in enumerate(coords)}

    records = []
    for metric_id, provenance, metric in candidate_metrics(coords, hessian):
        sqrt_g, condition, rank = psd_sqrt(metric)
        transformed = emb @ sqrt_g
        branch_supports = {
            coord: support(q, transformed[:, cidx[coord]]) for coord in ACTIVE_BRANCH_COORDS
        }
        active_supports = {
            coord: support(q, transformed[:, cidx[coord]]) for coord in ACTIVE_COORDS
        }
        min_branch = min(branch_supports.values())
        max_branch = max(branch_supports.values())
        max_active = max(active_supports.values())
        pass_support = min_branch >= SUPPORT_THRESHOLD
        pass_condition = condition <= COND_MAX
        records.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "MetricCandidateID": metric_id,
                "MetricProvenance": provenance,
                "MetricRank": rank,
                "MetricConditionNumber": condition,
                "MinActiveBranchQCleanSupport": min_branch,
                "MaxActiveBranchQCleanSupport": max_branch,
                "MaxActiveSectorQCleanSupport": max_active,
                "PhiSupport": branch_supports["TEMPLATE_PHI_PARENT_SOURCE"],
                "BSupport": branch_supports["TEMPLATE_B_BRANCH_RESPONSE"],
                "PSupport": active_supports["TEMPLATE_P_MORPH_PROJECTION"],
                "PassesSupportGate": pass_support,
                "PassesConditionGate": pass_condition,
                "MetricFreezeAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        )

    df = pd.DataFrame(records).sort_values(
        ["PassesSupportGate", "MinActiveBranchQCleanSupport"], ascending=[False, False]
    )
    df.to_csv(OUT_CANDIDATES, index=False)
    passing = df[df["PassesSupportGate"] & df["PassesConditionGate"]]
    best = df.iloc[0]
    status = (
        "P_TAUCOV_DOMAIN_METRIC_CANDIDATE_AUDIT_HAS_PREFLIGHT_METRIC_NO_SCORING"
        if len(passing)
        else "P_TAUCOV_DOMAIN_METRIC_CANDIDATE_AUDIT_NO_PASSING_METRIC_NO_SCORING"
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "MetricCandidatesAudited": len(df),
                "PassingMetricCandidates": len(passing),
                "BestMetricCandidateID": best["MetricCandidateID"],
                "BestMinActiveBranchQCleanSupport": float(best["MinActiveBranchQCleanSupport"]),
                "BestMaxActiveSectorQCleanSupport": float(best["MaxActiveSectorQCleanSupport"]),
                "SupportThreshold": SUPPORT_THRESHOLD,
                "MetricFreezeAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)

    table = "\n".join(
        f"| `{r.MetricCandidateID}` | `{r.MinActiveBranchQCleanSupport}` | `{r.MaxActiveBranchQCleanSupport}` | `{r.PSupport}` | `{r.PassesSupportGate}` |"
        for r in df.itertuples(index=False)
    )
    OUT_DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Domain-Metric Candidate Audit",
                "",
                f"Freeze ID: `{FREEZE_ID}`",
                "",
                f"Status: `{status}`",
                "",
                "## Purpose",
                "",
                "This target-blind audit tests a fixed set of domain-metric candidates",
                "derived from coordinate convention and the projection-essential parent",
                "action Hessian. It does not use target residuals, score outcomes, fitted",
                "alpha behavior, or winning nulls.",
                "",
                "The audit asks only whether any candidate metric gives active branch",
                "coordinates enough support in the frozen common clean subspace before",
                "empirical scoring.",
                "",
                "## Candidate Results",
                "",
                "| Metric candidate | min branch support | max branch support | projection support | support gate |",
                "|---|---:|---:|---:|---:|",
                table,
                "",
                "## Interpretation",
                "",
                f"Best candidate: `{best['MetricCandidateID']}` with minimum active-branch support `{float(best['MinActiveBranchQCleanSupport'])}`.",
                "",
                "If no candidate passes, the current coordinate/domain inventory is too",
                "poor to produce a parent-domain curvature source by metric update alone.",
                "A richer parent-domain embedding or new admissible coordinate source is",
                "then required before any scorecard.",
                "",
                "## Claim Boundary",
                "",
                "Allowed statement:",
                "",
                "> Target-blind metric candidates have been audited for Q-clean active-branch support.",
                "",
                "Forbidden statement:",
                "",
                "> A metric is frozen, a Tau signal is constructed, or empirical scoring is authorized.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
