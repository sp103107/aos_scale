# Windows Device Bring-up Notes (USB Serial)

**product_version_target:** `2.0.0-rc4` (BBWS SR7 S03)  
**scope:** operator PC bring-up hygiene only — not legal-for-trade / Metrc.

## How the app finds the scale

- The app never hardcodes a COM port. Ports are enumerated live via pyserial
  (`Scale → Scale Setup → Connect` lists what Windows currently exposes).
- Supported baud rates: 115200 (default) and 9600.
- USB serial only in this release; Bluetooth/Wi-Fi transports stay disabled.

## USB serial drivers

Most Arduino-compatible scale controllers use one of these USB-serial bridges.
Windows 10/11 usually installs them automatically via Windows Update; install
the vendor driver only if no COM port appears after plugging in.

| Bridge chip | Typical boards | Driver source |
|-------------|----------------|---------------|
| CH340 / CH341 | Elegoo / clone UNO R3 | WCH (wch-ic.com) CH341SER |
| FTDI FT232 | Genuine Arduino, many adapters | FTDI VCP driver (ftdichip.com) |
| CP210x | Some ESP/serial adapters | Silicon Labs VCP driver |

## If no COM port appears

1. Try another USB cable (charge-only cables expose no data lines).
2. Check Device Manager → Ports (COM & LPT); a yellow warning icon means a
   missing driver — install per the table above.
3. Close Arduino IDE / Serial Monitor — only one program can own the port.
4. Re-open Scale Setup; the port list refreshes on each open.

## Where run data lives on an installed PC

- App install (per-user): `%LOCALAPPDATA%\BestBudsWeightStation\app`
- Config / logs / runs / exports: `%LOCALAPPDATA%\BestBudsWeightStation\...`
- First run seeds the data folder to the platform runs directory — never
  relative to the exe or working directory.
- Session JSONL remains the authoritative record; exports are handoffs.

## Scale identity + profile bring-up (SR9)

1. Connect the scale in Scale Setup.
2. **Assign Device ID…** using `BBWS-SCALE-NNN` (or another `BBWS-…` board id). Device IDs must be unique on the floor.
3. Run Guided Calibration with a verified reference mass, then **ZERO**.
4. Run the **100 g Stability Test** (post-cal prompt or Scale Setup button). Review the recommendation, then **Confirm** to activate the profile.
5. On later reconnect, the station loads the active profile for that `device_id` (applies calibration factor and hanging-load stability).

Profiles live under `{config_dir}/scale_profiles/*.json`. They are local operational evidence only — not Metrc / legal-for-trade certification. Capture law is unchanged: scan → settle → lock → confirm → reset.

## Non-claims

- Not legal-for-trade / Metrc compliance; not a production weighing seal.
- Displayed grams require Guided Calibration with a verified reference mass.
- 100 g characterization is repeatability evidence, not certification.
- Scale profiles/receipts are local operational evidence; session JSONL remains authoritative.
