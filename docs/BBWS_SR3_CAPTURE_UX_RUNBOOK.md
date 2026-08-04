# BBWS SR3 — Harvest Station Capture UX Runbook

**series_id:** `BBWS_SR3_station_capture_ux`

## Operator loop

1. Start/resume a run and connect the scale.
2. Press **Scan** (or click the barcode field) and scan/type the plant tag.
3. The tag stays visible as **Active plant** while you hang the plant.
4. Wait until status shows **STABLE — LOCK WEIGHT**.
5. Press **Lock weight** (freezes the sample used for the record).
6. Press **Confirm & Record**.
7. The field clears and focus returns for the next plant.
8. Use the **Run plant log** list for a read-only view of recent saves (not Metrc).

## Non-claims

- Lock weight is not a legal-for-trade hold decision.
- Plant log is not a Metrc plant list.
- Scan is HID keyboard-wedge focus only (not BLE/SPP).

## Dual UI

PySide is primary; Tk shares `OperatorRuntime` and the same lock/confirm loop.
