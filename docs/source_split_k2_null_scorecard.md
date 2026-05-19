# Source-Split K2 / Null Scorecard

Status: authorized preflight scorecard completed.

This scorecard runs only after the source-split authorization guard returns
`AUTHORIZED`. It is a preflight benchmark, not measurement validation.

## Run

```text
python3 scripts/run_source_split_k2_null_scorecard.py
```

It writes:

```text
evidence/source_split_k2_null_scorecard.csv
evidence/source_split_k2_null_scorecard_summary.csv
```

## Result

The current source-split K1 target is a zero-contrast no-memory response. Under
the locked multiplicative K2 operator,

```text
K2(x) = W(x) * K1(x)
```

this means K2 is also zero for every allowed `rho`.

Current summary:

```text
K2DegenerateWithK1NoMemory: True
K2Rho4Status: STRICT_GATE_WARNING
K2Rho4SignStableViolations: 3
BestAICModel: POLY_DEG2_CONTROL
```

## Interpretation

This weakens distinct K2 evidence on the present source-split target. The
scorecard shows that the locked multiplicative operator is runnable, but it is
not distinguishable from the zero-contrast no-memory control under the current
K1 definition.

This is not final falsification. It means the next useful work is to revisit
the source-split K1 response definition or move to a likelihood-native target,
without changing the locked K2 kernel post hoc.

The row-level degeneracy audit is:

```text
python3 scripts/diagnose_source_split_k1_degeneracy.py
```

It confirms that all eight usable rows have zero K1 response, so every allowed
rho gives K2=K1.
