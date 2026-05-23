#!/usr/bin/env python3
"""Build a minimal target-blind Tau-response model specification for P-TauCov.

This is not a delta_C_Tau generator. It proposes the smallest admissible
mathematical form for the four Tau-side blockers so the next step can freeze a
concrete model without looking at target residuals or P5C v3 gains.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_minimal_tau_response_model_spec.md"
OUT_CSV = EVIDENCE / "p_taucov_minimal_tau_response_model_spec.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_minimal_tau_response_model_spec_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
SPEC_ID = "P_TAUCOV_MINIMAL_TAU_RESPONSE_MODEL_SPEC_v1"
CLAIM_BOUNDARY = "minimal_tau_response_model_spec_no_delta_c_tau_no_scoring"


ROWS = [
    {
        "Object": "BranchStateB",
        "CandidateDefinition": "B is a reduced branch-amplitude vector on the frozen observable/source coordinate basis",
        "AdmissibilityRole": "provides finite-dimensional target-blind branch degrees of freedom",
        "Status": "CANDIDATE_SPECIFIED_NOT_FROZEN",
    },
    {
        "Object": "BranchEquationFB",
        "CandidateDefinition": "F_B(Phi,B)=L0_B B - R_B Phi + lambda_B N_B(B)",
        "AdmissibilityRole": "separates linear branch relaxation from optional nonlinear self-response",
        "Status": "CANDIDATE_SPECIFIED_NOT_FROZEN",
    },
    {
        "Object": "ReducedBranchOperatorLBred",
        "CandidateDefinition": "L_B^red = L0_B + lambda_B D_B N_B(B_*) restricted to declared non-null branch domain",
        "AdmissibilityRole": "makes deltaB_star computable from the frozen branch equation",
        "Status": "CANDIDATE_SPECIFIED_NOT_FROZEN",
    },
    {
        "Object": "BranchDomainPolicy",
        "CandidateDefinition": "remove null/gauge modes by a declared projector P_red before inversion",
        "AdmissibilityRole": "prevents hidden fitting through singular directions",
        "Status": "CANDIDATE_SPECIFIED_NOT_FROZEN",
    },
    {
        "Object": "ParentMorphologyMap",
        "CandidateDefinition": "M_parent(Phi,B)=A_Phi Phi + A_B B",
        "AdmissibilityRole": "minimal linear morphology carrier; nonlinear terms require separate freeze",
        "Status": "CANDIDATE_SPECIFIED_NOT_FROZEN",
    },
    {
        "Object": "ProjectionMorphologyMap",
        "CandidateDefinition": "P_morph(Phi,B)=P0 + epsilon_P P1(Phi,B) with P0 fixed before scoring",
        "AdmissibilityRole": "keeps projection explicit and auditable instead of post-hoc morphology selection",
        "Status": "CANDIDATE_SPECIFIED_NOT_FROZEN",
    },
    {
        "Object": "TauMorphologyResponse",
        "CandidateDefinition": "T_tau = D_Phi M_proj - D_B M_proj (L_B^red)^-1 D_Phi F_B",
        "AdmissibilityRole": "mandatory branch-relaxation subtraction; distinguishes Tau response from generic morphology",
        "Status": "FORMULA_READY_DEPENDS_ON_FREEZE",
    },
    {
        "Object": "CovarianceResponseMap",
        "CandidateDefinition": "delta_C_Tau = D_M C[T_tau deltaPhi] with D_M C frozen as a linear covariance lift",
        "AdmissibilityRole": "converts morphology response to covariance response without target residuals",
        "Status": "FORMULA_READY_DEPENDS_ON_FREEZE",
    },
    {
        "Object": "NoOutcomeSelectionRule",
        "CandidateDefinition": "all matrices A_Phi,A_B,L0_B,R_B,P0,P1 and any lambda/epsilon switches must be frozen before scoring",
        "AdmissibilityRole": "blocks v3 outcome leakage and post-score branch selection",
        "Status": "HARD_RULE",
    },
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SpecID": SPEC_ID,
                "Object": row["Object"],
                "CandidateDefinition": row["CandidateDefinition"],
                "AdmissibilityRole": row["AdmissibilityRole"],
                "Status": row["Status"],
                "ScoringAuthorized": False,
                "DeltaCTauGenerated": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in ROWS
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SpecID": SPEC_ID,
                "CandidateObjectsSpecified": int((df["Status"] == "CANDIDATE_SPECIFIED_NOT_FROZEN").sum()),
                "FormulaReadyObjects": int((df["Status"] == "FORMULA_READY_DEPENDS_ON_FREEZE").sum()),
                "HardRules": int((df["Status"] == "HARD_RULE").sum()),
                "DeltaCTauGenerated": False,
                "BranchSupportFreezeAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "freeze_concrete_matrices_or_reject_candidate_spec",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Minimal Tau-Response Model Specification

Status: candidate model specification / not frozen / no `delta_C_Tau` / no
scoring authorization.

This note proposes a minimal target-blind mathematical form for the four
Tau-side blockers isolated by the P-TauCov input packet:

```text
F_B, L_B^red, M_parent, P_morph
```

It is not an empirical result. It is a candidate specification that must either
be frozen into concrete matrices/operators or rejected before any
`delta_C_Tau`, branch support, or alignment score is generated.

## 1. Minimal Branch State

Let `B` be a reduced branch-amplitude vector on the frozen observable/source
coordinate basis. The basis must be declared before scoring and cannot be
chosen from P5C v3 gains.

## 2. Candidate Branch Equation

The minimal branch equation is:

```math
F_B(\\Phi,B)
=
L^0_B B - R_B\\Phi + \\lambda_B N_B(B).
```

The linear part carries the target-blind branch relaxation. The optional
nonlinear term is allowed only if `lambda_B`, `N_B`, and its derivative are
frozen before scoring. The strictly linear candidate is recovered by
`lambda_B = 0`.

## 3. Reduced Branch Operator

The reduced branch operator is:

```math
L_B^{\\rm red}
=
P_{\\rm red}
\\left(L^0_B + \\lambda_B D_B N_B(B_*)\\right)
P_{\\rm red}.
```

`P_red` declares the invertible branch domain. Null modes, gauge-like modes,
and excluded directions must be frozen before inversion.

## 4. Parent Morphology Map

The minimal morphology carrier is:

```math
M_{\\rm parent}(\\Phi,B)
=
A_\\Phi\\Phi + A_B B.
```

This is intentionally conservative. Any nonlinear morphology term is a new
model family and requires a separate freeze.

## 5. Projection Morphology Map

The minimal projection map is:

```math
P_{\\rm morph}(\\Phi,B)
=
P_0 + \\epsilon_P P_1(\\Phi,B).
```

The safest first candidate is `epsilon_P = 0`, which tests whether a fixed
projection geometry plus branch relaxation already predicts a localized
covariance response. If `epsilon_P` is nonzero, `P_1` must be frozen before any
score is seen.

## 6. Resulting Tau Response

After the above objects are frozen, the admissible response remains:

```math
T_\\tau
=
D_\\Phi M_{\\rm proj}
-
D_B M_{\\rm proj}(L_B^{\\rm red})^{-1}D_\\Phi F_B.
```

and:

```math
\\delta C_\\tau
=
D_M C[T_\\tau\\delta\\Phi].
```

## 7. Reviewer-Safe Claim Boundary

Allowed statement:

```text
A minimal target-blind Tau-response model family has been specified for future
P-TauCov freezing.
```

Forbidden statement:

```text
This specification already produces a Tau-specific covariance signal.
```

## 8. Next Valid Step

The next valid step is one of:

```text
freeze concrete matrices/operators for the strictly linear candidate;
or reject this candidate specification and document why it is too weak.
```

Only a frozen concrete model can produce a hashed `delta_C_Tau` artifact.
""",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DOC}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
