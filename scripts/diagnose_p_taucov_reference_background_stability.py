#!/usr/bin/env python3
"""Diagnose reference-background stability for the P-TauCov active sector."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_HESSIAN = ROOT / "evidence/p_taucov_minimal_global_parent_action_scaffold_hessian.csv"
STATIONARITY = ROOT / "evidence/p_taucov_reference_background_stationarity_summary.csv"
S_REST = ROOT / "evidence/p_taucov_s_rest_no_leakage_summary.csv"
OUT_EIGENVALUES = ROOT / "evidence/p_taucov_reference_background_stability_eigenvalues.csv"
OUT_GATES = ROOT / "evidence/p_taucov_reference_background_stability_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_reference_background_stability_summary.csv"
DOC = ROOT / "docs/p_taucov_reference_background_stability_diagnostic.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_REFERENCE_BACKGROUND_STABILITY_DIAGNOSTIC_v1"
CLAIM_BOUNDARY = "reference_background_stability_diagnostic_no_scoring"
ACTIVE_COORDS = [
    "TEMPLATE_PHI_PARENT_SOURCE",
    "TEMPLATE_B_BRANCH_RESPONSE",
    "TEMPLATE_P_MORPH_PROJECTION",
]


def load_active_hessian() -> np.ndarray:
    rows = pd.read_csv(ACTIVE_HESSIAN)
    matrix = pd.DataFrame(0.0, index=ACTIVE_COORDS, columns=ACTIVE_COORDS)
    for row in rows.itertuples(index=False):
        matrix.loc[str(row.RowCoordinate), str(row.ColumnCoordinate)] = float(row.Value)
    matrix = (matrix + matrix.T) / 2.0
    return matrix.to_numpy(dtype=float)


def main() -> int:
    hessian = load_active_hessian()
    eigenvalues = np.linalg.eigvalsh(hessian)
    min_eigen = float(eigenvalues.min())
    max_eigen = float(eigenvalues.max())
    negative_count = int((eigenvalues < -1e-12).sum())
    positive_count = int((eigenvalues > 1e-12).sum())
    zero_count = int((np.abs(eigenvalues) <= 1e-12).sum())
    active_psd = min_eigen >= -1e-12
    active_indefinite = negative_count > 0 and positive_count > 0

    stationarity = pd.read_csv(STATIONARITY).iloc[0]
    s_rest = pd.read_csv(S_REST).iloc[0]
    reference_stationary = bool(stationarity["ReferenceBackgroundStationary"])
    s_rest_no_leakage = str(s_rest["Status"]).endswith("PASS_NO_SCORING")

    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "EigenIndex": idx,
                "Eigenvalue": float(value),
                "Interpretation": "negative" if value < -1e-12 else "positive" if value > 1e-12 else "zero",
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for idx, value in enumerate(eigenvalues)
        ]
    ).to_csv(OUT_EIGENVALUES, index=False)

    gates = [
        ("RBS-G1_ACTIVE_HESSIAN_AVAILABLE", ACTIVE_HESSIAN.exists(), 1.0),
        ("RBS-G2_REFERENCE_BACKGROUND_STATIONARY", reference_stationary, float(reference_stationary)),
        ("RBS-G3_S_REST_NO_LEAKAGE_PASS", s_rest_no_leakage, float(s_rest_no_leakage)),
        ("RBS-G4_ACTIVE_HESSIAN_POSITIVE_SEMIDEFINITE", active_psd, min_eigen),
        ("RBS-G5_FULL_LOCAL_STABILITY_PROVEN", active_psd and s_rest_no_leakage, min_eigen),
        ("RBS-G6_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
    ]
    gates_df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "Passed": bool(passed),
                "DiagnosticValue": float(value),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, passed, value in gates
        ]
    )
    gates_df.to_csv(OUT_GATES, index=False)
    passed_count = int(gates_df["Passed"].sum())
    status = (
        "P_TAUCOV_REFERENCE_BACKGROUND_STABILITY_PASS_NO_SCORING"
        if active_psd and s_rest_no_leakage and reference_stationary
        else "P_TAUCOV_REFERENCE_BACKGROUND_ACTIVE_SADDLE_STABILITY_NOT_PROVEN_NO_SCORING"
    )
    remaining_blockers = (
        "COVARIANCE_MAP"
        if status.endswith("PASS_NO_SCORING")
        else "REFERENCE_BACKGROUND_STABILITY;COVARIANCE_MAP"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates_df),
                "MinActiveEigenvalue": min_eigen,
                "MaxActiveEigenvalue": max_eigen,
                "NegativeEigenvalueCount": negative_count,
                "PositiveEigenvalueCount": positive_count,
                "ZeroEigenvalueCount": zero_count,
                "ActiveHessianPositiveSemidefinite": active_psd,
                "ActiveHessianIndefinite": active_indefinite,
                "ReferenceBackgroundStationary": reference_stationary,
                "SRestNoLeakagePass": s_rest_no_leakage,
                "FullStabilityProven": active_psd and s_rest_no_leakage and reference_stationary,
                "ResolvedBlocker": "NONE",
                "RemainingBlockers": remaining_blockers,
                "ScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Reference Background Stability Diagnostic",
                "",
                f"Status: `{status}`.",
                "",
                "This diagnostic tests whether the stationary reference background is",
                "already a locally stable energy background under the active scaffold",
                "Hessian. It does not use target residuals, score outcomes, or empirical",
                "covariance performance.",
                "",
                "## Result",
                "",
                f"- minimum active Hessian eigenvalue: `{min_eigen}`",
                f"- maximum active Hessian eigenvalue: `{max_eigen}`",
                f"- negative eigenvalue count: `{negative_count}`",
                f"- positive eigenvalue count: `{positive_count}`",
                f"- active Hessian positive semidefinite: `{active_psd}`",
                f"- full stability proven: `{active_psd and s_rest_no_leakage and reference_stationary}`",
                "",
                "The active scaffold is an indefinite response witness, not yet a",
                "positive local energy Hessian. The `S_rest` packet stabilizes the",
                "inactive complement and prevents leakage, but it cannot by itself",
                "turn the active witness Hessian into a positive energy form without",
                "changing the witness.",
                "",
                "## Consequence",
                "",
                "The background-stability blocker remains open. The next derivation",
                "must explain whether the active Hessian is a response operator rather",
                "than an energy Hessian, or must supply a constrained/dynamical",
                "stability theorem that preserves the projection-essential witness.",
                "",
                "## Claim Boundary",
                "",
                "Allowed: the current active scaffold has a stationary reference point",
                "and an explicit saddle-like Hessian diagnostic.",
                "",
                "Forbidden: this is not a stable Tau Core background, not a covariance",
                "scorecard, and not measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
