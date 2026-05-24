# P-TauCov Expanded Parent-Operator Scorecard Script Freeze

Status: `P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORECARD_SCRIPT_FROZEN_NO_SCORING`.

- script: `scripts/run_p_taucov_expanded_parent_operator_scorecard.py`
- SHA256: `b10a16c2180ec41d432fdbfba953d49169205c0b8f144e5340ab17aa252c7f76`
- mode: `blocked_until_expanded_final_manifest`

This freezes the expanded scorecard entrypoint before scoring authorization.
The script remains blocked unless a final expanded authorization manifest
exists and explicitly authorizes the primary covariance scorecard scope.
