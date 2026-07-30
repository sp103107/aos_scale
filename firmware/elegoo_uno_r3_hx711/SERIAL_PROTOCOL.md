# Serial Protocol

115200 8N1, newline-delimited ASCII, maximum command length 80 bytes.

Compatibility: hosts may also open at 9600 for older flashed boards; current firmware defaults to **115200**.

Commands: `PING`, `STATUS`, `TARE`, `READ`, `STREAM_ON`, `STREAM_OFF`, `SET_CAL,<factor>`, `SET_UNIT,g`.

Responses:

- `A,PONG` — PING acknowledgement
- `A,<command>,<status>` — other acknowledgements
- `S,<firmware>,<device>,<factor>,<unit>` — STATUS
- `W,<ms>,<raw>,<grams>,<ready>` — weight sample
- `E,<code>,<message>` — error (for example `HX711_NOT_READY`)

Notes:

- Setup must remain non-blocking so `PING`/`STATUS` work even if the HX711 is unready.
- With Rob Tillaart HX711 0.6.x, call `begin(dataPin, clockPin, false, false)` to avoid `reset()` → blocking `read()` hang.
- Default pins: DOUT=D2, SCK=D3.
