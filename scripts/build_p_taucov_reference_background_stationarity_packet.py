#!/usr/bin/env python3
"""Build the reference-background stationarity packet."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "evidence/p_taucov_full_action_domain_null_gauge_summary.csv"
OUT_BACKGROUND = ROOT / "evidence/p_taucov_reference_background_stationarity.csv"
OUT_GATES = ROOT / "evidence/p_taucov_reference_background_stationarity_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_reference_background_stationarity_summary.csv"
DOC = ROOT / "docs/p_taucov_reference_background_stationarity_packet_result.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_REFERENCE_BACKGROUND_STATIONARITY_PACKET_v1"
CLAIM_BOUNDARY = "reference_background_stationarity_no_scoring"


def main() -> int:
    domain = pd.read_csv(DOMAIN).iloc[0]
    coords = ["Phi", "B", "P"]
    values = {"Phi": 0.0, "B": 0.0, "P": 0.0}
    phi = values["Phi"]
    b = values["B"]
    p = values["P"]
    gradients = {
        "dV_dB": -b - 2.0 * p,
        "dV_dP": -2.0 * b - phi,
        "dV_dPhi": -p,
    }
    background_rows = []
    for coord in coords:
        background_rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Coordinate": coord,
                "ReferenceValue": values[coord],
                "Role": "active_reference_background",
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    for grad_id, value in gradients.items():
        background_rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Coordinate": grad_id,
                "ReferenceValue": value,
                "Role": "active_gradient_at_reference",
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    pd.DataFrame(background_rows).to_csv(OUT_BACKGROUND, index=False)

    grad_norm = float(np.linalg.norm(list(gradients.values())))
    gates = [
        ("RB-G1_DOMAIN_PACKET_VALID", str(domain["Status"]).endswith("PASS_NO_SCORING"), 1.0),
        ("RB-G2_ACTIVE_REFERENCE_ORIGIN_DECLARED", all(values[c] == 0.0 for c in coords), 1.0),
        ("RB-G3_ACTIVE_GRADIENT_ZERO", grad_norm < 1e-12, grad_norm),
        ("RB-G4_STABILITY_DEFERRED_TO_S_REST", True, 1.0),
        ("RB-G5_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
    ]
    gates_df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate,
                "Passed": bool(passed),
                "DiagnosticValue": float(value),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate, passed, value in gates
        ]
    )
    gates_df.to_csv(OUT_GATES, index=False)
    passed_count = int(gates_df["Passed"].sum())
    status = (
        "P_TAUCOV_REFERENCE_BACKGROUND_STATIONARY_STABILITY_DEFERRED_NO_SCORING"
        if passed_count == len(gates_df)
        else "P_TAUCOV_REFERENCE_BACKGROUND_STATIONARITY_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates_df),
                "GradientNormAtReference": grad_norm,
                "ReferenceBackgroundStationary": grad_norm < 1e-12,
                "FullStabilityProven": False,
                "ResolvedBlocker": "REFERENCE_BACKGROUND_STATIONARITY",
                "RemainingBlocker": "REFERENCE_BACKGROUND_STABILITY_REQUIRES_S_REST",
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
                "# P-TauCov Reference Background Stationarity Result",
                "",
                f"Status: `{status}`.",
                "",
                "The active scaffold has a stationary reference background at",
                "`Phi=P=B=0`. Full stability is not claimed; it is deferred to the",
                "`S_rest` embedding gate.",
                "",
                "## Key Numbers",
                "",
                f"- gradient norm at reference: `{grad_norm}`",
                f"- full stability proven: `False`",
                "",
                "No scoring or measurement validation is authorized.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
