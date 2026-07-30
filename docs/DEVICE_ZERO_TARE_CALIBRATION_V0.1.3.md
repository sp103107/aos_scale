# Device, Zero, Tare, and Calibration — v0.1.3

The serial service implements candidate-port enumeration, explicit selection, 9600-baud connection, PING, STATUS, READ, STREAM_ON/OFF, bounded parsing, stale-read detection, disconnect, and controlled reconnect.

Zero Scale sends `TARE`, requires acknowledgement, evaluates near-zero samples, and writes a zero receipt. Container tare supports stable capture and operator-entered known values. Calibration requires maintenance authorization, zero and loaded raw samples, a verified reference weight, proposal calculation, local tolerance testing, protected second confirmation, `SET_CAL`, and a confirming STATUS response.

All current calibration execution uses test/simulator evidence. No legal-for-trade or physical calibration claim is made.
