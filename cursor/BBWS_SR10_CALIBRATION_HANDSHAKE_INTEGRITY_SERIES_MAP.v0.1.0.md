# BBWS SR10 — Calibration Handshake Integrity Series Map

**series_id:** `BBWS_SR10_calibration_handshake_integrity`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR9_scale_profile_stability_governance` / `bbws-sr9-complete`  
**baseline:** `bbws-pre-sr10-cal-handshake`  
**product version target:** `2.0.0-rc5`  
**product version during impl:** `2.0.0-rc4` (bump in S09)

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR10_resume*.json
→ cursor/BBWS_SR10_*_SERIES_MAP*.md
→ superpowers/sr10_sNN_*.json
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + flash firmware 0.1.4 | Freeze SR10 contract; baseline tag; flash 0.1.4; STATUS receipt | `sr10_s01_scaffold_and_flash_014.v0.1.0.json` |
| **S02** | M02 | Host matched-ACK reader | Wait for A,SET_CAL / A,SET_DEVICE_ID / A,STREAM_OFF; skip W and unmatched A | `sr10_s02_matched_ack_reader.v0.1.0.json` |
| **S03** | M03 | Quiet Accept command window | Worker stays stopped through SET_CAL + STATUS verify; longer STREAM_OFF drain | `sr10_s03_quiet_accept_window.v0.1.0.json` |
| **S04** | M04 | Alice error message split | Split leftover ACK vs raw HX711 dump vs BAD_CAL — stop calling all streaming | `sr10_s04_alice_error_split.v0.1.0.json` |
| **S05** | M05 | Firmware 0.1.5 stream interrupt | Abort waitHx711Ready when Serial.available; bump protocol to 0.1.5 | `sr10_s05_firmware_015_stream_interrupt.v0.1.0.json` |
| **S06** | M06 | Scripted handshake regression tests | Interleaved W + STREAM_OFF ACK then SET_CAL ACK must succeed | `sr10_s06_scripted_handshake_tests.v0.1.0.json` |
| **S07** | M07 | Physical Accept + characterize | Flash 0.1.5; Connect/profile apply; Guided Cal Accept; 100 g Confirm | `sr10_s07_physical_accept_characterize.v0.1.0.json` |
| **S08** | M08 | Docs + operator Accept recovery | Bring-up flash steps, SERIAL_PROTOCOL 0.1.5, Accept recovery copy | `sr10_s08_docs_and_operator_recovery.v0.1.0.json` |
| **S09** | M09 | Bump to 2.0.0-rc5 + Windows packaging | Version/drift/manifest; Setup/zip; rc4→rc5 upgrade smoke | `sr10_s09_rc5_windows_packaging.v0.1.0.json` |
| **S10** | M10 | SR10 series closeout + tags | Docs/release, tag v2.0.0-rc5 + bbws-sr10-complete, push | `sr10_s10_release_and_closeout.v0.1.0.json` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- 100 g characterization is repeatability evidence, not certification
- Scale profiles/receipts are local operational evidence only
- JSONL remains authoritative for weight records
- Capture loop unchanged: scan → settle → lock → confirm → reset
- Firmware device identity must be unique; collision requires operator intervention
- Archived profiles never erase historical calibration or weight evidence
- Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only
- Not a remote weighing server
- Matched-ACK handshake is operational integrity only — not certification
