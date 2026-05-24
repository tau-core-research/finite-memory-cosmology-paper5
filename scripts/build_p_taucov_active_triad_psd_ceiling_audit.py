#!/usr/bin/env python3
"""Audit the PSD-lift ceiling for the active Phi/B/P triad."""

from __future__ import annotations

from pathlib import Path

import itertools

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

DOMAIN = EVIDENCE / "p_taucov_full_action_domain_coordinates.csv"
PREFLIGHT = EVIDENCE / "p_taucov_projection_coupled_specificity_preflight_summary.csv"

OUT = EVIDENCE / "p_taucov_active_triad_psd_ceiling_audit.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_active_triad_psd_ceiling_audit_summary.csv"
DOC = DOCS / "p_taucov_active_triad_psd_ceiling_audit.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_ACTIVE_TRIAD_PSD_CEILING_AUDIT_v1"
CLAIM_BOUNDARY = "active_triad_psd_ceiling_audit_no_scoring"

ACTIVE_TRIAD = [
    "TEMPLATE_PHI_PARENT_SOURCE",
    "TEMPLATE_B_BRANCH_RESPONSE",
    "TEMPLATE_P_MORPH_PROJECTION",
]


def psd_metrics(a: float, b: float, c: float, full_n: int) -> dict:
    j = np.array(
        [
            [0.0, a, b],
            [a, 0.0, c],
            [b, c, 0.0],
        ],
        dtype=float,
    )
    cov = j @ j.T
    fro = float(np.linalg.norm(cov, ord="fro"))
    if fro > 0.0:
        cov = cov / fro
    eigvals = np.clip(np.linalg.eigvalsh(cov), 0.0, None)
    eig_total = float(eigvals.sum())
    if eig_total > 0.0:
        probs = eigvals[eigvals > 0.0] / eig_total
        eff_rank_fraction = float(np.exp(-(probs * np.log(probs)).sum()) / full_n)
    else:
        eff_rank_fraction = 0.0
    diag_share = float(np.linalg.norm(np.diag(np.diag(cov)), ord="fro"))
    return {
        "a_phi_b": a,
        "b_phi_p": b,
        "c_b_p": c,
        "DiagonalEnergyShare": diag_share,
        "EffectiveRankFraction": eff_rank_fraction,
        "MinEigenvalue": float(eigvals.min()),
        "MaxEigenvalue": float(eigvals.max()),
    }


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    domain = pd.read_csv(DOMAIN)
    preflight = pd.read_csv(PREFLIGHT).iloc[0]
    full_n = len(domain)
    reduced = set(domain.loc[domain["InReducedDomain"].astype(bool), "CoordinateID"].astype(str))
    active_triad_available = all(coord in reduced for coord in ACTIVE_TRIAD)

    # Deterministic target-blind scan over normalized off-diagonal active-triad
    # source shapes. This is not a score search: it uses no residuals and tests
    # only the structural ceiling of the current three-coordinate domain.
    values = [-1.0, -0.5, -0.25, 0.25, 0.5, 1.0]
    rows = [psd_metrics(a, b, c, full_n) for a, b, c in itertools.product(values, repeat=3)]
    table = pd.DataFrame(rows)
    table.insert(0, "ProtocolID", PROTOCOL_ID)
    table.insert(1, "FreezeID", FREEZE_ID)
    table["UsesTargetResiduals"] = False
    table["UsesScoreOutcome"] = False
    table["ScoringAuthorized"] = False
    table["ClaimBoundary"] = CLAIM_BOUNDARY
    table.to_csv(OUT, index=False)

    best_diag = table.loc[table["DiagonalEnergyShare"].idxmin()]
    best_rank = table.loc[table["EffectiveRankFraction"].idxmax()]
    joint_passes = table[
        (table["DiagonalEnergyShare"] <= 0.80)
        & (table["EffectiveRankFraction"] >= 0.30)
    ]
    current_diag = float(preflight["DiagonalEnergyShare"])
    current_rank = float(preflight["EffectiveRankFraction"])
    status = (
        "P_TAUCOV_ACTIVE_TRIAD_PSD_CEILING_BLOCKS_SCORING_NO_SCORING"
        if active_triad_available and joint_passes.empty
        else "P_TAUCOV_ACTIVE_TRIAD_PSD_CEILING_OPEN_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "FullCoordinateCount": full_n,
                "ActiveTriadAvailable": active_triad_available,
                "ScanRows": len(table),
                "JointPassRows_DiagLe080_RankGe030": len(joint_passes),
                "BestDiagonalEnergyShare": float(best_diag["DiagonalEnergyShare"]),
                "BestDiagonal_EffectiveRankFraction": float(best_diag["EffectiveRankFraction"]),
                "BestRankEffectiveRankFraction": float(best_rank["EffectiveRankFraction"]),
                "BestRank_DiagonalEnergyShare": float(best_rank["DiagonalEnergyShare"]),
                "CurrentProjectionCoupledDiagonalEnergyShare": current_diag,
                "CurrentProjectionCoupledEffectiveRankFraction": current_rank,
                "RequiredNextRoute": "expand_active_parent_operator_source_or_use_separately_frozen_signed_contrast_protocol",
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Active-Triad PSD Ceiling Audit

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

The projection-coupled reduced-Jacobian candidate fixed the missing projection
channel, but failed because its PSD lift remained diagonal-dominated and
low-rank. This audit asks whether that failure is an accident of the chosen
minimal weights or a structural ceiling of the current active reduced triad.

The active triad is:

```text
Phi = TEMPLATE_PHI_PARENT_SOURCE
B   = TEMPLATE_B_BRANCH_RESPONSE
P   = TEMPLATE_P_MORPH_PROJECTION
```

## Target-Blind Scan

The audit scans deterministic off-diagonal triad source shapes:

```text
J = a |Phi><B| + b |Phi><P| + c |B><P| + transpose
```

with `a`, `b`, and `c` selected from a fixed no-score grid. The PSD lift is:

```text
C = J J^T / ||J J^T||_F
```

This is a structural ceiling audit only. It uses no target residuals, no score
outcomes, and no family gains.

## Result

- scanned rows: `{len(table)}`
- joint pass rows for diagonal share `<= 0.80` and effective-rank fraction
  `>= 0.30`: `{len(joint_passes)}`
- best diagonal energy share found: `{float(best_diag["DiagonalEnergyShare"])}`
- effective-rank fraction at best diagonal case:
  `{float(best_diag["EffectiveRankFraction"])}`
- best effective-rank fraction found:
  `{float(best_rank["EffectiveRankFraction"])}`
- diagonal energy share at best-rank case:
  `{float(best_rank["DiagonalEnergyShare"])}`

## Interpretation

Within the current three-coordinate active triad, a PSD-lifted covariance
candidate is structurally pushed toward diagonal dominance and marginal rank.
The next Tau-side route should therefore not merely retune the `Phi/B/P`
weights. It must either:

1. introduce a broader parent-side curvature/operator source with additional
   target-blind active support; or
2. open a separately frozen signed-operator-contrast protocol whose claim is
   not PSD covariance survival.

## Claim Boundary

Allowed statement:

> The current active triad is too narrow for the PSD covariance route under the
> existing specificity gates.

Forbidden statement:

> This audit authorizes scoring, tunes a new candidate, or validates Tau Core.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
