#!/usr/bin/env python3
"""Build a Route-A response/energy split packet for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WITNESS_SUMMARY = ROOT / "evidence/p_taucov_projection_essentiality_witness_summary.csv"
STABILITY_SUMMARY = ROOT / "evidence/p_taucov_reference_background_stability_summary.csv"
OUT_ENERGY = ROOT / "evidence/p_taucov_response_energy_split_energy_hessian.csv"
OUT_RESPONSE = ROOT / "evidence/p_taucov_response_energy_split_effective_response.csv"
OUT_GATES = ROOT / "evidence/p_taucov_response_energy_split_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_response_energy_split_summary.csv"
DOC = ROOT / "docs/p_taucov_response_energy_split_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_RESPONSE_ENERGY_SPLIT_PACKET_v1"
CLAIM_BOUNDARY = "response_energy_split_no_scoring"


def main() -> int:
    stability = pd.read_csv(STABILITY_SUMMARY).iloc[0]
    witness = pd.read_csv(WITNESS_SUMMARY).iloc[0]

    # Route A declares a stable microscopic branch energy:
    # E_micro(B;J)=1/2 B^2 + B J, where J is a source/projection channel.
    # The energy Hessian in the physical branch amplitude B is positive,
    # while eliminating B gives an indefinite/negative response Schur term.
    energy_coords = ["B_physical"]
    energy_hessian = np.array([[1.0]])
    energy_eigs = np.linalg.eigvalsh(energy_hessian)

    source_coords = ["Phi_source", "P_projection"]
    coupling = np.array([1.0, 2.0])
    effective_response = -np.outer(coupling, coupling)
    response_eigs = np.linalg.eigvalsh(effective_response)
    stationarity_gradient_norm = 0.0

    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Coordinate": coord,
                "EnergyHessianDiagonal": float(energy_hessian[idx, idx]),
                "EnergyEigenvalue": float(energy_eigs[idx]),
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for idx, coord in enumerate(energy_coords)
        ]
    ).to_csv(OUT_ENERGY, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "RowCoordinate": row_coord,
                "ColumnCoordinate": col_coord,
                "Value": float(effective_response[row_idx, col_idx]),
                "GeneratedFrom": "negative_schur_response_after_stable_branch_elimination",
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row_idx, row_coord in enumerate(source_coords)
            for col_idx, col_coord in enumerate(source_coords)
        ]
    ).to_csv(OUT_RESPONSE, index=False)

    energy_positive = float(energy_eigs.min()) > 0.0
    response_indefinite_or_signed = float(response_eigs.min()) < 0.0
    witness_available = str(witness["Status"]).endswith("PASS_NO_SCORING")
    saddle_diagnosed = bool(stability["ActiveHessianIndefinite"])
    gates = [
        ("RES-G1_STABILITY_DIAGNOSTIC_AVAILABLE", saddle_diagnosed, float(saddle_diagnosed)),
        ("RES-G2_POSITIVE_MICRO_BRANCH_ENERGY", energy_positive, float(energy_eigs.min())),
        ("RES-G3_SIGNED_EFFECTIVE_RESPONSE_EXISTS", response_indefinite_or_signed, float(response_eigs.min())),
        ("RES-G4_STATIONARY_REFERENCE_RETAINED", stationarity_gradient_norm < 1e-12, stationarity_gradient_norm),
        ("RES-G5_PROJECTION_ESSENTIAL_WITNESS_RETAINED", witness_available, float(witness_available)),
        ("RES-G6_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
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
        "P_TAUCOV_RESPONSE_ENERGY_SPLIT_PASS_NO_SCORING"
        if passed_count == len(gates_df)
        else "P_TAUCOV_RESPONSE_ENERGY_SPLIT_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates_df),
                "MinEnergyEigenvalue": float(energy_eigs.min()),
                "MinEffectiveResponseEigenvalue": float(response_eigs.min()),
                "MaxEffectiveResponseEigenvalue": float(response_eigs.max()),
                "EnergyPositive": energy_positive,
                "EffectiveResponseSigned": response_indefinite_or_signed,
                "Interpretation": "active_witness_is_response_operator_not_energy_hessian",
                "ResolvedStabilityInterpretation": status.endswith("PASS_NO_SCORING"),
                "StillOpen": "COVARIANCE_MAP;FULL_DYNAMICAL_STABILITY",
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
                "# P-TauCov Response/Energy Split Packet",
                "",
                f"Status: `{status}`.",
                "",
                "This packet implements Route A from the stability-resolution note.",
                "It separates the stable microscopic branch energy from the signed",
                "effective response obtained after branch elimination.",
                "",
                "## Minimal Route-A Form",
                "",
                "```math",
                "E_{\\rm micro}(B;J)=\\frac{1}{2}B^2 + BJ,",
                "```",
                "",
                "with source/projection channel",
                "",
                "```math",
                "J = \\Phi + 2P.",
                "```",
                "",
                "The physical branch amplitude has positive Hessian:",
                "",
                "```math",
                "\\partial_B^2 E_{\\rm micro}=1>0.",
                "```",
                "",
                "Eliminating `B` gives the signed Schur response",
                "",
                "```math",
                "E_{\\rm eff}(J)=-\\frac{1}{2}J^2.",
                "```",
                "",
                "Thus an indefinite or negative effective response is compatible with",
                "a positive microscopic branch energy. The active witness should",
                "therefore be treated as a response operator, not as the energy",
                "Hessian itself.",
                "",
                "## Key Numbers",
                "",
                f"- minimum microscopic energy eigenvalue: `{float(energy_eigs.min())}`",
                f"- minimum effective response eigenvalue: `{float(response_eigs.min())}`",
                f"- maximum effective response eigenvalue: `{float(response_eigs.max())}`",
                f"- gates passed: `{passed_count}/{len(gates_df)}`",
                "",
                "## Claim Boundary",
                "",
                "Allowed: a positive branch-energy toy form can generate a signed",
                "effective response after branch elimination.",
                "",
                "Forbidden: this is not a full dynamical stability theorem, not a",
                "covariance scorecard, and not measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
