#!/usr/bin/env python3
"""Build the P-TauCov delta_C_Tau source schema and readiness matrix.

This artifact intentionally does not fabricate a delta_C_Tau matrix. It records
the exact source objects that must exist before a target-blind Tau covariance
response can be generated.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_delta_c_tau_source_schema.md"
OUT_CSV = EVIDENCE / "p_taucov_delta_c_tau_source_schema.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_delta_c_tau_source_readiness.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
SCHEMA_ID = "P_TAUCOV_DELTA_C_TAU_SOURCE_SCHEMA_v1"
CLAIM_BOUNDARY = "source_schema_blocks_delta_c_tau_generation_until_inputs_exist"


ROWS = [
    ("PhiPerturbationFamily", "parent perturbation family deltaPhi", "NOT_PROVIDED"),
    ("BranchEquationFB", "reduced branch equation F_B(Phi,B)=0", "NOT_PROVIDED"),
    ("ReducedBranchOperatorLBred", "linearized reduced branch operator L_B^red", "NOT_PROVIDED"),
    ("BranchDomainPolicy", "declared invertible reduced branch domain and excluded null modes", "NOT_PROVIDED"),
    ("BranchResponseRule", "deltaB_star = -(L_B^red)^-1 D_Phi F_B[deltaPhi]", "FORMULA_DECLARED_ONLY"),
    ("ParentMorphologyMap", "M_parent(Phi,B)", "NOT_PROVIDED"),
    ("ProjectionMorphologyMap", "P_morph(Phi,B)", "NOT_PROVIDED"),
    ("ProjectedMorphologyDerivativePhi", "D_Phi M_proj", "NOT_PROVIDED"),
    ("ProjectedMorphologyDerivativeB", "D_B M_proj", "NOT_PROVIDED"),
    ("CovarianceFunctionalDerivative", "D_M C", "NOT_PROVIDED"),
    ("ObservableCoordinateIndex", "frozen coordinate/index basis for delta_C_Tau rows and columns", "NOT_PROVIDED"),
    ("NormalizationPolicy", "Frobenius/trace/sign convention before support extraction", "NOT_PROVIDED"),
    ("LeakageExclusionAudit", "proof no held-out residual or v3 outcome input is used", "NOT_PROVIDED"),
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SchemaID": SCHEMA_ID,
                "SourceObject": item,
                "Definition": definition,
                "Status": status,
                "RequiredForDeltaCTau": True,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for item, definition, status in ROWS
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    missing = df[df["Status"].isin(["NOT_PROVIDED", "FORMULA_DECLARED_ONLY"])]
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SchemaID": SCHEMA_ID,
                "RequiredSourceObjects": len(df),
                "ReadySourceObjects": int((df["Status"] == "READY").sum()),
                "MissingOrFormulaOnlyObjects": len(missing),
                "DeltaCTauGenerationStatus": "BLOCKED_PENDING_CONCRETE_TAU_RESPONSE_INPUTS",
                "BranchSupportFreezeAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "V4KernelAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov delta_C_Tau Source Schema

Status: source schema / readiness blocker / no scoring authorization.

This document is the input checklist for generating a real target-blind
`delta_C_Tau` artifact. It deliberately does not fabricate a response matrix.
The protocol remains blocked until the Tau-response source objects below are
provided.

## Required Source Objects

| Source object | Role | Current status |
| --- | --- | --- |
| `PhiPerturbationFamily` | parent perturbation family `deltaPhi` | `NOT_PROVIDED` |
| `BranchEquationFB` | reduced branch equation `F_B(Phi,B)=0` | `NOT_PROVIDED` |
| `ReducedBranchOperatorLBred` | branch linearization `L_B^red` | `NOT_PROVIDED` |
| `BranchDomainPolicy` | invertible reduced domain and excluded null modes | `NOT_PROVIDED` |
| `BranchResponseRule` | `deltaB_star = -(L_B^red)^-1 D_Phi F_B[deltaPhi]` | `FORMULA_DECLARED_ONLY` |
| `ParentMorphologyMap` | parent morphology `M_parent(Phi,B)` | `NOT_PROVIDED` |
| `ProjectionMorphologyMap` | projected map `P_morph(Phi,B)` | `NOT_PROVIDED` |
| `ProjectedMorphologyDerivativePhi` | `D_Phi M_proj` | `NOT_PROVIDED` |
| `ProjectedMorphologyDerivativeB` | `D_B M_proj` | `NOT_PROVIDED` |
| `CovarianceFunctionalDerivative` | `D_M C` | `NOT_PROVIDED` |
| `ObservableCoordinateIndex` | frozen matrix row/column basis | `NOT_PROVIDED` |
| `NormalizationPolicy` | response normalization before support extraction | `NOT_PROVIDED` |
| `LeakageExclusionAudit` | proof no target residual or v3 outcome enters | `NOT_PROVIDED` |

## Readiness Meaning

The present status is:

```text
DeltaCTauGenerationStatus: BLOCKED_PENDING_CONCRETE_TAU_RESPONSE_INPUTS
BranchSupportFreezeAuthorized: false
PTauCovScoringAuthorized: false
V4KernelAuthorized: false
```

This is a useful negative state. It prevents the program from converting the
P5C v3 local anomaly into a Tau claim without first supplying the missing
Tau-side response machinery.

## Next Valid Step

Provide a concrete, target-blind Tau-response input packet with:

```text
F_B, L_B^red, branch-domain policy,
P_morph, M_parent, D_M C,
observable coordinate index,
normalization policy,
leakage exclusion audit.
```

Only after this source schema is ready may a hashed `delta_C_Tau` matrix be
generated.
""",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DOC}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
