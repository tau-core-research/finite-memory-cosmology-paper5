# P-TauCov Parent-Action Scorecard Script Freeze

Status: `P_TAUCOV_PARENT_ACTION_SCORECARD_SCRIPT_FROZEN_NO_SCORING`.

- script: `scripts/run_p_taucov_parent_action_scorecard.py`
- SHA256: `56b8c66746f5e9b88c97d381e17d8e77a1c87803a5cea529a4ca9f7863afe93c`
- mode: `inert_until_final_manifest`

This freezes the scorecard entrypoint before scoring authorization.
The script is intentionally blocked unless a final authorization
manifest exists.
