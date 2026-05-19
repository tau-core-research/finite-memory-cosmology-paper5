# PySR Criteria-Set-3 Reproduction Contract

Status: PYSR_CRITERIA3_CONTRACT_READY_RUNTIME_AVAILABLE.

This contract turns the upstream criteria-set-3 symbolic-regression route into a local execution target. It is a reproduction preflight, not measurement validation.

## Runtime

- PySR available: True
- SymPy available: True
- scikit-learn available: True
- SciPy available: True
- Julia on PATH: False
- Private Julia available through juliacall: True
- Execution ready: True

## Locked Constraints

- Do not change the K2 kernel.
- Do not allow rho > 4.
- Do not refit K1.
- Do not use target-sign gates.
- Do not use amplitude fitting.
- Do not treat this route as measurement validation.

## Next Action

run a small criteria-set-3 smoke reproduction, then scale to bootstrap derivative exports
