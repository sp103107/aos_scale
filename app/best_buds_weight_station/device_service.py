from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Callable, Protocol

from .models import now_rfc3339
from .simulator import parse_line

# Device-neutral USB serial rates. Bluetooth/Wi-Fi transports are out of scope.
ALLOWED_BAUD_RATES = frozenset({115200, 9600})
DEFAULT_BAUD_RATE = 115200


class DeviceMode(str, Enum):
    PHYSICAL_SERIAL = "physical_serial"
    SERIAL_SIMULATOR = "serial_simulator"


@dataclass(frozen=True)
class SerialPortCandidate:
    device: str
    description: str = ""
    hardware_id: str = ""


@dataclass
class DeviceStatus:
    connected: bool = False
    mode: str = DeviceMode.PHYSICAL_SERIAL.value
    port: str | None = None
    protocol_validated: bool = False
    streaming: bool = False
    device_id: str | None = None
    firmware_version: str | None = None
    calibration_factor: float | None = None
    unit: str = "g"
    last_reading_at: float | None = None
    stale: bool = True
    disconnect_reason: str | None = None
    truth_class: str = "SOURCE_PRESENT"
    baud_rate: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SerialTransport(Protocol):
    is_open: bool

    def open(self) -> None: ...
    def close(self) -> None: ...
    def write_line(self, line: str) -> None: ...
    def read_line(self, max_length: int) -> str: ...


