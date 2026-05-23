# P-TauCov Parent-Action Scorecard Script Freeze

Status: `P_TAUCOV_PARENT_ACTION_SCORECARD_SCRIPT_FROZEN_NO_SCORING`.

- script: `scripts/run_p_taucov_parent_action_scorecard.py`
- SHA256: `6b06dcfd404bbebe5521f7a9b88857a8142abc5e0b1e5af0e4c77f0d2c5ca334`
- mode: `inert_until_final_manifest`

This freezes the scorecard entrypoint before scoring authorization.
The script is intentionally blocked unless a final authorization
manifest exists.
