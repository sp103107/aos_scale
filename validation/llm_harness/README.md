# LLM Validation Harness

Machine-first validation control surface for Cursor, Codex, and other coding agents.

```bash
python -m best_buds_weight_station.validation inspect
python -m best_buds_weight_station.validation prepare --profile development
python -m best_buds_weight_station.validation run --lane software
python -m best_buds_weight_station.validation run --lane firmware --port COM4
python -m best_buds_weight_station.validation run --lane serial --port COM4
python -m best_buds_weight_station.validation evaluate --profile integration
```

Each lane emits JSON and writes a receipt under `validation/receipts/`. Physical lanes never pass from source presence or fixtures.
