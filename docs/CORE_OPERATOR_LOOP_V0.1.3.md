# Core Operator Loop — v0.1.3

The active UI dispatches canonical actions to `ApplicationController`. The controller routes capture actions into the preserved `CaptureMachine`; it does not directly write weight records.

## Automatic mode

`barcode.submit → reading.ingest → stability detector → SessionStore.commit → Alice receipt validation → feedback → WAITING_FOR_BARCODE`

## Manual mode

`barcode.submit → reading.ingest → MANUAL_CONFIRM → capture.confirm → SessionStore.commit → Alice receipt validation → feedback → WAITING_FOR_BARCODE`

`capture.cancel` clears only uncommitted item state. `run.finish` cannot mutate committed weight records.
