#!/usr/bin/env python3
"""Build observed-input contract for epsilon-P3 P-TauCov scoring."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
BRANCH = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_weights.csv"
P5C_ROWS = ROOT / "evidence/p5c_kernel_covariance_oos_scorecard_v3.csv"
BRIDGE = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.yaml"
DOC = ROOT / "docs/p_taucov_epsilon_p3_observed_input_contract.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_observed_input_contract.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_observed_input_contract.sha256"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_observed_input_contract_summary.csv"
SCHEMA = ROOT / "evidence/p_taucov_epsilon_p3_observed_input_contract_schema.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
CONTRACT_ID = "P_TAUCOV_EPSILON_P3_OBSERVED_INPUT_CONTRACT_v1"
CLAIM_BOUNDARY = "epsilon_p3_observed_input_contract_shape_blocked_no_scoring"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not BRANCH.exists():
        raise FileNotFoundError(f"Missing branch support weights: {BRANCH.relative_to(ROOT)}")

    branch = pd.read_csv(BRANCH)
    tau_ids = sorted(set(branch["RowCoordinate"].astype(str)) | set(branch["ColumnCoordinate"].astype(str)))
    tau_dimension = len(tau_ids)
    p5c_rows = pd.read_csv(P5C_ROWS) if P5C_ROWS.exists() else pd.DataFrame()
    p5c_dimension = int(len(p5c_rows)) if not p5c_rows.empty else 0
    bridge_ready = BRIDGE.exists()
    status = "BRIDGE_READY_CONTRACT_NO_SCORING" if bridge_ready else "BLOCKED_COORDINATE_SPACE_MISMATCH"

    schema = pd.DataFrame(
        [
            ("ObservedInputID", "string", "fixed id for observed input matrix"),
            ("RowCoordinate", "string", "must match frozen Tau-coordinate IDs"),
            ("ColumnCoordinate", "string", "must match frozen Tau-coordinate IDs"),
            ("ObservedWhitenedCovarianceResidual", "float", "held-out whitened covariance residual value"),
            ("UsesTargetResiduals", "boolean", "true only inside final authorized scorecard input"),
            ("InputFrozenBeforeScoring", "boolean", "must be true before final scoring authorization"),
        ],
        columns=["Field", "Type", "Requirement"],
    )
    schema.insert(0, "ProtocolID", PROTOCOL_ID)
    schema.insert(1, "ContractID", CONTRACT_ID)
    schema["ClaimBoundary"] = CLAIM_BOUNDARY
    schema.to_csv(SCHEMA, index=False)

    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "ContractID": CONTRACT_ID,
        "Status": status,
        "RequiredObservedMatrix": "evidence/p_taucov_epsilon_p3_observed_input_matrix.csv",
        "RequiredCoordinateSpace": "P-TauCov Tau-coordinate basis",
        "RequiredDimension": tau_dimension,
        "AvailableP5Cv3ScorecardRows": p5c_dimension,
        "ShapeCompatibility": bool(bridge_ready),
        "Reason": (
            "target-blind coordinate bridge is frozen; scorecard may project Tau-coordinate delta_C_tau into family-clock space after final authorization"
            if bridge_ready
            else "P3 branch support lives in 8-dimensional Tau-coordinate space, while available P5C empirical covariance rows live in family-clock scorecard space."
        ),
        "RequiredBridge": "freeze_target_blind_coordinate_bridge_from_tau_coordinate_space_to_empirical_family_clock_space",
        "PTauCovScoringAuthorized": False,
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA256.write_text(
        "\n".join(f"{file_sha256(path)}  {path.relative_to(ROOT)}" for path in [SCHEMA, MANIFEST]) + "\n",
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "ContractID": CONTRACT_ID,
                "Status": status,
                "RequiredDimension": tau_dimension,
                "AvailableP5Cv3ScorecardRows": p5c_dimension,
                "ShapeCompatibility": bool(bridge_ready),
                "PTauCovScoringAuthorized": False,
                "NextStep": manifest["RequiredBridge"],
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        f"""# P-TauCov Epsilon-P3 Observed Input Contract

Status: `{status}`.

This contract defines the observed input required by the frozen epsilon-P3
scorecard.

The required scorecard input is a long-form matrix:

```text
RowCoordinate
ColumnCoordinate
ObservedWhitenedCovarianceResidual
```

The coordinate IDs must match the frozen P-TauCov Tau-coordinate support.

## Current Blocker

```text
RequiredDimension: {tau_dimension}
AvailableP5Cv3ScorecardRows: {p5c_dimension}
ShapeCompatibility: {str(bool(bridge_ready)).lower()}
```

The P3 branch support is defined in Tau-coordinate space. Empirical scoring
requires the frozen target-blind coordinate bridge before the scorecard can
project the Tau-side response into family-clock space.

Forbidden statement:

```text
The observed input contract authorizes P-TauCov scoring.
```
""",
        encoding="utf-8",
    )
    for path in [SCHEMA, MANIFEST, SHA256, SUMMARY, DOC]:
        print(f"Wrote {path.relative_to(ROOT)}")
    print(f"P_TAUCOV_EPSILON_P3_OBSERVED_INPUT_CONTRACT_{status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
