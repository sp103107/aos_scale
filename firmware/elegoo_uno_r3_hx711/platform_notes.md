# Platform Notes

Target FQBN: `arduino:avr:uno`. HX711 DOUT → D2, SCK → D3, VCC → 5V, GND → GND. Verify the load-cell datasheet; do not trust wire color alone.

Library: Rob Tillaart HX711 (tested 0.6.4). Use `begin(dout, sck, false, false)` so startup does not block on a missing/unready amp. Serial default: **115200**.
