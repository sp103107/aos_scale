# Continuation Handoff - Best Buds Weight Station v0.1.8

Current phase: `rc3c12_final_polish_and_drift_review`

Next phase: `rc3d_uno_r3_hx711_physical_scale_bringup`

Run `python -m best_buds_weight_station.bootstrap --profile cursor-ready` before any physical integration. Preserve all historical Context records and non-claims. Use `PySerialTransport -> DeviceService -> ScaleReadingWorker` as the canonical physical serial path.
