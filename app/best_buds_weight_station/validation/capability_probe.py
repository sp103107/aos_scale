from __future__ import annotations
import importlib.util, platform, shutil, subprocess, sys
from pathlib import Path
from typing import Any

def _cmd_version(command:list[str])->dict[str,Any]:
    exe=shutil.which(command[0])
    if not exe: return {"available":False,"path":None,"version":None}
    try:
        cp=subprocess.run(command,text=True,capture_output=True,timeout=10)
        text=(cp.stdout or cp.stderr).strip().splitlines()
        return {"available":cp.returncode==0,"path":exe,"version":text[0] if text else None,"exit_code":cp.returncode}
    except Exception as exc:
        return {"available":False,"path":exe,"version":None,"error":f"{type(exc).__name__}: {exc}"}

def probe(repo_root:Path)->dict[str,Any]:
    try:
        from ..device_service import DeviceService
        ports=[p.__dict__ for p in DeviceService.discover_ports()]
    except Exception as exc:
        ports=[]; port_error=f"{type(exc).__name__}: {exc}"
    else: port_error=None
    return {
      "python":{"available":True,"version":sys.version.split()[0],"executable":sys.executable},
      "platform":{"system":platform.system(),"release":platform.release(),"machine":platform.machine()},
      "modules":{name:importlib.util.find_spec(name) is not None for name in ("pytest","jsonschema","yaml","serial","openpyxl")},
      "tools":{
        "arduino_cli":_cmd_version(["arduino-cli","version"]),
        "dpkg_deb":_cmd_version(["dpkg-deb","--version"]),
        "git":_cmd_version(["git","--version"]),
      },
      "serial_ports":ports,
      "serial_port_probe_error":port_error,
      "repo_root":str(repo_root),
    }
