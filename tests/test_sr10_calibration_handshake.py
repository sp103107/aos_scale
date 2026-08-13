"""SR10 calibration handshake integrity — matched-ACK and Alice error split."""
from __future__ import annotations

import pytest

from best_buds_weight_station.alice.authority import operator_safe_error
from best_buds_weight_station.device_service import (
    DeviceProtocolError,
    DeviceService,
    ScriptedSerialTransport,
    SimulatedFirmwareTransport,
)


def _factory(responses: list[str]):
    transport = ScriptedSerialTransport(responses)
    return transport, (lambda port, baud, timeout: transport)


def _connected(responses_after_handshake: list[str]) -> tuple[ScriptedSerialTransport, DeviceService]:
    responses = ["A,PONG\n", "S,0.1.5,BBWS-USB-001,1.0,g\n", *responses_after_handshake]
    transport, factory = _factory(responses)
    service = DeviceService(transport_factory=factory, settle_s=0.0, sleep=lambda _s: None)
    service.connect("/dev/sr10")
    return transport, service


def test_set_cal_skips_weight_and_leftover_stream_off_ack():
    """Interleaved W + A,STREAM_OFF,OK must not steal the SET_CAL ACK."""
    t, service = _connected(
        [
            "W,10,100,1.000,1\n",
            "A,STREAM_OFF,OK\n",
            "A,SET_CAL,OK\n",
        ]
    )
    ack = service.set_calibration(154.396667)
    assert ack["kind"] == "A"
    assert ack["fields"][0] == "SET_CAL"
    assert t.commands[-1].startswith("SET_CAL,154.39666700")


def test_set_cal_unmatched_ack_only_times_out_with_distinct_error():
    t, service = _connected(["A,STREAM_OFF,OK\n", "A,STREAM_OFF,OK\n"])
    with pytest.raises(DeviceProtocolError) as excinfo:
        service.set_calibration(100.0)
    message = str(excinfo.value).lower()
    assert "matched ack" in message
    assert "set_cal" in message
    assert "interleaving" in message


def test_simulator_cal_set_alias_still_accepted():
    service = DeviceService(
        transport_factory=lambda p, b, t: SimulatedFirmwareTransport(p, b, t),
        settle_s=0.0,
        sleep=lambda _s: None,
    )
    service.connect("SIM")
    ack = service.set_calibration(103.2)
    assert ack["fields"][0] == "CAL_SET"


def test_stop_stream_matched_ack_skips_weight_lines():
    t, service = _connected(
        [
            "A,STREAM_ON,OK\n",
            "W,1,1,0.1,1\n",
            "W,2,2,0.2,1\n",
            "A,STREAM_OFF,OK\n",
        ]
    )
    service.start_stream()
    assert service.status.streaming
    service.stop_stream()
    assert not service.status.streaming
    assert t.commands[-2:] == ["STREAM_ON", "STREAM_OFF"]


def test_set_device_id_matched_ack_skips_leftover_stream_off():
    t, service = _connected(
        [
            "A,STREAM_OFF,OK\n",
            "A,SET_DEVICE_ID,OK\n",
            "S,0.1.5,BBWS-SCALE-001,1.0,g\n",
        ]
    )
    result = service.set_device_id("BBWS-SCALE-001")
    assert result["device_id"] == "BBWS-SCALE-001"
    assert any(c.startswith("SET_DEVICE_ID,BBWS-SCALE-001") for c in t.commands)


def test_alice_leftover_ack_message_is_not_streaming_blanket():
    msg = operator_safe_error(
        DeviceProtocolError("matched ACK for SET_CAL timed out after interleaving replies; last=...")
    )
    assert "leftover" in msg.lower() or "handshake" in msg.lower()
    assert "still streaming" not in msg.lower()


def test_alice_raw_hx711_dump_still_points_at_firmware_flash():
    msg = operator_safe_error(
        ValueError("malformed serial line from raw HX711 test sketch ('raw hx711...')")
    )
    assert "not running the weight-station firmware" in msg
    assert "best_buds_scale_firmware.ino" in msg


def test_alice_bad_cal_rejected_message():
    msg = operator_safe_error(DeviceProtocolError("calibration rejected: BAD_CAL"))
    assert "rejected the calibration factor" in msg.lower()
