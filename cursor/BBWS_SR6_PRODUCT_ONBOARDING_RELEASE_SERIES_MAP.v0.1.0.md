# BBWS SR6 — Product Onboarding + Release Series Map

**series_id:** `BBWS_SR6_product_onboarding_release`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR5_run_artifact_polish` / `bbws-sr5-complete`  
**baseline:** `bbws-pre-sr6-onboarding-release`  
**product version target:** `2.0.0-rc1`

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR6_resume*.json
→ cursor/BBWS_SR6_*_SERIES_MAP*.md
→ superpowers/sr6_sNN_*.json
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + onboarding/release contract freeze | Freeze docs/release contract and non-claims | `sr6_s01_onboarding_contract_freeze.v0.1.0.json` |
| **S02** | M02 | Salvage selection map KS + Book Spine | Map onboarding/entrypoint cites to BBWS docs | `sr6_s02_salvage_selection_map.v0.1.0.json` |
| **S03** | M03 | Human START_HERE + intended user | Root START_HERE and INTENDED_USER docs | `sr6_s03_human_start_here.v0.1.0.json` |
| **S04** | M04 | Operator onboarding runbook | Structured OPERATOR_ONBOARDING with capture loop | `sr6_s04_operator_onboarding.v0.1.0.json` |
| **S05** | M05 | Coding-agent START HERE + onboard.py | Agent front door and Python document router | `sr6_s05_coding_agent_entry.v0.1.0.json` |
| **S06** | M06 | README + RELEASE_CANDIDATE for 2.0.0-rc1 | GitHub-facing honesty for product RC | `sr6_s06_github_docs_refresh.v0.1.0.json` |
| **S07** | M07 | Drift concordance for 2.0.0-rc1 | Version concordance validator and test fixes | `sr6_s07_drift_concordance.v0.1.0.json` |
| **S08** | M08 | Bump product version to 2.0.0-rc1 | version.py and packaging version consumers | `sr6_s08_version_bump_rc1.v0.1.0.json` |
| **S09** | M09 | Clean clone source zip bundle | make_release_bundle source zip + receipt | `sr6_s09_clone_zip_bundle.v0.1.0.json` |
| **S10** | M10 | GitHub Release + bbws-sr6-complete | gh release, tags, ACTIVE_ARC series_complete | `sr6_s10_series_closeout.v0.1.0.json` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- Not production-sealed weighing certification
- JSONL remains authoritative for records
- Salvage/KS/Book Spine are documentation doctrine cites only
- Coding-agent onboard entry is guidance/bootstrap routing, not a new capture runtime
- Capture loop unchanged: scan → settle → lock → confirm → reset
