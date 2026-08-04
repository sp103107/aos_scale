# BBWS SR3 — Harvest Station Capture UX Runbook

**series_id:** `BBWS_SR3_station_capture_ux`

## Operator loop

1. Start/resume a run and connect the scale.
2. On New Run, enter **Cultivator** (company/grower, default Best Buds) and **Strain** (sticky plant strain).
3. When the station shows **Ready to scan**, press **Scan** to open the scanner window.
4. Scan/type the plant tag and press Enter. The scanner window closes and the accepted tag appears in the main barcode field and **Active plant** banner.
5. The tag stays visible as **Active plant** while you hang the plant.
6. Wait until status shows **STABLE — LOCK WEIGHT**.
7. Press **Lock weight** (freezes the sample used for the record).
8. Press **Confirm & Record**.
9. The field clears and focus returns for the next plant.
10. Use the **Run plant log** list for a read-only view of recent saves (not Metrc).

## Cultivator vs Strain

| Operator term | Stored as | CSV column |
|---------------|-----------|------------|
| Cultivator (company) | `facility_id` | `cultivator` |
| Strain (sticky) | `cultivar_*` | `strain` (+ legacy `cultivar_*`) |

Change Strain updates only the sticky strain for the open run.

## Non-claims

- Lock weight is not a legal-for-trade hold decision.
- Plant log is not a Metrc plant list.
- Scan opens an HID keyboard-wedge capture window; it is not BLE/SPP or camera scanning.

## Window layout

The PySide station surface scrolls vertically when the available window height is smaller than the complete operator surface. Controls and the run plant log remain separate instead of compressing or overlapping.

## Dual UI

PySide is primary; Tk shares `OperatorRuntime` and the same lock/confirm loop.
