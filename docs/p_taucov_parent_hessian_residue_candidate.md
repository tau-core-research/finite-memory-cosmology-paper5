# P-TauCov Parent-Hessian Residue Candidate

Status: `P_TAUCOV_PARENT_HESSIAN_RESIDUE_CANDIDATE_PREFLIGHT_FAIL_NO_SCORING`

This is a no-score preflight artifact. It builds a target-blind
parent-Hessian residue candidate from the existing commutator object,
then applies clock high-pass, family/context balancing, and frozen
null-direction exclusion. It does not run an empirical scorecard.

## Key Metrics

- gates passed: `6/7`
- smooth PSD projection overlap: `2.5570441632129657e-05`
- projection-null abs correlation: `0.0031689019692280663`
- spectral residue rank fraction: `0.6060221504346557`
- orientation anchor margin: `-0.013887136532598933`
- balanced retained norm: `0.9526874184714962`
- max family share: `0.13443140702906006`
- max clock share: `0.137526862430535`
- max context share: `0.31257021778706495`

## Claim Boundary

Allowed: this candidate either passes or fails the no-score structural
preflight for parent-Hessian residue specificity.

Forbidden: this candidate demonstrates Tau Core, survives empirically,
or rescues a failed scorecard.
