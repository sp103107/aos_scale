from __future__ import annotations
import json
from pathlib import Path
from best_buds_weight_station.stage_runner import StageRunner

ROOT=Path(__file__).resolve().parents[1]

def test_stage_catalog_and_plans_are_version_aligned():
    runner=StageRunner(ROOT,persist=False)
    assert runner.version=='0.1.9'
    stages=runner.catalog.list()
    assert len(stages)==11
    assert stages[0]['stage_id']=='00_repository_preflight'
    assert stages[-1]['stage_id']=='100_cursor_handoff'
    plan=runner.catalog.plan('cursor_ready')
    assert plan['version']=='0.1.9'
    assert plan['stages']==[stage['stage_id'] for stage in stages]

def test_stage_runner_executes_a_real_validation_command():
    result=StageRunner(ROOT,persist=False).run_stage('10_naming_concordance',run_id='pytest-v018')
    assert result['status']=='PASS'
    assert result['commands'][0]['exit_code']==0
    assert result['evidence_class']=='runtime_execution_pass'

def test_stage_contracts_parse():
    for path in (ROOT/'pipeline/stages').glob('*.json'):
        data=json.loads(path.read_text())
        assert data['version']=='0.1.9'
        assert data['commands']
        assert data['receipt_path'].startswith('validation/receipts/stages/')
