from __future__ import annotations
import json
from pathlib import Path

class StageCatalog:
    def __init__(self, repo_root: Path):
        self.repo_root=repo_root.resolve()
        product_version=(self.repo_root/'VERSION').read_text(encoding='utf-8').strip()
        catalog_path=self.repo_root/'pipeline'/f'stage_catalog.v{product_version}.json'
        if not catalog_path.exists():
            # Pipeline artifacts are archival and version-pinned (e.g. v0.1.9).
            # When the product version moves ahead, keep using the newest
            # existing catalog and align stage/plan lookups to its version.
            candidates=sorted((self.repo_root/'pipeline').glob('stage_catalog.v*.json'))
            if not candidates:
                raise FileNotFoundError(f'no stage catalog found under {self.repo_root/"pipeline"}')
            catalog_path=candidates[-1]
        self.version=catalog_path.name[len('stage_catalog.v'):-len('.json')]
        self.catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
        self.entries={item['stage_id']:item for item in self.catalog['stages']}
    def stage(self, stage_id: str) -> dict:
        if stage_id not in self.entries: raise KeyError(f'unknown stage: {stage_id}')
        return json.loads((self.repo_root/self.entries[stage_id]['path']).read_text(encoding='utf-8'))
    def plan(self, plan_id: str) -> dict:
        path=self.repo_root/'pipeline'/'plans'/f'{plan_id}.v{self.version}.json'
        if not path.exists(): raise KeyError(f'unknown plan: {plan_id}')
        return json.loads(path.read_text(encoding='utf-8'))
    def list(self) -> list[dict]:
        return [self.stage(item['stage_id']) for item in self.catalog['stages']]
