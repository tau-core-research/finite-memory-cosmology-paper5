#!/usr/bin/env python3
"""Freeze concrete epsilon-P3 branch support from delta_C_tau only."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "data/p_taucov/linear/coordinate_basis.csv"
P3 = ROOT / "data/p_taucov/linear/P3_core_mixing_operator.csv"
FREEZE = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_freeze.csv"
WEIGHTS = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_weights.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_summary.csv"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_freeze.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_freeze.sha256"
DOC = ROOT / "docs/p_taucov_epsilon_p3_branch_support_freeze.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EPSILON_P3_BRANCH_SUPPORT_FREEZE_v1"
Q_BRANCH = 0.80


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_matrix(path: Path, ids: list[str]) -> np.ndarray:
    df = pd.read_csv(path)
    if list(df.columns) != ["coordinate_id"] + ids:
        raise ValueError(f"Unexpected matrix columns in {path}")
    return df[ids].astype(float).to_numpy()


def main() -> int:
    for path in [BASIS, P3]:
        if not path.exists():
            raise FileNotFoundError(f"Missing required input: {path.relative_to(ROOT)}")

    basis = pd.read_csv(BASIS)
    ids = basis["coordinate_id"].astype(str).tolist()
    p3 = read_matrix(P3, ids)
    delta = p3 @ p3.T
    abs_delta = np.abs(delta)
    total = float(abs_delta.sum())
    if total <= 0.0:
        raise ValueError("delta_C_tau mass is zero; cannot freeze branch support")
    weights = abs_delta / total

    flat = []
    for i, row_id in enumerate(ids):
        for j, col_id in enumerate(ids):
            flat.append(
                {
                    "ProtocolID": PROTOCOL_ID,
                    "FreezeID": FREEZE_ID,
                    "RowCoordinate": row_id,
                    "ColumnCoordinate": col_id,
                    "DeltaCTau": float(delta[i, j]),
                    "AbsDeltaCTau": float(abs_delta[i, j]),
                    "WBranch": float(weights[i, j]),
                }
            )
    weights_df = pd.DataFrame(flat)
    weights_df = weights_df.sort_values(["WBranch", "RowCoordinate", "ColumnCoordinate"], ascending=[False, True, True]).reset_index(drop=True)
    weights_df["CumulativeMass"] = weights_df["WBranch"].cumsum()
    selected = weights_df["CumulativeMass"].le(Q_BRANCH) | weights_df["CumulativeMass"].shift(fill_value=0.0).lt(Q_BRANCH)
    weights_df["OmegaBranch"] = selected
    weights_df["q_branch"] = Q_BRANCH
    weights_df["BranchSupportSource"] = "delta_C_Tau_only"
    weights_df["UsesTargetResiduals"] = False
    weights_df["UsesP5Cv3Outcome"] = False
    weights_df["PTauCovScoringAuthorized"] = False
    weights_df.to_csv(WEIGHTS, index=False)

    selected_df = weights_df[weights_df["OmegaBranch"]].copy()
    selected_df.to_csv(FREEZE, index=False)

    label_ids = set(basis.loc[basis["coordinate_family"].isin(["ExternalMetadata", "CoordinateConvention"]), "coordinate_id"].astype(str))
    label_selected = selected_df["RowCoordinate"].isin(label_ids) | selected_df["ColumnCoordinate"].isin(label_ids)
    selected_mass = float(selected_df["WBranch"].sum())
    label_mass = float(selected_df.loc[label_selected, "WBranch"].sum())
    selected_rows = int(len(selected_df))
    status = "FROZEN_BRANCH_SUPPORT_NO_SCORING" if selected_mass >= Q_BRANCH and label_mass == 0.0 else "BLOCKED"

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "q_branch": Q_BRANCH,
                "SelectedCells": selected_rows,
                "SelectedMass": selected_mass,
                "LabelOrConventionMass": label_mass,
                "BranchSupportSource": "delta_C_Tau_only",
                "UsesTargetResiduals": False,
                "UsesP5Cv3Outcome": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": "epsilon_p3_branch_support_frozen_no_empirical_scoring_no_tau_signal_claim",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "FreezeID": FREEZE_ID,
        "Status": status,
        "q_branch": Q_BRANCH,
        "SelectedCells": selected_rows,
        "SelectedMass": selected_mass,
        "BranchSupportSource": "delta_C_Tau_only",
        "DeltaCTauSource": "P3_core_mixing_operator_times_transpose",
        "OperatorFile": str(P3.relative_to(ROOT)),
        "CoordinateBasisFile": str(BASIS.relative_to(ROOT)),
        "WeightsFile": str(WEIGHTS.relative_to(ROOT)),
        "SelectedSupportFile": str(FREEZE.relative_to(ROOT)),
        "TargetResidualsUsed": False,
        "P5CV3OutcomeUsed": False,
        "PTauCovScoringAuthorized": False,
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": "epsilon_p3_branch_support_frozen_no_empirical_scoring_no_tau_signal_claim",
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA256.write_text(
        "\n".join(f"{file_sha256(path)}  {path.relative_to(ROOT)}" for path in [FREEZE, WEIGHTS, SUMMARY, MANIFEST]) + "\n",
        encoding="utf-8",
    )

    DOC.write_text(
        f"""# P-TauCov Epsilon-P3 Branch-Support Freeze

Status: `{status}`.

This artifact freezes concrete branch support for the epsilon-P3 P-TauCov
candidate. The support is derived only from the frozen P3 covariance response:

```text
delta_C_tau = P3 P3^T
W_branch(i,j) = |delta_C_tau(i,j)| / sum_ab |delta_C_tau(a,b)|
q_branch = {Q_BRANCH}
Omega_branch = smallest W_branch-ranked set carrying at least q_branch mass
```

## Result

```text
SelectedCells: {selected_rows}
SelectedMass: {selected_mass:.12g}
LabelOrConventionMass: {label_mass:.12g}
BranchSupportSource: delta_C_Tau_only
PTauCovScoringAuthorized: false
```

## Claim Boundary

Allowed statement:

```text
The epsilon-P3 branch support is frozen from delta_C_tau only.
```

Forbidden statement:

```text
This support freeze is an empirical P-TauCov score, survival result, or Tau
signal.
```
""",
        encoding="utf-8",
    )

    for path in [FREEZE, WEIGHTS, SUMMARY, MANIFEST, SHA256, DOC]:
        print(f"Wrote {path.relative_to(ROOT)}")
    if status != "FROZEN_BRANCH_SUPPORT_NO_SCORING":
        print("P_TAUCOV_EPSILON_P3_BRANCH_SUPPORT_BLOCKED")
        return 1
    print("P_TAUCOV_EPSILON_P3_BRANCH_SUPPORT_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
