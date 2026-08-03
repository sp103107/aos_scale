# BBWS SR2 S01 — Tk/Linux gap matrix vs PySide SR1

Frozen audit before Tk port seasons (S02–S06) and display-unit seasons (S07–S08).

| Surface | PySide SR1 | Tk before SR2 | SR2 target |
|---------|------------|---------------|------------|
| Soft confirm / duplicate warning | yes | no | S02 |
| Cancel → barcode focus | yes | partial | S02 |
| Test Scanner + receipt | yes | no | S03 |
| Barcode policy / auto ID | yes | no | S03 |
| Sticky Change Strain | yes | no | S04 |
| Pending sync / rebuild CSV | yes | no | S05 |
| Recover soft path | yes | basic recover only | S05 |
| Export + reconcile gate | yes | export only | S06 |
| Display unit g/kg/lb | no | no | S07–S08 |
| Linux launcher / Xvfb smoke | notes | secondary | S09 |

## Locks

- Shared `OperatorRuntime` — no second controller
- Storage remains grams
- Firmware remains `SET_UNIT,g`
- Linux: source + Xvfb smoke; no new GUI installer
