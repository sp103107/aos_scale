# Windows Package Smoke Checklist — BBWS SR1 S10

## Dev entry smoke

- [ ] `python -m best_buds_weight_station` starts UI (or CLI help)
- [ ] Simulator bootstrap can create a run and save one plant
- [ ] `ACTIVE_ARC.yaml` points at series-complete after S10E10
- [ ] `scripts/reconcile_export_jsonl.py` exits 0 on fixture session

## Installer notes (when binaries built)

- [ ] Inno/PyInstaller artifact launches without missing DLL
- [ ] Data root writable
- [ ] No Authenticode / release-seal claim from season push alone

## Tag policy

- Prefer series tag `bbws-sr1-complete` on `0.1.9` unless VERSION advances in S10
- Optional prereleases: `v0.1.9-bbws-s05`, `v0.1.9-bbws-s07`
