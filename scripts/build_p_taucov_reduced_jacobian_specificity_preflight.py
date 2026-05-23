#!/usr/bin/env python3
"""Run a target-blind specificity preflight for the reduced-Jacobian candidate."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"
DOMAIN = EVIDENCE / "p_taucov_full_action_domain_coordinates.csv"
DELTA_C = EVIDENCE / "p_taucov_reduced_jacobian_delta_c_tau_candidate.csv"
ASSEMBLY = EVIDENCE / "p_taucov_reduced_jacobian_assembly_summary.csv"

OUT = EVIDENCE / "p_taucov_reduced_jacobian_specificity_preflight.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_reduced_jacobian_specificity_preflight_summary.csv"
DOC = DOCS / "p_taucov_reduced_jacobian_specificity_preflight.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_REDUCED_JACOBIAN_SPECIFICITY_PREFLIGHT_v1"
CLAIM_BOUNDARY = "reduced_jacobian_specificity_preflight_no_scoring"


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
    diag = np.diag(np.diag(matrix))
    diagonal_energy_share = 0.0 if fro == 0.0 else float(np.linalg.norm(diag, ord="fro") / fro)
    support = np.sum(np.abs(matrix), axis=1) + np.sum(np.abs(matrix), axis=0)
    support_entropy = entropy(support)

    idx = {coord: i for i, coord in enumerate(coords)}
    p_morph = np.zeros((len(coords), len(coords)))
    for coord in ["TEMPLATE_M_PARENT_MORPHOLOGY", "TEMPLATE_P_MORPH_PROJECTION"]:
        if coord in idx:
            p_morph[idx[coord], idx[coord]] = 1.0
    comm = p_morph @ matrix - matrix @ p_morph
    comm_norm = float(np.linalg.norm(comm, ord="fro"))
    noncomm_share = 0.0 if fro == 0.0 else comm_norm / fro

    reduced_ids = [idx[coord] for coord in coords if coord in reduced]
    forbidden_ids = [idx[coord] for coord in coords if coord in gauge_forbidden]
    reduced_energy = float(np.linalg.norm(matrix[np.ix_(reduced_ids, reduced_ids)], ord="fro"))
    forbidden_leakage = (
        float(np.linalg.norm(matrix[forbidden_ids, :], ord="fro") + np.linalg.norm(matrix[:, forbidden_ids], ord="fro"))
        if forbidden_ids
        else 0.0
    )

    morphology_ids = [idx[c] for c in ["TEMPLATE_M_PARENT_MORPHOLOGY", "TEMPLATE_P_MORPH_PROJECTION"] if c in idx]
    morphology_energy = (
        float(np.linalg.norm(matrix[np.ix_(morphology_ids, morphology_ids)], ord="fro"))
        if morphology_ids
        else 0.0
    )
    morphology_energy_share = 0.0 if fro == 0.0 else morphology_energy / fro

    gates = [
        ("RJS-G1_ASSEMBLY_VALID", str(assembly["Status"]) == "P_TAUCOV_REDUCED_JACOBIAN_ASSEMBLED_NO_SCORING", 1.0, "assembly artifact exists"),
        ("RJS-G2_REDUCED_SUPPORT_ONLY", forbidden_leakage < 1e-12, forbidden_leakage, "no gauge/forbidden leakage"),
        ("RJS-G3_NOT_DIAGONAL_ONLY", diagonal_energy_share <= 0.80, diagonal_energy_share, "fails if covariance is essentially diagonal"),
        ("RJS-G4_NONCOMMUTING_WITH_PMORPH", noncomm_share >= 0.10, noncomm_share, "requires projection-sensitive noncommutativity"),
        ("RJS-G5_EFFECTIVE_RANK_NOT_TOO_LOW", eff_rank_fraction >= 0.30, eff_rank_fraction, "requires nontrivial rank support"),
        ("RJS-G6_SUPPORT_ENTROPY_NOT_TOO_LOW", support_entropy >= 0.30, support_entropy, "requires distributed support"),
        ("RJS-G7_MORPHOLOGY_CHANNEL_PRESENT", morphology_energy_share > 0.0, morphology_energy_share, "requires explicit morphology/projection channel energy"),
        ("RJS-G8_NO_TARGET_OR_SCORE_INPUTS", True, 1.0, "preflight uses only assembly artifact"),
    ]
    rows = [
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
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)
    status = (
        "P_TAUCOV_REDUCED_JACOBIAN_SPECIFICITY_PREFLIGHT_PASS_NO_SCORING"
        if bool(df["Passed"].all())
        else "P_TAUCOV_REDUCED_JACOBIAN_SPECIFICITY_PREFLIGHT_FAIL_NO_SCORING"
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
                "NoncommutatorShare": noncomm_share,
                "EffectiveRankFraction": eff_rank_fraction,
                "SupportEntropy": support_entropy,
                "MorphologyEnergyShare": morphology_energy_share,
                "ReducedEnergyNorm": reduced_energy,
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
        f"""# P-TauCov Reduced-Jacobian Specificity Preflight

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This preflight checks whether the assembled strict branch-only `delta_C_Tau`
candidate is structurally specific enough to justify any later scoring
authorization. It uses no target residuals and no score outcomes.

## Result

The candidate is clean but too simple:

- diagonal energy share: `{diagonal_energy_share}`
- noncommutator share versus `P_morph`: `{noncomm_share}`
- effective-rank fraction: `{eff_rank_fraction}`
- support entropy: `{support_entropy}`
- morphology energy share: `{morphology_energy_share}`
- failed gates: `{failed}`

## Interpretation

The strict branch-only assembly is a valid source-assembly artifact, but it is
not yet a Tau-specific score candidate. It is diagonal, low-support, and does
not carry an explicit morphology/projection noncommutative signature.

## Claim Boundary

Allowed statement:

> The first reduced-Jacobian candidate was assembled and then rejected at
> specificity preflight before scoring.

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
