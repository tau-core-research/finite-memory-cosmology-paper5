# P-TauCov Projection-Essentiality Action Selection Theorem Candidate

Status: conditional selection theorem / no empirical scorecard / no survival
claim.

The projection-essentiality parent-action origin showed that the witness is the
Hessian of the local normal form

```math
V_{\rm PE}(\Phi,B,P)
=
-2PB - P\Phi - \frac{1}{2}B^2 .
```

This note records the next stricter claim: under a small set of declared
local-normal-form constraints, this is the unique quadratic form in the
`(Phi,B,P)` sector.

## Declared Constraints

The theorem candidate uses only structural constraints, not score behavior:

| Constraint | Meaning |
| --- | --- |
| C1 | quadratic local normal form in `(Phi,B,P)` |
| C2 | no `M` coordinate and no target residual input |
| C3 | no pure projection self-energy `P^2` in the witness sector |
| C4 | no pure source self-energy `Phi^2` in the witness sector |
| C5 | branch counterterm normalized as `-1/2 B^2` |
| C6 | branch relaxation orientation: stationary branch response satisfies `B_* = -2P` |
| C7 | source-projection coupling normalized as `-P Phi` |

The no-`P^2` and no-`Phi^2` constraints are important. They prevent the witness
from becoming a projection spike or a source-amplitude proxy. The branch
counterterm fixes the reduced-branch scale. The `B_*=-2P` condition fixes the
projection-to-branch relaxation orientation.

## Result

Under C1-C7, the admissible quadratic local normal form is uniquely

```math
V_{\rm PE}(\Phi,B,P)
=
-2PB - P\Phi - \frac{1}{2}B^2 .
```

Equivalently, the generated Hessian witness is uniquely

```math
H_{\rm PE}
=
-2(PB+BP) - (P\Phi+\Phi P) - BB .
```

## Claim Boundary

Allowed:

```text
The projection-essential witness is the unique local quadratic normal form
under the declared branch-relaxation and no-self-energy constraints.
```

Forbidden:

```text
This proves the final Tau Core action or validates the empirical covariance
signal.
```

## Remaining Open Gate

The remaining theoretical gate is to derive C1-C7 from the global Tau Core
parent structure rather than declaring them as local normal-form constraints.
