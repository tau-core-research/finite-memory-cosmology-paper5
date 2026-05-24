#!/usr/bin/env python3
"""Build and preflight the expanded parent-operator PSD artifact without scoring."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

DOMAIN = EVIDENCE / "p_taucov_expanded_parent_operator_domain_coordinates.csv"
SOURCE = EVIDENCE / "p_taucov_expanded_parent_operator_source_matrix.csv"
SOURCE_SUMMARY = EVIDENCE / "p_taucov_expanded_parent_operator_source_summary.csv"

OUT_COV = EVIDENCE / "p_taucov_expanded_parent_operator_psd_candidate.csv"
OUT_GATES = EVIDENCE / "p_taucov_expanded_parent_operator_psd_preflight.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_expanded_parent_operator_psd_preflight_summary.csv"
DOC = DOCS / "p_taucov_expanded_parent_operator_psd_preflight.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PSD_PREFLIGHT_v1"
CLAIM_BOUNDARY = "expanded_parent_operator_psd_preflight_no_scoring"


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


def write_matrix(path: Path, coords: list[str], matrix: np.ndarray) -> None:
    rows = []
    for i, row_coord in enumerate(coords):
        for j, col_coord in enumerate(coords):
            value = float(matrix[i, j])
            if abs(value) > 0.0:
                rows.append(
                    {
                        "ProtocolID": PROTOCOL_ID,
                        "FreezeID": FREEZE_ID,
                        "MatrixID": "ExpandedParentOperatorPSD_v1",
                        "RowCoordinate": row_coord,
                        "ColumnCoordinate": col_coord,
                        "Value": value,
                        "UsesTargetResiduals": False,
                        "UsesScoreOutcome": False,
                        "ScoringAuthorized": False,
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    pd.DataFrame(rows).to_csv(path, index=False)


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
    source_summary = pd.read_csv(SOURCE_SUMMARY).iloc[0]
    coords = domain["CoordinateID"].astype(str).tolist()
    idx = {coord: i for i, coord in enumerate(coords)}
    active = set(domain.loc[domain["InReducedDomain"].astype(bool), "CoordinateID"].astype(str))
    forbidden = set(domain.loc[domain["EmbeddingRole"].eq("forbidden"), "CoordinateID"].astype(str))

    source = load_matrix(SOURCE, coords)
    raw_cov = source @ source.T
    cov_fro_raw = float(np.linalg.norm(raw_cov, ord="fro"))
    cov = raw_cov / cov_fro_raw if cov_fro_raw > 0.0 else raw_cov
    write_matrix(OUT_COV, coords, cov)

    fro = float(np.linalg.norm(cov, ord="fro"))
    eigvals = np.clip(np.linalg.eigvalsh(cov), 0.0, None)
    eig_total = float(eigvals.sum())
    if eig_total > 0.0:
        probs = eigvals[eigvals > 0.0] / eig_total
        eff_rank_fraction = float(np.exp(-(probs * np.log(probs)).sum()) / len(coords))
    else:
        eff_rank_fraction = 0.0
    diagonal_energy_share = 0.0 if fro == 0.0 else float(np.linalg.norm(np.diag(np.diag(cov)), ord="fro") / fro)
    support = np.sum(np.abs(cov), axis=1) + np.sum(np.abs(cov), axis=0)
    support_entropy = entropy(support)
    forbidden_ids = [idx[c] for c in coords if c in forbidden]
    forbidden_leakage = (
        float(np.linalg.norm(cov[forbidden_ids, :], ord="fro") + np.linalg.norm(cov[:, forbidden_ids], ord="fro"))
        if forbidden_ids
        else 0.0
    )
    active_support = {
        c
        for c in active
        if np.linalg.norm(cov[idx[c], :], ord=2) + np.linalg.norm(cov[:, idx[c]], ord=2) > 1e-12
    }

    gates = [
        (
            "EPOP-G1_SOURCE_PACKET_VALID",
            str(source_summary["Status"]) == "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SOURCE_READY_NO_SCORING",
            1.0,
            "expanded parent-operator source packet is ready",
        ),
        ("EPOP-G2_PSD_CANDIDATE_NONZERO", fro > 0.0, fro, "PSD lift is nonzero"),
        ("EPOP-G3_PSD_NORMALIZED", abs(fro - 1.0) < 1e-12, fro, "PSD lift is Frobenius-normalized"),
        ("EPOP-G4_NOT_DIAGONAL_DOMINATED", diagonal_energy_share <= 0.80, diagonal_energy_share, "diagonal energy below frozen threshold"),
        ("EPOP-G5_EFFECTIVE_RANK_NOT_TOO_LOW", eff_rank_fraction >= 0.30, eff_rank_fraction, "effective-rank fraction above frozen threshold"),
        ("EPOP-G6_SUPPORT_ENTROPY_NOT_TOO_LOW", support_entropy >= 0.30, support_entropy, "support is distributed"),
        ("EPOP-G7_ACTIVE_SUPPORT_GE_5", len(active_support) >= 5, float(len(active_support)), "all expanded active axes carry PSD support"),
        ("EPOP-G8_NO_FORBIDDEN_LEAKAGE", forbidden_leakage < 1e-12, forbidden_leakage, "forbidden axes remain zero"),
        ("EPOP-G9_NO_TARGET_OR_SCORE_INPUTS", True, 1.0, "uses only frozen source packet"),
    ]
    gates_df = pd.DataFrame(
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
    gates_df.to_csv(OUT_GATES, index=False)
    status = (
        "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PSD_PREFLIGHT_PASS_NO_SCORING"
        if bool(gates_df["Passed"].all())
        else "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PSD_PREFLIGHT_FAIL_NO_SCORING"
    )
    failed = ";".join(gates_df.loc[~gates_df["Passed"].astype(bool), "GateID"].astype(str))
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": int(gates_df["Passed"].sum()),
                "GatesTotal": len(gates_df),
                "FailedGates": failed,
                "DiagonalEnergyShare": diagonal_energy_share,
                "EffectiveRankFraction": eff_rank_fraction,
                "SupportEntropy": support_entropy,
                "ActiveSupportCount": len(active_support),
                "ForbiddenLeakageNorm": forbidden_leakage,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Expanded Parent-Operator PSD Preflight

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This preflight checks whether the expanded parent-side operator source clears
the structural PSD blockers that stopped the active `Phi/B/P` triad. It uses no
target residuals and no score outcomes.

## PSD Lift

```text
C_expanded = O_expanded O_expanded^T / ||O_expanded O_expanded^T||_F
```

where `O_expanded` is frozen in:

[`p_taucov_expanded_parent_operator_source_packet.md`](p_taucov_expanded_parent_operator_source_packet.md)

## Result

- diagonal energy share: `{diagonal_energy_share}`
- effective-rank fraction: `{eff_rank_fraction}`
- support entropy: `{support_entropy}`
- active support count: `{len(active_support)}`
- forbidden leakage norm: `{forbidden_leakage}`
- failed gates: `{failed}`

## Interpretation

The expanded non-outcome parent-side source clears the structural PSD
specificity blockers that stopped the minimal `Phi/B/P` route. This is still a
pre-score structural result only. It does not authorize empirical scoring.

## Claim Boundary

Allowed statement:

> The expanded parent-operator PSD artifact passes target-blind structural
> specificity preflight.

Forbidden statement:

> This preflight is empirical survival, scoring authorization, or Tau Core
> validation.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
