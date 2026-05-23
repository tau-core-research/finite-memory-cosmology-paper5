#!/usr/bin/env python3
"""Create the P-TauCov branch-support freeze template.

This script deliberately does not compute a scored support. It creates the
pre-scoring contract that any future W_branch/Omega_branch artifact must obey.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_CSV = EVIDENCE / "p_taucov_branch_support_freeze.csv"
OUT_YAML = EVIDENCE / "p_taucov_branch_support_freeze.yaml"
OUT_DOC = DOCS / "p_taucov_branch_support_freeze.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_BRANCH_SUPPORT_FREEZE_TEMPLATE_v1"
CLAIM_BOUNDARY = "branch_support_template_no_scoring_authorization_no_survival_claim"


ROWS = [
    {
        "Item": "ProtocolID",
        "Value": PROTOCOL_ID,
        "Status": "DECLARED",
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "FreezeID",
        "Value": FREEZE_ID,
        "Status": "TEMPLATE_ONLY",
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "BranchSupportSource",
        "Value": "delta_C_Tau_only",
        "Status": "REQUIRED",
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "DefaultContinuousWeight",
        "Value": "W_branch_ij_abs_delta_C_Tau_normalized_by_total_abs_mass",
        "Status": "DECLARED",
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "DefaultBinarySupport",
        "Value": "Omega_branch_smallest_set_carrying_predeclared_q_branch_response_mass",
        "Status": "DECLARED",
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "q_branch",
        "Value": "NOT_SET",
        "Status": "MUST_BE_FROZEN_BEFORE_SCORING",
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "ForbiddenInputP5Cv3GainPattern",
        "Value": "forbidden",
        "Status": "HARD_BLOCK",
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "ForbiddenInputHeldOutResiduals",
        "Value": "forbidden",
        "Status": "HARD_BLOCK",
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "ForbiddenInputDominantFamily",
        "Value": "forbidden_unless_independently_derived_from_delta_C_Tau",
        "Status": "HARD_BLOCK",
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "P5Cv3Status",
        "Value": "P5C_V3_STRONG_LOCAL_COVARIANCE_SIGNAL_BUT_NO_GLOBAL_SURVIVAL",
        "Status": "ANOMALY_CANDIDATE_ONLY",
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "V4KernelAuthorized",
        "Value": "false",
        "Status": "NOT_AUTHORIZED",
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
    {
        "Item": "PTauCovScoringAuthorized",
        "Value": "false",
        "Status": "NOT_AUTHORIZED",
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    },
]


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return f'"{value}"'


def main() -> int:
    EVIDENCE.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)

    df = pd.DataFrame(ROWS)
    df.to_csv(OUT_CSV, index=False)

    with OUT_YAML.open("w", encoding="utf-8") as handle:
        handle.write(f"protocol_id: {yaml_scalar(PROTOCOL_ID)}\n")
        handle.write(f"freeze_id: {yaml_scalar(FREEZE_ID)}\n")
        handle.write(f"claim_boundary: {yaml_scalar(CLAIM_BOUNDARY)}\n")
        handle.write("scoring_authorized: false\n")
        handle.write("v4_kernel_authorized: false\n")
        handle.write("branch_support_source: delta_C_Tau_only\n")
        handle.write("rows:\n")
        for row in ROWS:
            handle.write(f"  - item: {yaml_scalar(row['Item'])}\n")
            handle.write(f"    value: {yaml_scalar(row['Value'])}\n")
            handle.write(f"    status: {yaml_scalar(row['Status'])}\n")
            handle.write(f"    scoring_authorized: {yaml_scalar(row['ScoringAuthorized'])}\n")
            handle.write(f"    claim_boundary: {yaml_scalar(row['ClaimBoundary'])}\n")

    OUT_DOC.write_text(
        """# P-TauCov Branch-Support Freeze Template

Status: template only / no scoring authorization.

This artifact is the pre-scoring branch-support contract for
`P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1`.

It does not compute `W_branch` or `Omega_branch`. It specifies the admissible
source and the hard exclusions that must remain in force when a future branch
support is actually frozen.

## Required Source

The only admissible support source is:

```text
delta_C_Tau_only
```

The default continuous support weight is:

```math
W_{\\rm branch}(i,j)
=
\\frac{|\\delta C_{\\tau}(i,j)|}
{\\sum_{a,b}|\\delta C_{\\tau}(a,b)|}.
```

The default binary support is the smallest set carrying a predeclared response
mass fraction `q_branch`. In this template `q_branch` is deliberately `NOT_SET`;
it must be frozen before scoring.

## Hard Blocks

The branch support must not use:

```text
P5C v3 family-localized gain pattern;
held-out residuals;
dominant positive family;
observed OOS DeltaNLL pattern;
signed diagnostic advantage;
failed family-permutation gate.
```

## Current Status

```text
P5Cv3Status: P5C_V3_STRONG_LOCAL_COVARIANCE_SIGNAL_BUT_NO_GLOBAL_SURVIVAL
P5Cv3Meaning: anomaly candidate only
PTauCovScoringAuthorized: false
V4KernelAuthorized: false
```

## Next Valid Step

The next valid step is to build a concrete `delta_C_Tau` artifact from the
declared Tau morphology response and then freeze `q_branch`, `W_branch`, and
`Omega_branch` before any alignment score is run.
""",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_YAML}")
    print(f"Wrote {OUT_DOC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
