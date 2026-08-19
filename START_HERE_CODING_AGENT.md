# START HERE — Coding Agent / LLM

**runtime_claimed:** false  
**product_version:** `2.0.0-rc10.1`  
**series:** see `ACTIVE_ARC.yaml`

## Mission

Continue Best Buds Weight Station work from product-owned arc pointers. Prefer evidence, receipts, and non-claims. Do not invent Metrc or legal-for-trade status.

## Load order (required)

```text
1. ACTIVE_ARC.yaml
2. context/resume_pack/BBWS_SR*_resume*.json (active series)
3. cursor/*_SERIES_MAP*.md for that series
4. superpowers/srN_sNN_*.json for current season
5. Execute next SnnEkk only
```

Human operator door: [START_HERE.md](START_HERE.md).

## Quick guidance CLI

```bash
python -m best_buds_weight_station.onboard
python -m best_buds_weight_station.onboard --json
```

Prints version, key paths, ACTIVE_ARC summary, and bootstrap hints.  
**Does not** start the operator UI or mutate capture state.

## Evidence-gated bootstrap

```bash
python -m best_buds_weight_station.bootstrap --profile cursor-ready
```

Windows:

```powershell
.\cursor_bootstrap.ps1 -Plan cursor_ready
```

## Forbidden (unless a season explicitly authorizes)

- Capture state machine / Scan→Lock→Confirm workflow redesign without a series
- Claiming JSONL is non-authoritative
- Metrc sync / legal-for-trade claims
- Mutating `M:/SALVAGE` or Arc Launcher as Best Buds runtime
- Auto-push mid-episode (push at series closeout unless told otherwise)

## Product layout (high signal)

| Path | Role |
|------|------|
| `app/best_buds_weight_station/` | Product code |
| `launch_best_buds.bat` | Operator launch |
| `docs/` | Runbooks + onboarding |
| `tests/` | Contract tests |
| `scripts/scaffold_bbws_sr*.py` | Arc scaffolds |
| `ACTIVE_ARC.yaml` | Live series pointer |

## Non-claims

- Coding-agent onboard entry is guidance/bootstrap routing, not a new capture runtime
- Not legal-for-trade / Metrc
- Salvage cites are doctrine only

## Local agent cockpit (optional, gitignored)

If present on this machine (not shipped in RC source zips):

```bash
python _local_agent/kickoff.py
```

Paste prompt: `_local_agent/CODING_AGENT_KICKOFF.md`. Guidance only — same non-claims as product onboard.

## Related kickoffs

- `kickoff_prompts/BBWS_SR6_HUMAN_CHAT_KICKOFF.md` (when SR6 active)
- `context/resume_pack/CONTINUATION_HANDOFF_PROMPT.md`
