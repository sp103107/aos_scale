# Gate vs suggest matrix

| Condition | Class | Operator outcome |
|-----------|-------|------------------|
| Scale not connected / no live samples | Hard block | Plain next step: connect / wait for live weight |
| Mid plant capture during cal | Hard block | Finish or cancel the plant first |
| Cal test outside local tolerance | Hard block | Show measured vs reference; retry Test; no SET_CAL |
| Accept without confirmation | Hard block | Confirm dialog |
| No harvest run | Soft | Allow maintenance cal / Zero |
| Uncalibrated factor ≈ 1.0 | Soft | Banner + new-run suggest; Skip OK |
| No barcode scanner | Soft | Type Enter, or Use auto ID when setting off |
| Legal-for-trade disclaimer | Soft | One line in cal dialog |
