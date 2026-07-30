# Run and File Management — v0.1.3

- Data directories are resolved, created when allowed, and write-tested before acceptance.
- New Run creates a repository-standard session folder and manifest on disk.
- Load Run accepts a run folder, session manifest, or authoritative ledger selection and validates identifiers, schema compatibility, and hash chain.
- Resume Last Run reads a durable pointer from the settings directory.
- Finish Run updates the run manifest and appends a non-weight run-finished event.
- Export remains non-authoritative and does not invalidate committed plant records if it fails.
