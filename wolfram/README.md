# Wolfram independent finite-memory check

This directory contains an optional Wolfram Language second implementation for
the finite-memory diagnostic packet.

Run from the repository root:

```bash
wolframscript -file wolfram/FiniteMemory_Diagnostic_Check.wl
```

The script independently verifies the symbolic memory-budget relations and
cross-checks the compact CSV evidence used by the manuscript:

- finite-memory operator: `W(x)=1+rho*x^3`;
- passive tail budget: `E_tail=rho/4`;
- passive bound: `rho<=4`;
- generalized power-kernel bound: `rho<=p+1`;
- threshold/shape-selection audit rows;
- SN+BAO point-level diagnostic gate rows.

Outputs are written to:

`studies/finite_memory_cosmology_paper5_v01/wolfram_audit_logs/`
