from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_runtime_execution_posture_is_evidence_gated():
    state=json.loads((ROOT/'repo_release_state.json').read_text())
    # Release state tracks the live product version (drift repair keeps it aligned).
    assert state['version']==(ROOT/'VERSION').read_text().strip()
    assert state['bump_scope']=='full_repo'
    assert state['execution_posture']=='real_execution_allowed'
    assert state['execution_authorized'] is True
    assert state['evidence_required'] is True
    assert state['claim_gate_required'] is True
    assert state['production_ready_claimed'] is False
    assert state['release_seal_claimed'] is False
    assert state['physical_device_status']=='not_run'

def test_context_sequence_ten_and_handoff_exist():
    ws=json.loads((ROOT/'context/working_set/working_set_update_0010.json').read_text())
    episode=json.loads((ROOT/'context/episodes/episode_0010_v0.1.9.json').read_text())
    assert ws['update_seq']==10
    assert episode['sequence']==10
    assert (ROOT/'context/resume_pack/resume_pack_manifest.v0.1.9.json').exists()
    assert (ROOT/'cursor/CURSOR_UNO_R3_PHYSICAL_INTEGRATION_HANDOFF_V0_1_9.md').exists()
