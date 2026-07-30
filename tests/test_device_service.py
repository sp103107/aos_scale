import pytest
from best_buds_weight_station.device_service import DeviceMode, DeviceProtocolError, DeviceService, ScriptedSerialTransport, SimulatedFirmwareTransport


def factory(responses, fail_write_at=None):
    transport=ScriptedSerialTransport(responses,fail_write_at=fail_write_at)
    return transport, (lambda port,baud,timeout: transport)


def test_connect_ping_status_protocol_validation():
    t,f=factory(['A,PONG\n','S,0.1.3,DEV-1,100.0,g\n'])
    service=DeviceService(transport_factory=f); status=service.connect('/dev/ttyTEST')
    assert status.connected and status.protocol_validated and status.device_id=='DEV-1'
    assert t.commands==['PING','STATUS']


def test_bad_ping_rejected():
    _,f=factory(['A,NOPE\n'])
    with pytest.raises(DeviceProtocolError): DeviceService(transport_factory=f).connect('/dev/x')


def test_stream_start_stop():
    t,f=factory(['A,PONG\n','S,0.1.3,DEV,100,g\n','A,STREAM_ON\n','A,STREAM_OFF\n'])
    service=DeviceService(transport_factory=f); service.connect('/dev/x'); service.start_stream(); assert service.status.streaming
    service.stop_stream(); assert not service.status.streaming and t.commands[-2:]==['STREAM_ON','STREAM_OFF']


def test_read_weight_parses_bounded_message():
    _,f=factory(['A,PONG\n','S,0.1.3,DEV,100,g\n','W,100,1234,12.340,1\n'])
    service=DeviceService(transport_factory=f); service.connect('/dev/x'); msg=service.read_weight()
    assert msg['weight_g']==12.34 and msg['raw_value']==1234 and not service.status.stale


def test_malformed_line_rejected():
    _,f=factory(['A,PONG\n','S,0.1.3,DEV,100,g\n','garbage\n'])
    service=DeviceService(transport_factory=f); service.connect('/dev/x')
    with pytest.raises(ValueError): service.read_weight()


def test_oversized_line_rejected():
    _,f=factory(['A,PONG\n','S,0.1.3,DEV,100,g\n','X'*200+'\n'])
    service=DeviceService(transport_factory=f,max_line_length=40); service.connect('/dev/x')
    with pytest.raises(ValueError): service.read_weight()


def test_disconnect_on_write_failure():
    t,f=factory(['A,PONG\n','S,0.1.3,DEV,100,g\n'],fail_write_at=2)
    service=DeviceService(transport_factory=f); service.connect('/dev/x')
    with pytest.raises(ConnectionError): service.read_weight()
    assert not service.status.connected


def test_controlled_reconnect():
    made=[]
    def f(port,baud,timeout):
        t=ScriptedSerialTransport(['A,PONG\n','S,0.1.3,DEV,100,g\n']); made.append(t); return t
    service=DeviceService(transport_factory=f); service.connect('/dev/x'); service.disconnect(); service.reconnect()
    assert service.status.connected and len(made)==2


def test_stale_reading_detection():
    now=[0.0]
    t,f=factory(['A,PONG\n','S,0.1.3,DEV,100,g\n','W,1,1,1.0,1\n'])
    service=DeviceService(transport_factory=f,clock=lambda:now[0],stale_after_s=2); service.connect('/dev/x'); service.read_weight()
    now[0]=3.0; assert service.is_stale()


def test_set_calibration_command():
    t,f=factory(['A,PONG\n','S,0.1.3,DEV,100,g\n','A,CAL_SET\n'])
    service=DeviceService(transport_factory=f); service.connect('/dev/x'); service.set_calibration(101.5)
    assert t.commands[-1].startswith('SET_CAL,101.50000000')


def test_simulator_evidence_is_not_physical():
    service=DeviceService(mode=DeviceMode.SERIAL_SIMULATOR,transport_factory=lambda p,b,t: SimulatedFirmwareTransport(p,b,t)); service.connect('SIM')
    evidence=service.evidence(); assert evidence['truth_class']=='SIMULATOR_PASS' and evidence['physical_device_pass'] is False


def test_physical_serial_open_is_only_source_present():
    _,f=factory(['A,PONG\n','S,0.1.3,DEV,100,g\n'])
    service=DeviceService(mode=DeviceMode.PHYSICAL_SERIAL,transport_factory=f); service.connect('/dev/x')
    assert service.evidence()['truth_class']=='SOURCE_PRESENT' and not service.evidence()['physical_device_pass']


def test_tare_retries_transient_hx711_not_ready():
    t, f = factory([
        'A,PONG\n', 'S,0.1.3,DEV,100,g\n',
        'E,HX711_NOT_READY,tare rejected\n',
        'A,TARE,OK\n',
    ])
    service = DeviceService(transport_factory=f, settle_s=0.0, sleep=lambda _s: None)
    service.connect('/dev/x')
    msg = service.tare()
    assert msg['kind'] == 'A' and t.commands.count('TARE') == 2


def test_read_weight_retries_transient_hx711_not_ready():
    t, f = factory([
        'A,PONG\n', 'S,0.1.3,DEV,100,g\n',
        'E,HX711_NOT_READY,sensor unavailable\n',
        'W,100,1234,0.050,1\n',
    ])
    service = DeviceService(transport_factory=f, settle_s=0.0, sleep=lambda _s: None)
    service.connect('/dev/x')
    msg = service.read_weight()
    assert msg['weight_g'] == 0.05 and t.commands.count('READ') == 2

    captured = []

    def f(port, baud, timeout):
        captured.append(baud)
        return ScriptedSerialTransport(['A,PONG\n', 'S,0.1.3,DEV,100,g\n'])

    service = DeviceService(transport_factory=f, settle_s=0.0)
    service.connect('/dev/x', baud=115200)
    service.disconnect()
    service.connect('/dev/x', baud=9600)
    assert captured == [115200, 9600]


def test_unsupported_baud_rejected():
    _, f = factory(['A,PONG\n', 'S,0.1.3,DEV,100,g\n'])
    with pytest.raises(ValueError, match='baud'):
        DeviceService(transport_factory=f, settle_s=0.0).connect('/dev/x', baud=57600)


def test_reconnect_retains_selected_baud():
    captured = []

    def f(port, baud, timeout):
        captured.append(baud)
        return ScriptedSerialTransport(['A,PONG\n', 'S,0.1.3,DEV,100,g\n'])

    service = DeviceService(transport_factory=f, settle_s=0.0)
    service.connect('/dev/x', baud=115200)
    service.disconnect()
    service.reconnect()
    assert captured == [115200, 115200]


def test_startup_chatter_does_not_break_ping_handshake():
    # Unsolicited STATUS from board reset must be discarded before PING response.
    _, f = factory([
        'S,0.1.3,DEV-BOOT,100.0,g\n',
        'A,PONG\n',
        'S,0.1.3,DEV-1,100.0,g\n',
    ])
    service = DeviceService(transport_factory=f, settle_s=0.0)
    status = service.connect('/dev/x', baud=115200)
    assert status.connected and status.protocol_validated and status.device_id == 'DEV-1'


def test_default_connect_baud_is_115200():
    captured = []

    def f(port, baud, timeout):
        captured.append(baud)
        return ScriptedSerialTransport(['A,PONG\n', 'S,0.1.3,DEV,100,g\n'])

    DeviceService(transport_factory=f, settle_s=0.0).connect('/dev/x')
    assert captured == [115200]
