# Reproducibility

## Public Packet Scope

This public repository contains the manuscript scaffold and distilled evidence
tables for a theory-method diagnostic note. It intentionally does not include
the full exploratory research tree or the full Tau Core repository history.

The included evidence tables are manuscript-facing summaries:

```text
evidence/claim_matrix.csv
evidence/result_summary.csv
evidence/diagnostic_point_audit.csv
evidence/source_packet_manifest.csv
```

## What Can Be Reproduced From This Repository

Readers can reproduce the claim discipline and manuscript-level result summary:

```text
allowed / forbidden claim boundaries
finite-memory operator statement
BAO-only diagnostic summary
SN+BAO sign-stability diagnostic summary
paper-readiness limitations
```

## What Is Not Yet Public Here

The full exploratory packet generator chain, source reconstruction scripts, and
Tau Core internal theory files are not included in this public packet. A later
methods release may add a standalone reproduction script once the likelihood
proxy is promoted beyond diagnostic status.

## Current Reproduction Status

```text
manuscript evidence tables: included
full covariance likelihood: not included / not complete
direct published likelihood comparison: not included / not complete
full Tau Core theory: intentionally not included
```

## Generate PDF

```bash
python3 -m pip install -r requirements.txt
python3 make_pdf.py
```

Generated output:

```text
finite_memory_projection_corrections.pdf
```

The renderer supports the small subset of Markdown used in `draft.md`,
including fenced code blocks, tables, bullets, and `$$ ... $$` display
equation blocks.
