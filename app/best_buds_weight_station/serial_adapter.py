"""Legacy serial compatibility adapter.

Canonical physical capture path: PySerialTransport -> DeviceService -> ScaleReadingWorker.
This module is preserved for historical compatibility only and must not be selected by new integrations.
"""
from __future__ import annotations

LEGACY_COMPATIBILITY_ADAPTER = True
from .simulator import parse_line
class SerialScale:
    def __init__(self,port,baud=9600,timeout=1.0,max_line=160): self.port=port; self.baud=baud; self.timeout=timeout; self.max_line=max_line; self.serial=None
    def connect(self):
        try: import serial
        except ImportError as e: raise RuntimeError('pyserial is required for physical serial operation') from e
        self.serial=serial.Serial(self.port,self.baud,timeout=self.timeout)
    def command(self,text):
        if not self.serial: raise RuntimeError('not connected')
        if len(text)>80 or '\n' in text or '\r' in text: raise ValueError('malformed command')
        self.serial.write((text+'\n').encode('ascii'))
    def read(self):
        line=self.serial.readline(self.max_line+1)
        if len(line)>self.max_line: raise ValueError('serial line too long')
        return parse_line(line.decode('ascii','strict'))
