from __future__ import annotations
import json
from pathlib import Path

class ValidationGraph:
    def __init__(self, repo_root: Path):
        self.path=repo_root/"validation/llm_harness/validation_graph.json"
        self.data=json.loads(self.path.read_text(encoding="utf-8"))
        self.nodes={n["lane"]:n for n in self.data["lanes"]}
    def prerequisites(self,lane:str)->list[str]:
        if lane not in self.nodes: raise ValueError(f"unknown lane: {lane}")
        return list(self.nodes[lane].get("requires",[]))
    def ordered_lanes(self)->list[str]: return [n["lane"] for n in self.data["lanes"]]
