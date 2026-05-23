#!/usr/bin/env python3
"""Build a minimal linear dynamical stability packet for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESPONSE_ENERGY = ROOT / "evidence/p_taucov_response_energy_split_summary.csv"
OUT_MODES = ROOT / "evidence/p_taucov_linear_dynamical_stability_modes.csv"
OUT_GATES = ROOT / "evidence/p_taucov_linear_dynamical_stability_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_linear_dynamical_stability_summary.csv"
DOC = ROOT / "docs/p_taucov_linear_dynamical_stability_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_LINEAR_DYNAMICAL_STABILITY_PACKET_v1"
CLAIM_BOUNDARY = "linear_dynamical_stability_no_scoring"


def main() -> int:
    response_energy = pd.read_csv(RESPONSE_ENERGY).iloc[0]

    # Minimal stable microscopic branch dynamics:
    # L = 1/2 dot(B)^2 - 1/2 B^2 - B J.
    # Around the stationary branch B_*=-J, the fluctuation b obeys
    # b_ddot + b = 0.  The static Schur response remains -1/2 J^2.
    kinetic = np.array([[1.0]])
    stiffness = np.array([[1.0]])
    omega_sq = np.linalg.eigvals(np.linalg.solve(kinetic, stiffness)).real
    omega = np.sqrt(omega_sq)
    static_response_min_eig = float(response_energy["MinEffectiveResponseEigenvalue"])
    static_response_preserved = static_response_min_eig < 0.0
    positive_kinetic = float(np.linalg.eigvalsh(kinetic).min()) > 0.0
    positive_stiffness = float(np.linalg.eigvalsh(stiffness).min()) > 0.0
    bounded_modes = bool((omega_sq > 0.0).all())

    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "ModeID": "B_branch_fluctuation",
                "KineticEigenvalue": float(kinetic[0, 0]),
                "StiffnessEigenvalue": float(stiffness[0, 0]),
                "OmegaSquared": float(omega_sq[0]),
                "Omega": float(omega[0]),
                "BoundedLinearMode": bool(omega_sq[0] > 0.0),
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_MODES, index=False)

    gates = [
        ("LDS-G1_RESPONSE_ENERGY_SPLIT_AVAILABLE", str(response_energy["Status"]).endswith("PASS_NO_SCORING"), 1.0),
        ("LDS-G2_POSITIVE_KINETIC_FORM", positive_kinetic, float(np.linalg.eigvalsh(kinetic).min())),
        ("LDS-G3_POSITIVE_STIFFNESS_FORM", positive_stiffness, float(np.linalg.eigvalsh(stiffness).min())),
        ("LDS-G4_BOUNDED_LINEAR_MODE", bounded_modes, float(omega_sq.min())),
        ("LDS-G5_STATIC_RESPONSE_PRESERVED", static_response_preserved, static_response_min_eig),
        ("LDS-G6_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
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
        "P_TAUCOV_LINEAR_DYNAMICAL_STABILITY_PASS_NO_SCORING"
        if passed_count == len(gates_df)
        else "P_TAUCOV_LINEAR_DYNAMICAL_STABILITY_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates_df),
                "MinKineticEigenvalue": float(np.linalg.eigvalsh(kinetic).min()),
                "MinStiffnessEigenvalue": float(np.linalg.eigvalsh(stiffness).min()),
                "MinOmegaSquared": float(omega_sq.min()),
                "BoundedLinearModes": bounded_modes,
                "StaticResponsePreserved": static_response_preserved,
                "StillOpen": "NONLINEAR_STABILITY;MICROSCOPIC_UV_COMPLETION;EMPIRICAL_SCORING_AUTHORIZATION",
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
                "# P-TauCov Linear Dynamical Stability Packet",
                "",
                f"Status: `{status}`.",
                "",
                "This packet supplies the minimal linear dynamics needed to interpret",
                "the signed reduced response as compatible with a stable microscopic",
                "branch mode.",
                "",
                "## Minimal Dynamics",
                "",
                "```math",
                "L = \\frac{1}{2}\\dot B^2 - \\frac{1}{2}B^2 - BJ.",
                "```",
                "",
                "At the stationary branch value `B_*=-J`, the fluctuation `b=B-B_*`",
                "obeys",
                "",
                "```math",
                "\\ddot b + b = 0.",
                "```",
                "",
                "Thus the microscopic branch fluctuation is linearly bounded while",
                "the static elimination still gives the signed response",
                "`E_eff(J)=-J^2/2`.",
                "",
                "## Key Numbers",
                "",
                f"- minimum kinetic eigenvalue: `{float(np.linalg.eigvalsh(kinetic).min())}`",
                f"- minimum stiffness eigenvalue: `{float(np.linalg.eigvalsh(stiffness).min())}`",
                f"- minimum omega squared: `{float(omega_sq.min())}`",
                f"- gates passed: `{passed_count}/{len(gates_df)}`",
                "",
                "## Claim Boundary",
                "",
                "Allowed: the minimal branch response can be embedded in a linearly",
                "stable one-mode microscopic dynamics.",
                "",
                "Forbidden: this is not nonlinear stability, not a UV completion, not",
                "a covariance scorecard, and not measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
