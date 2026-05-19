# Source-Split K1 Degeneracy Audit

Status: degeneracy diagnosed; distinct K2 evidence is blocked by the current
zero-contrast K1 target.

## Run

```text
python3 scripts/diagnose_source_split_k1_degeneracy.py
```

It writes:

```text
evidence/source_split_k1_degeneracy_audit.csv
evidence/source_split_k1_degeneracy_summary.csv
```

## Result

The current source-split K1 target is:

```text
K1NoMemoryResponse = 0
```

on all eight usable target rows.

Because the locked K2 operator is multiplicative,

```text
K2(x) = W(x) * K1(x)
```

this gives:

```text
K2(x) = 0
```

for every allowed `rho`.

Current summary:

```text
ZeroK1Rows: 8
RowsWhereK2EqualsK1: 8
RowsWithFiniteMemoryLeverage: 0
MaxAbsFiniteMemoryLeverageRho4: 0
```

## Interpretation

This is a clean degeneracy, not a numerical accident. The current source-split
target can test whether the pipeline runs, but it cannot distinguish locked
multiplicative K2 from no-memory K1.

The next source-split task is therefore not to change K2. It is to define an
externally derived, coordinate-native, nonzero K1 response target, or to move to
a likelihood-native target where the no-memory response is not identically zero.

The requirements are recorded in:

```text
evidence/source_split_k1_response_requirements.csv
```

The follow-up sensitivity audit is:

```text
python3 scripts/build_source_split_k1_response_candidate_audit.py
python3 scripts/run_source_split_k1_candidate_sensitivity.py
```

It shows that nonzero K1 candidates exist as sensitivity controls, but none is
currently promoted to primary K1.