class PySerialTransport:
    def __init__(self, port: str, baud: int = DEFAULT_BAUD_RATE, timeout: float = 1.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.serial = None
        self.is_open = False

    def open(self) -> None:
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError("pyserial is required for physical serial operation") from exc
        try:
            self.serial = serial.Serial(self.port, self.baud, timeout=self.timeout)
        except Exception as exc:
            # Preserve original error class for operator diagnostics (busy port, missing device).
            raise
        self.is_open = bool(self.serial.is_open)

    def close(self) -> None:
        if self.serial is not None:
            self.serial.close()
        self.is_open = False

    def write_line(self, line: str) -> None:
        if not self.serial or not self.is_open:
            raise ConnectionError("serial transport is not connected")
        self.serial.write((line + "\n").encode("ascii", "strict"))

    def read_line(self, max_length: int) -> str:
        if not self.serial or not self.is_open:
            raise ConnectionError("serial transport is not connected")
        data = self.serial.readline(max_length + 1)
        if len(data) > max_length:
            raise ValueError("serial line too long")
        return data.decode("ascii", "strict")


class DeviceProtocolError(RuntimeError):
    pass


class DeviceService:
    COMMANDS = {"PING", "STATUS", "TARE", "READ", "STREAM_ON", "STREAM_OFF", "SET_UNIT,g"}

    def __init__(
        self,
        *,
        mode: DeviceMode = DeviceMode.PHYSICAL_SERIAL,
        transport_factory: Callable[[str, int, float], SerialTransport] | None = None,
        stale_after_s: float = 2.5,
        max_line_length: int = 160,
        clock: Callable[[], float] = time.monotonic,
        settle_s: float = 0.0,
        sleep: Callable[[float], None] = time.sleep,
        handshake_attempts: int = 8,
    ):
        self.mode = mode
        self.transport_factory = transport_factory or (lambda port, baud, timeout: PySerialTransport(port, baud, timeout))
        self.stale_after_s = stale_after_s
        self.max_line_length = max_line_length
        self.clock = clock
        self.settle_s = settle_s
        self.sleep = sleep
        self.handshake_attempts = handshake_attempts
        self.transport: SerialTransport | None = None
        self.status = DeviceStatus(mode=mode.value, truth_class="SIMULATOR_PASS" if mode == DeviceMode.SERIAL_SIMULATOR else "SOURCE_PRESENT")
        self.last_message: dict[str, Any] | None = None
        self._last_port: str | None = None
        self._last_baud = DEFAULT_BAUD_RATE
        self._reconnect_attempts = 0
        # Host-side display zero: firmware factor is often still 1.0 during bring-up,
        # so hardware TARE alone can leave a huge residual labeled as grams.
        self.host_zero_offset_g: float = 0.0
        self.invert_weight_sign: bool = False

    @staticmethod
    def discover_ports() -> list[SerialPortCandidate]:
        try:
            from serial.tools import list_ports
        except ImportError:
            return []
        candidates = [
            SerialPortCandidate(item.device, item.description or "", item.hwid or "")
            for item in list_ports.comports()
        ]
        return sorted(candidates, key=lambda item: item.device)

    def connect(
        self,
        port: str,
        *,
        baud: int = DEFAULT_BAUD_RATE,
        timeout: float = 1.0,
        validate_protocol: bool = True,
    ) -> DeviceStatus:
        if not port or "\x00" in port or len(port) > 256:
            raise ValueError("invalid serial port")
        if baud not in ALLOWED_BAUD_RATES:
            raise ValueError(f"unsupported baud rate {baud}; allowed: {sorted(ALLOWED_BAUD_RATES)}")
        self.disconnect(silent=True)
        try:
            self.transport = self.transport_factory(port, baud, timeout)
            self.transport.open()
            self._last_port = port
            self._last_baud = baud
            self.status = DeviceStatus(
                connected=True,
                mode=self.mode.value,
                port=port,
                baud_rate=baud,
                stale=True,
                truth_class="SIMULATOR_PASS" if self.mode == DeviceMode.SERIAL_SIMULATOR else "SOURCE_PRESENT",
            )
            self.clear_host_zero()
            if self.settle_s > 0:
                self.sleep(self.settle_s)
            if validate_protocol:
                self._drain_startup_chatter()
                self.ping()
                self.read_status()
                self.status.protocol_validated = True
        except Exception:
            self.disconnect(silent=True, reason="connect_failed")
            raise
        return self.status

    def disconnect(self, *, silent: bool = False, reason: str | None = None) -> DeviceStatus:
        if self.transport is not None:
            try:
                self.transport.close()
            except Exception:
                if not silent:
                    raise
        self.transport = None
        self.status.connected = False
        self.status.streaming = False
        self.status.protocol_validated = False
        self.status.stale = True
        self.status.disconnect_reason = reason
        self.clear_host_zero()
        return self.status

    def clear_host_zero(self) -> None:
        """Clear host display zero/polarity adjustments."""
        self.host_zero_offset_g = 0.0
        self.invert_weight_sign = False

    def set_host_zero_offset(self, offset_g: float, *, invert_sign: bool | None = None) -> None:
        """Apply a host-side zero so live weight reads near 0 after Zero."""
        self.host_zero_offset_g = float(offset_g)
        if invert_sign is not None:
            self.invert_weight_sign = bool(invert_sign)

    def _decorate_weight_message(self, message: dict[str, Any]) -> dict[str, Any]:
        if message.get("kind") != "W":
            return message
        out = dict(message)
        weight = float(out["weight_g"])
        if self.invert_weight_sign:
            weight = -weight
        weight = weight - self.host_zero_offset_g
        out["weight_g"] = weight
        out["host_zero_offset_g"] = self.host_zero_offset_g
        out["invert_weight_sign"] = self.invert_weight_sign
        return out

    def _drain_startup_chatter(self) -> None:
        """Discard unsolicited lines emitted during USB board reset."""
        if not self.transport or not self.status.connected:
            return
        # Scripted/simulated transports may not expose a flushable buffer; best-effort only.
        serial_obj = getattr(self.transport, "serial", None)
        if serial_obj is None:
            return
        try:
            deadline = self.clock() + 0.35
            while self.clock() < deadline:
                waiting = getattr(serial_obj, "in_waiting", 0)
                if not waiting:
                    break
                self.transport.read_line(self.max_line_length)
        except Exception:
            return

    def _send(self, command: str) -> None:
        if not self.transport or not self.status.connected:
            raise ConnectionError("device is disconnected")
        if len(command) > 80 or "\n" in command or "\r" in command:
            raise ValueError("malformed command")
        allowed = command in self.COMMANDS or command.startswith("SET_CAL,")
        if not allowed:
            raise ValueError("unsupported firmware command")
        try:
            self.transport.write_line(command)
        except Exception as exc:
            self.disconnect(silent=True, reason=type(exc).__name__)
            raise ConnectionError("serial write failed") from exc

    def _read(self) -> dict[str, Any]:
        if not self.transport or not self.status.connected:
            raise ConnectionError("device is disconnected")
        try:
            line = self.transport.read_line(self.max_line_length)
            if not line:
                raise TimeoutError("serial response timed out")
            message = parse_line(line)
        except Exception as exc:
            if isinstance(exc, (ConnectionError, OSError)):
                self.disconnect(silent=True, reason=type(exc).__name__)
            raise
        self.last_message = message
        if message.get("kind") == "W":
            message = self._decorate_weight_message(message)
            self.last_message = message
            self.status.last_reading_at = self.clock()
            self.status.stale = False
        if message.get("kind") == "S":
            self.status.device_id = str(message["device_id"])
            self.status.firmware_version = str(message["firmware_version"])
            self.status.calibration_factor = float(message["calibration_factor"])
            self.status.unit = str(message["unit"])
        return message

    def _read_expected(self, *, kinds: set[str], attempts: int | None = None) -> dict[str, Any]:
        """Read until an expected response kind appears, skipping startup chatter."""
        remaining = self.handshake_attempts if attempts is None else attempts
        last: dict[str, Any] | None = None
        for _ in range(remaining):
            message = self._read()
            last = message
            if message.get("kind") in kinds:
                return message
        raise DeviceProtocolError(f"expected one of {sorted(kinds)}; got {last}")

    def ping(self) -> dict[str, Any]:
        self._send("PING")
        message = self._read_expected(kinds={"A"})
        fields = message.get("fields") or []
        # Accept A,PONG or A,PING,OK for firmware compatibility during transition.
        if not fields:
            raise DeviceProtocolError("unexpected PING response")
        if fields[0] == "PONG":
            return message
        if fields[0] == "PING" and len(fields) > 1 and fields[1] in {"OK", "PONG"}:
            return message
        raise DeviceProtocolError("unexpected PING response")

    def read_status(self) -> dict[str, Any]:
        self._send("STATUS")
        message = self._read_expected(kinds={"S"})
        if message.get("unit") != "g":
            raise DeviceProtocolError("device unit is not grams")
        return message

    def _flush_input(self) -> None:
        """Discard pending UART bytes so command/response pairing stays clean."""
        if not self.transport:
            return
        serial_obj = getattr(self.transport, "serial", None)
        if serial_obj is not None:
            try:
                serial_obj.reset_input_buffer()
                return
            except Exception:
                pass
        # Scripted transports: drop queued lines if present.
        responses = getattr(self.transport, "responses", None)
        if isinstance(responses, list):
            # Keep scripted responses; they are intentional.
            return
        queue = getattr(self.transport, "queue", None)
        if isinstance(queue, list) and queue and getattr(self.transport, "streaming", False):
            # Simulated stream may keep producing; no byte buffer to flush.
            return

    def start_stream(self) -> dict[str, Any]:
        self._flush_input()
        self._send("STREAM_ON")
        response = self._read_expected(kinds={"A"}, attempts=max(self.handshake_attempts, 16))
        self.status.streaming = True
        return response

    def stop_stream(self) -> dict[str, Any]:
        self._send("STREAM_OFF")
        # While streaming, unread W lines may precede the ACK.
        response = self._read_expected(kinds={"A"}, attempts=max(self.handshake_attempts, 24))
        self.status.streaming = False
        self._flush_input()
        return response

    def _hx711_retry(self, label: str, attempt: Callable[[], dict[str, Any]], *, attempts: int = 8) -> dict[str, Any]:
        """Retry when firmware reports a transient HX711_NOT_READY.

        Live streaming can still show motion because later frames succeed; a single
        TARE/READ must wait out brief DOUT-not-ready windows after STREAM_OFF.
        """
        last_error: Exception | None = None
        for index in range(max(1, attempts)):
            try:
                return attempt()
            except DeviceProtocolError as exc:
                last_error = exc
                if "HX711_NOT_READY" not in str(exc):
                    raise
                self.sleep(0.05 + (0.05 * index))
        assert last_error is not None
        raise DeviceProtocolError(f"{label} failed after retries: {last_error}") from last_error

    def read_weight(self) -> dict[str, Any]:
        def once() -> dict[str, Any]:
            self._flush_input()
            self._send("READ")
            message = self._read_expected(kinds={"W", "E"}, attempts=max(self.handshake_attempts, 16))
            if message.get("kind") == "E":
                fields = message.get("fields") or []
                code = fields[0] if fields else "DEVICE_ERROR"
                raise DeviceProtocolError(f"weight read failed: {code}")
            if message.get("kind") != "W":
                raise DeviceProtocolError("weight response required")
            return message

        return self._hx711_retry("weight read", once)

    def read_stream_message(self) -> dict[str, Any]:
        if not self.status.streaming:
            raise RuntimeError("streaming is not active")
        return self._read()

    def tare(self) -> dict[str, Any]:
        def once() -> dict[str, Any]:
            self._flush_input()
            self._send("TARE")
            message = self._read_expected(kinds={"A", "E"}, attempts=max(self.handshake_attempts, 16))
            if message.get("kind") == "E":
                fields = message.get("fields") or []
                code = fields[0] if fields else "DEVICE_ERROR"
                raise DeviceProtocolError(f"tare failed: {code}")
            if message.get("kind") != "A" or not message.get("fields") or message["fields"][0] not in {"TARE", "TARED", "OK"}:
                raise DeviceProtocolError("tare was not acknowledged")
            return message

        # Brief settle after stream stop so DOUT can go ready before the first TARE.
        self.sleep(0.15)
        return self._hx711_retry("tare", once)

    def set_calibration(self, factor: float) -> dict[str, Any]:
        if not isinstance(factor, (int, float)) or factor == 0 or abs(float(factor)) > 1e12:
            raise ValueError("invalid calibration factor")
        self._send(f"SET_CAL,{float(factor):.8f}")
        message = self._read()
        if message.get("kind") != "A":
            raise DeviceProtocolError("calibration factor was not acknowledged")
        return message

    def is_stale(self) -> bool:
        last = self.status.last_reading_at
        self.status.stale = last is None or (self.clock() - last) > self.stale_after_s
        return self.status.stale

    def reconnect(self, *, max_attempts: int = 2) -> DeviceStatus:
        if self.status.connected:
            return self.status
        if not self._last_port:
            raise RuntimeError("no previous serial port is available")
        last_error: Exception | None = None
        for _ in range(max_attempts):
            self._reconnect_attempts += 1
            try:
                return self.connect(self._last_port, baud=self._last_baud)
            except Exception as exc:
                last_error = exc
        raise ConnectionError("controlled reconnect failed") from last_error

    def evidence(self) -> dict[str, Any]:
        return {
            "evidence_id": f"device-status-{int(time.time())}",
            "created_at": now_rfc3339(),
            "mode": self.mode.value,
            "truth_class": self.status.truth_class,
            "physical_device_pass": False,
            "status": self.status.to_dict(),
            "non_claims": [
                "Opening a serial port is not physical load-cell proof.",
                "Simulator responses are not physical hardware evidence.",
            ],
        }


class ScriptedSerialTransport:
    """Deterministic local test transport; never labeled physical evidence."""

    def __init__(self, responses: list[str], *, fail_write_at: int | None = None):
        self.responses = list(responses)
        self.commands: list[str] = []
        self.is_open = False
        self.fail_write_at = fail_write_at

    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False

    def write_line(self, line: str) -> None:
        if not self.is_open:
            raise ConnectionError("scripted transport closed")
        if self.fail_write_at is not None and len(self.commands) == self.fail_write_at:
            raise OSError("injected serial disconnect")
        self.commands.append(line)

    def read_line(self, max_length: int) -> str:
        if not self.is_open:
            raise ConnectionError("scripted transport closed")
        if not self.responses:
            raise TimeoutError("no scripted response")
        line = self.responses.pop(0)
        if len(line.encode("ascii")) > max_length:
            return line
        return line


class SimulatedFirmwareTransport:
    """Command-responsive firmware simulator used for local application tests."""

    def __init__(self, port: str = "SIMULATOR", baud: int = DEFAULT_BAUD_RATE, timeout: float = 1.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.is_open = False
        self.queue: list[str] = []
        self.commands: list[str] = []
        self.calibration_factor = 103.2
        self.unit = "g"
        self.weight_g = 0.0
        self.raw_value = 0
        self.device_ms = 0
        self.streaming = False

    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False

    def set_weight(self, weight_g: float) -> None:
        self.weight_g = float(weight_g)
        self.raw_value = int(self.weight_g * self.calibration_factor)
        self.device_ms += 150

    def write_line(self, line: str) -> None:
        if not self.is_open:
            raise ConnectionError("simulator transport closed")
        self.commands.append(line)
        if line == "PING":
            self.queue.append("A,PONG\n")
        elif line == "STATUS":
            self.queue.append(f"S,0.1.8-sim,SIM-UNO-001,{self.calibration_factor:.8f},{self.unit}\n")
        elif line == "TARE":
            self.weight_g = 0.0
            self.raw_value = 0
            self.queue.append("A,TARED\n")
        elif line == "READ":
            self.queue.append(f"W,{self.device_ms},{self.raw_value},{self.weight_g:.3f},1\n")
        elif line == "STREAM_ON":
            self.streaming = True
            self.queue.append("A,STREAM_ON\n")
        elif line == "STREAM_OFF":
            self.streaming = False
            self.queue.append("A,STREAM_OFF\n")
        elif line.startswith("SET_CAL,"):
            self.calibration_factor = float(line.split(",", 1)[1])
            self.queue.append("A,CAL_SET\n")
        elif line == "SET_UNIT,g":
            self.unit = "g"
            self.queue.append("A,UNIT_SET\n")
        else:
            self.queue.append("E,UNKNOWN_COMMAND\n")

    def read_line(self, max_length: int) -> str:
        if not self.is_open:
            raise ConnectionError("simulator transport closed")
        if self.queue:
            return self.queue.pop(0)
        if self.streaming:
            return f"W,{self.device_ms},{self.raw_value},{self.weight_g:.3f},1\n"
        raise TimeoutError("no simulator response")
