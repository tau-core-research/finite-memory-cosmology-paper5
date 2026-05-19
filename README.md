# Finite-memory cosmology paper 5

This repository is the public reproducibility package for Paper 5:

**Finite-memory projection corrections as a diagnostic gate for cosmological consistency tests**

The manuscript is a cautious method-note and benchmark-preflight package. It
defines a locked finite-memory projection operator, reproduces the current
diagnostic packet, builds null comparators, and records the public-data and
source-native backreaction blockers that remain before any measurement claim.

The package intentionally does **not** claim a discovery, a validated physical
model, or measurement validation of a finite-memory effect. All Tau Core /
projection-language references are treated as motivation for a locked diagnostic
operator, not as assumptions required to reproduce the benchmark.

## Author And Research Workflow

I am an independent researcher using an AI-assisted workflow to develop reproducible diagnostic tests around projection-sensitive residual hypotheses. I am not claiming expert-level validation. I would value criticism on whether the proposed gate/falsification structure is scientifically meaningful.

AI systems are used for drafting, mathematical organization, code generation, literature triage, and internal consistency checks. Numerical and symbolic audits can support reproducibility and error-finding, but they do not replace independent expert review or physical validation.

## Theory Context

The broader Tau Core theory background is maintained separately at:

```text
https://github.com/tau-core-research/tau-core-theory
```

This Paper 5 repository is standalone. It can be read as a finite-memory
diagnostic-gate proposal with reproducible preflight scorecards.

## Repository contents

```text
paper5_submission_source/                         Paper-facing draft/PDF packet
docs/                                             Method notes and audit summaries
evidence/                                         Reproducibility CSV outputs
data/                                             Derived public-input and reproduction packets
frozen/                                           Locked operator/configuration artifacts
src/fmc/                                          Minimal scoring and covariance helpers
scripts/                                          Reproduction and audit scripts
studies/finite_memory_cosmology_paper5_v01/       Paper 5 package generator
wolfram/                                         Independent Wolfram checks
tests/                                            Public reproducibility checks
arxiv_submission_source.zip                       arXiv-style source packet
```

Raw survey products are not redistributed here. The retained files are derived
tables, source-package extracts, and local reproduction artifacts needed to
rerun the Paper 5 preflight analyses.

## Reproduce

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Regenerate the current diagnostic gate:

```bash
PYTHONPATH=src python scripts/run_gate_current_packet.py
```

Regenerate the coordinate/null/source-native preflight layers used by the
current package:

```bash
PYTHONPATH=src python scripts/run_coordinate_robustness.py
PYTHONPATH=src python scripts/run_null_comparison.py
PYTHONPATH=src python scripts/build_registered_protocol_guided_reproduction_families.py
PYTHONPATH=src python scripts/run_registered_protocol_guided_bridge_scorecard.py
PYTHONPATH=src python scripts/build_registered_protocol_guided_dominance_audit.py
PYTHONPATH=src python scripts/build_finite_memory_preflight_packet.py
python scripts/build_figures.py
```

Regenerate the paper-facing PDF and arXiv-style packet:

```bash
python studies/finite_memory_cosmology_paper5_v01/make_paper5_submission_source_v01.py
```

Run public checks:

```bash
python -m pytest -q
```

Optional independent Wolfram check:

```bash
wolframscript -file wolfram/FiniteMemory_Diagnostic_Check.wl
```

This second implementation verifies the symbolic memory-budget identities and
cross-checks the shape-selection, threshold-sensitivity, and SN+BAO point-level
gate CSVs used by the manuscript. It checks software/table reproducibility, not
the physical correctness of the finite-memory diagnostic ansatz.

## Main outputs

- `paper5_submission_source/main.pdf`
- `paper5_submission_source/main.tex`
- `paper5_submission_source/draft.md`
- `finite_memory_projection_corrections.pdf`
- `figures/*.pdf`
- `evidence/finite_memory_preflight_summary.csv`
- `evidence/registered_protocol_guided_dominance_summary.csv`
- `evidence/source_native_reproduction_family_dominance_summary.csv`
- `studies/finite_memory_cosmology_paper5_v01/wolfram_audit_logs/finite_memory_diagnostic_check_wolfram.csv`
- `arxiv_submission_source.zip`

## Claim boundary

Allowed wording: diagnostic compatibility, preflight benchmark, locked
prediction, null comparators, covariance-aware benchmark requirements, and
falsification criteria.

Disallowed wording includes discovery language, finite-memory confirmation
language, theory-proven language, measurement-validation language, and
detection language.

## Citation

Use `CITATION.cff` for repository citation metadata. Data-use and
redistribution boundaries are documented in `DATA_NOTICE.md`.
