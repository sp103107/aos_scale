# Continuation Handoff — Best Buds Weight Station v0.1.4

Continue from the complete `v0.1.4` repository. Use the LLM validation harness to execute RC3B–RC3G against the connected PC-first UNO/HX711/load-cell assembly. Do not claim physical success until the firmware, protocol, zero/tare, calibration, repeatability, physical barcode loop, and restart/resume receipts exist.

Start with:

```bash
python -m best_buds_weight_station.validation inspect
python -m best_buds_weight_station.validation prepare --profile development
python -m best_buds_weight_station.validation run --lane software
```
