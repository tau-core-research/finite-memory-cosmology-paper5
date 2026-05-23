#!/usr/bin/env python3
"""Validate the P-TauCov protocol draft artifacts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_branch_localized_covariance_protocol.md"
GATES = ROOT / "evidence/p_taucov_protocol_gate_registry.csv"
CONTROLS = ROOT / "evidence/p_taucov_control_registry.csv"
STATUS = ROOT / "evidence/p_taucov_status_boundary.csv"
OUT = ROOT / "evidence/p_taucov_protocol_validation.csv"


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_PROTOCOL_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("gate_registry_exists", GATES.exists())
    add("control_registry_exists", CONTROLS.exists())
    add("status_boundary_exists", STATUS.exists())
    if not all(path.exists() for path in [DOC, GATES, CONTROLS, STATUS]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_PROTOCOL_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    for phrase in [
        "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1",
        "T_{\\tau}",
        "\\delta C_{\\tau}",
        "W_branch or Omega_branch",
        "W_{\\rm branch}(i,j)",
        "S_{\\tau}",
        "outside-branch",
        "shuffled",
        "morphology-null",
        "projection-null",
        "generic covariance baselines",
        "This document is a protocol and claim-boundary artifact",
        "P5C v3 remains:",
        "anomaly candidate only",
        "not a full Tau Core validation",
        "V4KernelAuthorized: false unless P-TauCov branch support is frozen",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    gates = pd.read_csv(GATES)
    controls = pd.read_csv(CONTROLS)
    status = pd.read_csv(STATUS)
    add("ten_gates_declared", len(gates) == 10)
    add("all_gates_required_before_scoring", gates["RequiredBeforeScoring"].astype(bool).all())
    add("outside_branch_control_declared", "OUTSIDE_BRANCH" in set(controls["ControlID"]))
    add("shuffled_control_declared", "SHUFFLED_SUPPORT" in set(controls["ControlID"]))
    add("morphology_null_declared", "MORPHOLOGY_NULL" in set(controls["ControlID"]))
    add("projection_null_declared", "PROJECTION_NULL" in set(controls["ControlID"]))
    add("generic_family_permuted_declared", "GENERIC_FAMILY_PERMUTED" in set(controls["ControlID"]))
    add("v4_not_authorized", status.loc[status["Item"].eq("V4_scoring"), "Status"].iloc[0] == "NOT_AUTHORIZED")
    add(
        "p5c_v3_anomaly_only",
        status.loc[status["Item"].eq("P5C_v3"), "Meaning"].iloc[0] == "Anomaly candidate only",
    )

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_PROTOCOL_INVALID")
        print(failed.to_string(index=False))
        return 1
    print("P_TAUCOV_PROTOCOL_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
