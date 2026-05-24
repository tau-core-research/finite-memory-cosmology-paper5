# P-TauCov Parent-Source Gap Packet

Status: `P_TAUCOV_PARENT_SOURCE_GAP_IDENTIFIED_NO_SCORING`

This packet records why the current P-TauCov source route must stop
before any new empirical scorecard.

## Key Diagnosis

- residue candidate status: `P_TAUCOV_PARENT_HESSIAN_RESIDUE_CANDIDATE_PREFLIGHT_FAIL_NO_SCORING`
- residue norm after required cleaning: `1.2666834795585915e-16`
- expanded primary minus strongest null: `-147.251561813177`
- previous commutator projection-null correlation: `0.7337111972818574`

The problem is no longer just empirical scoring. The problem is source
selection. The current parent-side recipes can create positive covariance
gain, but when forced to be non-smooth, projection-clean, and balanced,
the available residue vanishes.

## Consequence

The next object must be derived upstream of the empirical bridge. It must
come from a microscopic parent source selector: a compact spectrum,
boundary/domain condition, index residue, or parent-action Hessian mode
selection rule.

## Next Allowed Artifact

`p_taucov_microscopic_residue_source_spec_v1_no_score`

Forbidden: building another empirical covariance kernel before this source
selector exists.
