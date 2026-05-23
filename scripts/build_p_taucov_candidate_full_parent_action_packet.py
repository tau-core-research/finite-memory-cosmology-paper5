#!/usr/bin/env python3
"""Build a first full-parent-action candidate packet for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = ROOT / "evidence/p_taucov_minimal_global_parent_action_scaffold_summary.csv"
GATE = ROOT / "evidence/p_taucov_full_parent_action_embedding_gate.csv"
OUT_PACKET = ROOT / "evidence/p_taucov_candidate_full_parent_action_packet.csv"
OUT_GATES = ROOT / "evidence/p_taucov_candidate_full_parent_action_packet_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_candidate_full_parent_action_packet_summary.csv"
DOC = ROOT / "docs/p_taucov_candidate_full_parent_action_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_CANDIDATE_FULL_PARENT_ACTION_PACKET_v1"
CLAIM_BOUNDARY = "candidate_full_parent_action_packet_no_scoring"


def main() -> int:
    scaffold = pd.read_csv(SCAFFOLD).iloc[0]
    fields = [
        ("PARENT_DOMAIN", "finite eight-coordinate tau response cell; continuum embedding not declared", "partial"),
        ("MEASURE_DMU_TAU", "uniform counting measure on frozen tau-coordinate packet", "declared"),
        ("NORMALIZATION", "Frobenius normalization inherited from projection-essential witness packets", "declared"),
        ("NULL_GAUGE_MODES", "inactive coordinate axes and forbidden morphology/target sector declared as excluded", "partial"),
        ("REDUCED_BRANCH_DOMAIN", "branch coordinate B with reduced metric coefficient -1/2", "declared"),
        ("REFERENCE_BACKGROUND", "local stationary point around Phi=0 P=0 B=0", "partial"),
        ("ACTIVE_SECTOR", "integral dmu_tau[-1/2 B^2 - 2PB - P Phi]", "declared"),
        ("S_REST", "all non-witness sectors held inactive; no microscopic dynamics declared", "partial"),
        ("COVARIANCE_MAP", "inherited empirical bridge/covariance map; full independent D_M C not declared", "partial"),
        ("FORBIDDEN_INPUTS", "target residuals scores alpha behavior dominant-family identity excluded", "declared"),
    ]
    packet = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "FieldID": fid,
                "FieldValue": value,
                "DeclarationStatus": status,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for fid, value, status in fields
        ]
    )
    packet.to_csv(OUT_PACKET, index=False)

    gate_rows = []
    gate_specs = pd.read_csv(GATE)
    declared = set(packet.loc[packet["DeclarationStatus"].eq("declared"), "FieldID"])
    partial = set(packet.loc[packet["DeclarationStatus"].eq("partial"), "FieldID"])
    checks = {
        "EMB-G1": "PARENT_DOMAIN" in declared,
        "EMB-G2": {"MEASURE_DMU_TAU", "NORMALIZATION"}.issubset(declared),
        "EMB-G3": {"NULL_GAUGE_MODES", "REDUCED_BRANCH_DOMAIN"}.issubset(declared),
        "EMB-G4": "REFERENCE_BACKGROUND" in declared,
        "EMB-G5": str(scaffold["Status"]).endswith("PASS_NO_SCORING") and float(scaffold["MaxAbsHessianMinusWitness"]) < 1e-12,
        "EMB-G6": "S_REST" in declared,
        "EMB-G7": "COVARIANCE_MAP" in declared,
        "EMB-G8": not bool(packet["UsesTargetResiduals"].any()) and not bool(packet["UsesScoreOutcome"].any()),
    }
    diagnostic = {
        "EMB-G1": 0.0 if "PARENT_DOMAIN" in partial else 1.0,
        "EMB-G2": 1.0,
        "EMB-G3": 0.0 if "NULL_GAUGE_MODES" in partial else 1.0,
        "EMB-G4": 0.0 if "REFERENCE_BACKGROUND" in partial else 1.0,
        "EMB-G5": float(scaffold["MaxAbsHessianMinusWitness"]),
        "EMB-G6": 0.0 if "S_REST" in partial else 1.0,
        "EMB-G7": 0.0 if "COVARIANCE_MAP" in partial else 1.0,
        "EMB-G8": 1.0,
    }
    for row in gate_specs.itertuples(index=False):
        gate_id = str(row.GateID)
        gate_rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "GateName": row.GateName,
                "Passed": bool(checks[gate_id]),
                "DiagnosticValue": float(diagnostic[gate_id]),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    gates = pd.DataFrame(gate_rows)
    gates.to_csv(OUT_GATES, index=False)
    passed_count = int(gates["Passed"].sum())
    status = (
        "P_TAUCOV_CANDIDATE_FULL_PARENT_ACTION_PACKET_PASS_NO_SCORING"
        if passed_count == len(gates)
        else "P_TAUCOV_CANDIDATE_FULL_PARENT_ACTION_PACKET_BLOCKED_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates),
                "DeclaredFields": int(packet["DeclarationStatus"].eq("declared").sum()),
                "PartialFields": int(packet["DeclarationStatus"].eq("partial").sum()),
                "BlockingFields": ";".join(sorted(partial)),
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
                "# P-TauCov Candidate Full Parent-Action Packet",
                "",
                f"Status: `{status}`.",
                "",
                "This packet attempts to embed the minimal active scaffold in a fuller",
                "parent-action candidate. It is intentionally blocked while required",
                "fields remain partial.",
                "",
                "## Blocking Fields",
                "",
                f"`{';'.join(sorted(partial))}`",
                "",
                "## Key Numbers",
                "",
                f"- gates passed: `{passed_count}/{len(gates)}`",
                f"- declared fields: `{int(packet['DeclarationStatus'].eq('declared').sum())}`",
                f"- partial fields: `{int(packet['DeclarationStatus'].eq('partial').sum())}`",
                "",
                "## Claim Boundary",
                "",
                "Allowed: a candidate full-action packet has been drafted and its",
                "blocking fields are explicit.",
                "",
                "Forbidden: this is not a full Tau Core action, not a covariance",
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
