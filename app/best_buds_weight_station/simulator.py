from __future__ import annotations
from dataclasses import dataclass
from time import sleep

@dataclass(frozen=True)
class SimReading:
    device_ms:int; raw_value:int; weight_g:float; ready:bool=True
    def line(self): return f'W,{self.device_ms},{self.raw_value},{self.weight_g:.3f},{1 if self.ready else 0}'

def stable_sequence(target_g=125.0):
    values=[0.0,12.5,84.2,target_g-0.2,target_g+0.2,target_g-0.1,target_g+0.1,target_g,target_g+0.05,target_g-0.05,target_g]
    return [SimReading(i*150,int(v*103.2),v,True) for i,v in enumerate(values)]

def parse_line(line):
    parts=line.strip().split(','); kind=parts[0]
    if kind=='W' and len(parts)==5: return {'kind':'W','device_ms':int(parts[1]),'raw_value':int(parts[2]),'weight_g':float(parts[3]),'ready':parts[4]=='1'}
    if kind=='S' and len(parts)>=5: return {'kind':'S','firmware_version':parts[1],'device_id':parts[2],'calibration_factor':float(parts[3]),'unit':parts[4]}
    if kind in ('E','A'): return {'kind':kind,'fields':parts[1:]}
    preview = line.strip()[:80]
    if preview.lower().startswith('raw') or 'hx711' in preview.lower():
        raise ValueError(
            f"malformed serial line from raw HX711 test sketch ({preview!r}); "
            "flash best_buds_scale_firmware.ino"
        )
    raise ValueError(f'malformed serial line ({preview!r})')
