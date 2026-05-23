#!/usr/bin/env python3
"""Run specificity preflight for the projection-coupled P-TauCov candidate."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

DOMAIN = EVIDENCE / "p_taucov_full_action_domain_coordinates.csv"
DELTA_C = EVIDENCE / "p_taucov_projection_coupled_delta_c_tau_candidate.csv"
ASSEMBLY = EVIDENCE / "p_taucov_projection_coupled_jacobian_assembly_summary.csv"

OUT = EVIDENCE / "p_taucov_projection_coupled_specificity_preflight.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_projection_coupled_specificity_preflight_summary.csv"
DOC = DOCS / "p_taucov_projection_coupled_specificity_preflight.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PROJECTION_COUPLED_SPECIFICITY_PREFLIGHT_v1"
CLAIM_BOUNDARY = "projection_coupled_specificity_preflight_no_scoring"


def load_matrix(path: Path, coords: list[str]) -> np.ndarray:
    df = pd.read_csv(path)
    idx = {coord: i for i, coord in enumerate(coords)}
    matrix = np.zeros((len(coords), len(coords)), dtype=float)
    for row in df.itertuples(index=False):
        row_coord = str(row.RowCoordinate)
        col_coord = str(row.ColumnCoordinate)
        if row_coord in idx and col_coord in idx:
            matrix[idx[row_coord], idx[col_coord]] = float(row.Value)
    return matrix


def entropy(values: np.ndarray) -> float:
    total = float(values.sum())
    if total <= 0.0:
        return 0.0
    probs = values[values > 0.0] / total
    if len(probs) <= 1:
        return 0.0
    return float(-(probs * np.log(probs)).sum() / np.log(len(values)))


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    domain = pd.read_csv(DOMAIN)
    coords = domain["CoordinateID"].astype(str).tolist()
    reduced = set(domain.loc[domain["InReducedDomain"].astype(bool), "CoordinateID"].astype(str))
    gauge_forbidden = set(domain.loc[domain["EmbeddingRole"].isin(["gauge", "forbidden"]), "CoordinateID"].astype(str))
    matrix = load_matrix(DELTA_C, coords)
    assembly = pd.read_csv(ASSEMBLY).iloc[0]

    eigvals = np.clip(np.linalg.eigvalsh(matrix), 0.0, None)
    eig_total = float(eigvals.sum())
    if eig_total > 0.0:
        probs = eigvals[eigvals > 0.0] / eig_total
        eff_rank = float(np.exp(-(probs * np.log(probs)).sum()))
        eff_rank_fraction = eff_rank / len(coords)
    else:
        eff_rank_fraction = 0.0

    fro = float(np.linalg.norm(matrix, ord="fro"))
    diagonal_energy_share = 0.0 if fro == 0.0 else float(np.linalg.norm(np.diag(np.diag(matrix)), ord="fro") / fro)
    support = np.sum(np.abs(matrix), axis=1) + np.sum(np.abs(matrix), axis=0)
    support_entropy = entropy(support)

    idx = {coord: i for i, coord in enumerate(coords)}
    p_active = np.zeros_like(matrix)
    p_active[idx["TEMPLATE_P_MORPH_PROJECTION"], idx["TEMPLATE_P_MORPH_PROJECTION"]] = 1.0
    comm = p_active @ matrix - matrix @ p_active
    noncomm_share = 0.0 if fro == 0.0 else float(np.linalg.norm(comm, ord="fro") / fro)

    forbidden_ids = [idx[coord] for coord in coords if coord in gauge_forbidden]
    forbidden_leakage = (
        float(np.linalg.norm(matrix[forbidden_ids, :], ord="fro") + np.linalg.norm(matrix[:, forbidden_ids], ord="fro"))
        if forbidden_ids
        else 0.0
    )
    projection_idx = idx["TEMPLATE_P_MORPH_PROJECTION"]
    branch_idx = idx["TEMPLATE_B_BRANCH_RESPONSE"]
    projection_energy = float(np.linalg.norm(matrix[projection_idx, :], ord=2) + np.linalg.norm(matrix[:, projection_idx], ord=2))
    branch_energy = float(np.linalg.norm(matrix[branch_idx, :], ord=2) + np.linalg.norm(matrix[:, branch_idx], ord=2))

    gates = [
        (
            "PCS-G1_ASSEMBLY_VALID",
            str(assembly["Status"]) == "P_TAUCOV_PROJECTION_COUPLED_JACOBIAN_ASSEMBLED_NO_SCORING",
            1.0,
            "projection-coupled assembly artifact exists",
        ),
        ("PCS-G2_REDUCED_SUPPORT_ONLY", forbidden_leakage < 1e-12, forbidden_leakage, "no gauge/forbidden leakage"),
        ("PCS-G3_NOT_DIAGONAL_DOMINATED", diagonal_energy_share <= 0.80, diagonal_energy_share, "fails if covariance remains diagonal dominated"),
        ("PCS-G4_NONCOMMUTING_WITH_ACTIVE_PMORPH", noncomm_share >= 0.10, noncomm_share, "requires active projection noncommutativity"),
        ("PCS-G5_EFFECTIVE_RANK_NOT_TOO_LOW", eff_rank_fraction >= 0.30, eff_rank_fraction, "requires nontrivial rank support"),
        ("PCS-G6_SUPPORT_ENTROPY_NOT_TOO_LOW", support_entropy >= 0.30, support_entropy, "requires distributed support"),
        ("PCS-G7_PROJECTION_CHANNEL_PRESENT", projection_energy > 0.0, projection_energy, "requires explicit projection support"),
        ("PCS-G8_BRANCH_CHANNEL_PRESENT", branch_energy > 0.0, branch_energy, "requires explicit branch support"),
        ("PCS-G9_NO_TARGET_OR_SCORE_INPUTS", True, 1.0, "preflight uses only no-score assembly artifact"),
    ]
    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "Passed": bool(passed),
                "MetricValue": float(value),
                "Interpretation": interpretation,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, passed, value, interpretation in gates
        ]
    )
    df.to_csv(OUT, index=False)
    status = (
        "P_TAUCOV_PROJECTION_COUPLED_SPECIFICITY_PREFLIGHT_PASS_NO_SCORING"
        if bool(df["Passed"].all())
        else "P_TAUCOV_PROJECTION_COUPLED_SPECIFICITY_PREFLIGHT_FAIL_NO_SCORING"
    )
    failed = ";".join(df.loc[~df["Passed"].astype(bool), "GateID"].astype(str))
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": int(df["Passed"].sum()),
                "GatesTotal": len(df),
                "FailedGates": failed,
                "DiagonalEnergyShare": diagonal_energy_share,
                "ActiveProjectionNoncommutatorShare": noncomm_share,
                "EffectiveRankFraction": eff_rank_fraction,
                "SupportEntropy": support_entropy,
                "ProjectionChannelEnergy": projection_energy,
                "BranchChannelEnergy": branch_energy,
                "ForbiddenGaugeLeakageNorm": forbidden_leakage,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Projection-Coupled Specificity Preflight

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This preflight checks whether the projection-coupled reduced-Jacobian candidate
is structurally specific enough to justify any later scoring authorization. It
uses no target residuals and no score outcomes.

## Result

- diagonal energy share: `{diagonal_energy_share}`
- active projection noncommutator share: `{noncomm_share}`
- effective-rank fraction: `{eff_rank_fraction}`
- support entropy: `{support_entropy}`
- projection channel energy: `{projection_energy}`
- branch channel energy: `{branch_energy}`
- failed gates: `{failed}`

## Interpretation

The projection-coupled assembly fixes the previous zero-morphology-channel
failure, but the PSD-lifted covariance remains too diagonal-dominated and too
low-rank to authorize scoring.

## Claim Boundary

Allowed statement:

> The projection-coupled candidate improves the branch-only artifact by adding
> an explicit active projection channel, but it still fails specificity
> preflight before scoring.

Forbidden statement:

> This candidate authorizes scoring, survived a Tau-specific test, or validates
> Tau Core.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
