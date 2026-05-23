#!/usr/bin/env python3
"""Build the P-TauCov delta_C_Tau construction contract.

This is a pre-scoring contract. It declares the allowed construction path for a
future Tau-derived covariance-response object and records the inputs that are
forbidden because they would leak the P5C v3 outcome back into the prediction.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_delta_c_tau_contract.md"
OUT_CSV = EVIDENCE / "p_taucov_delta_c_tau_contract.csv"
OUT_YAML = EVIDENCE / "p_taucov_delta_c_tau_contract.yaml"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
CONTRACT_ID = "P_TAUCOV_DELTA_C_TAU_CONSTRUCTION_CONTRACT_v1"
CLAIM_BOUNDARY = "delta_c_tau_contract_no_scoring_authorization_no_empirical_claim"


ROWS = [
    {
        "Item": "ProtocolID",
        "Requirement": PROTOCOL_ID,
        "Status": "DECLARED",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "ContractID",
        "Requirement": CONTRACT_ID,
        "Status": "CONTRACT_ONLY",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "BranchEquation",
        "Requirement": "B_equals_B_star_of_Phi_and_delta_B_star_equals_minus_inverse_LBred_DPhi_FB_deltaPhi",
        "Status": "REQUIRED",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "ProjectedMorphology",
        "Requirement": "M_proj_equals_P_morph_M_parent",
        "Status": "REQUIRED",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "TauMorphologyResponse",
        "Requirement": "T_tau_equals_DPhi_Mproj_minus_DB_Mproj_inverse_LBred_DPhi_FB",
        "Status": "REQUIRED",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "CovarianceResponse",
        "Requirement": "delta_C_Tau_equals_D_M_C_of_T_tau_deltaPhi",
        "Status": "REQUIRED",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "AdmissibleInputs",
        "Requirement": "Phi_grid_B_star_rule_LBred_DPhi_FB_P_morph_M_parent_D_M_C",
        "Status": "MUST_BE_FROZEN",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "ForbiddenTargets",
        "Requirement": "held_out_residuals_v3_gain_pattern_dominant_family_oos_deltaNLL_signed_diagnostic",
        "Status": "HARD_BLOCK",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "OutputMatrix",
        "Requirement": "delta_C_Tau_square_symmetric_indexed_on_frozen_observable_coordinates",
        "Status": "FUTURE_REQUIRED",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "OutputNormalization",
        "Requirement": "frobenius_norm_or_trace_norm_frozen_before_branch_support",
        "Status": "MUST_BE_FROZEN",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "LeakageAudit",
        "Requirement": "prove_no_target_residual_or_v3_outcome_inputs_used",
        "Status": "REQUIRED",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "BranchSupportAuthorization",
        "Requirement": "forbidden_until_concrete_delta_C_Tau_hash_and_normalization_are_frozen",
        "Status": "NOT_AUTHORIZED",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "PTauCovScoringAuthorization",
        "Requirement": "forbidden_by_this_contract",
        "Status": "NOT_AUTHORIZED",
        "RequiredBeforeScoring": True,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
]


def yaml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return f'"{value}"'


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(ROWS)
    df.to_csv(OUT_CSV, index=False)

    with OUT_YAML.open("w", encoding="utf-8") as handle:
        handle.write(f"protocol_id: {yaml_value(PROTOCOL_ID)}\n")
        handle.write(f"contract_id: {yaml_value(CONTRACT_ID)}\n")
        handle.write(f"claim_boundary: {yaml_value(CLAIM_BOUNDARY)}\n")
        handle.write("scoring_authorized: false\n")
        handle.write("branch_support_authorized: false\n")
        handle.write("delta_c_tau_artifact_present: false\n")
        handle.write("rows:\n")
        for row in ROWS:
            handle.write(f"  - item: {yaml_value(row['Item'])}\n")
            handle.write(f"    requirement: {yaml_value(row['Requirement'])}\n")
            handle.write(f"    status: {yaml_value(row['Status'])}\n")
            handle.write(f"    required_before_scoring: {yaml_value(row['RequiredBeforeScoring'])}\n")
            handle.write(f"    scoring_authorized: {yaml_value(row['ScoringAuthorized'])}\n")

    OUT_DOC.write_text(
        """# P-TauCov delta_C_Tau Construction Contract

Status: construction contract / no branch-support freeze / no scoring
authorization.

This document defines the only admissible construction path for the future
`delta_C_Tau` artifact used by P-TauCov. It does not compute `delta_C_Tau`; it
locks the rule that must be satisfied before `W_branch`, `Omega_branch`, or
`S_tau` can be evaluated.

## 1. Required Branch Equation

The reduced branch must be declared as:

```math
B = B_*(\\Phi),
```

with first-order branch response:

```math
\\delta B_*
=
- (L_B^{\\rm red})^{-1} D_\\Phi F_B[\\delta\\Phi].
```

`L_B^{red}` must be invertible only on the declared reduced branch domain. Any
null space, gauge direction, or excluded mode must be declared before scoring.

## 2. Required Projected Morphology

The observable morphology map must have the declared form:

```math
M_{\\rm proj}(\\Phi,B)
=
P_{\\rm morph}(\\Phi,B)M_{\\rm parent}(\\Phi,B).
```

`P_morph`, `M_parent`, and the observable coordinate index must be frozen before
the response is converted into covariance space.

## 3. Required Tau Morphology Response

The only admissible Tau morphology response is:

```math
T_{\\tau}
=
D_\\Phi M_{\\rm proj}
-
D_B M_{\\rm proj}(L_B^{\\rm red})^{-1}D_\\Phi F_B.
```

The second term is mandatory. Dropping it converts the test into a generic
morphology response and invalidates P-TauCov.

## 4. Required Covariance Response

The predicted covariance response must be constructed as:

```math
\\delta C_{\\tau}
=
D_M C[T_{\\tau}\\delta\\Phi].
```

The output must be a square symmetric response matrix indexed on the frozen
observable coordinates. Its normalization must be frozen before branch support
is computed.

## 5. Allowed Inputs

Allowed inputs are limited to:

```text
Phi grid or perturbation family;
B_star rule;
L_B^red;
D_Phi F_B;
P_morph;
M_parent;
D_M C;
frozen observable coordinate index;
normalization convention.
```

## 6. Forbidden Inputs

The construction must not use:

```text
held-out residuals;
P5C v3 family-localized gain pattern;
dominant positive family;
observed OOS DeltaNLL pattern;
signed diagnostic advantage;
failed family-permutation gate;
post-score branch choice.
```

## 7. Authorization Boundary

This contract does not authorize scoring. It also does not authorize a concrete
branch-support freeze until a hashed `delta_C_Tau` artifact and its
normalization are present.

Allowed statement:

```text
The construction path for a future Tau-derived covariance-response artifact is
predeclared.
```

Forbidden statement:

```text
P-TauCov has already demonstrated a Tau-specific covariance response.
```

## 8. Next Valid Step

The next valid step is a target-blind generator that produces:

```text
evidence/p_taucov_delta_c_tau.csv
evidence/p_taucov_delta_c_tau.yaml
evidence/p_taucov_delta_c_tau.sha256
docs/p_taucov_delta_c_tau_freeze.md
```

Only after that can `q_branch`, `W_branch`, and `Omega_branch` be frozen.
""",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DOC}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_YAML}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
