# Continuation Handoff — Best Buds Cultivator Weight Station v0.1.3

Import and verify the complete `best_buds_cultivator_weight_station_v0_1_3` repository before modification. Read `VERSION`, `repo_release_state.json`, `docs/SYSTEM_STATE_CURRENT.md`, current manifests and reports, Working Set 4, Episode 4, Ledger through sequence 38, and this Resume Pack.

The next intended full-repository bump is `v0.1.4`, internal phase `rc3_physical_scale_integration_and_local_control_bridge`.

Required physical lane: inspect delivered hardware, identify load-cell wires, wire HX711 and controller, compile/upload firmware with Arduino AVR toolchain, validate physical serial discovery and stream, perform reference-weight calibration and repeatability tests, perform hanging-load tests, and execute the full physical barcode-to-record loop. Add physical receipts only from actual execution.

Preserve the v0.1.3 authority sequence: canonical action → CaptureMachine → SessionStore JSONL/individual/checkpoint/recent pointer → commit receipt → Alice validation → feedback/progression. Do not bypass this path with UI, button, Bluetooth, Wi-Fi, or UNO Q adapters.

Non-claims remain binding: no physical device, firmware compile, Windows-native, UNO Q, Bluetooth, Wi-Fi, legal-for-trade, production-readiness, release-seal, Context runtime, or Drive upload claim without evidence.
