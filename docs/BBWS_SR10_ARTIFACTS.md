# BBWS SR10 Artifacts

**series_id:** `BBWS_SR10_calibration_handshake_integrity`  
**product_version_target:** `2.0.0-rc5`  
**product_version_during_impl:** `2.0.0-rc4`  
**generated:** 2026-08-13T15:35:00Z

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR10_CALIBRATION_HANDSHAKE_INTEGRITY_SERIES_MAP.v0.1.0.md` |
| Resume pack | `context/resume_pack/BBWS_SR10_resume.v0.1.0.json` |
| Device service (matched ACK) | `app/best_buds_weight_station/device_service.py` |
| Operator Accept quiet window | `app/best_buds_weight_station/operator_runtime.py` |
| Alice authority | `app/best_buds_weight_station/alice/authority.py` |
| Firmware 0.1.5 | `firmware/elegoo_uno_r3_hx711/best_buds_scale_firmware.ino` |
| Serial protocol | `firmware/elegoo_uno_r3_hx711/SERIAL_PROTOCOL.md` |
| Contract freeze | `reports/sr10_s01_contract_freeze.v0.1.0.json` |
| Flash 0.1.4 receipt | `reports/sr10_s01_firmware_flash_014.json` |
| Handshake tests | `tests/test_sr10_calibration_handshake.py` |
| Physical handshake | `reports/sr10_s07_physical_handshake.json` |
| Drift gate | `scripts/validate_drift_concordance_v200_rc5.py` |

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
