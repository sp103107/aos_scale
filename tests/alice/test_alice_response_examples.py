import json
from pathlib import Path
import jsonschema
from best_buds_weight_station.alice import robust_examples
from best_buds_weight_station.ui import alice_panel_snapshot

ROOT=Path(__file__).parents[2]


def test_all_structured_response_examples_validate():
    schema=json.load((ROOT/'contracts/alice/alice_response.schema.json').open())
    examples=robust_examples()
    for name in ['missing_cultivar','automatic_commit','manual_confirm','jsonl_failure','xlsx_pending','duplicate','serial_disconnect','restart_recovery']:
        jsonschema.validate(examples[name],schema)


def test_required_robust_example_messages():
    examples=robust_examples()
    assert examples['automatic_commit']['operator_message']=='Record BB-HR-2026-0719-A-000042 saved locally. Net weight: 1200.0 g. Scan the next container.'
    assert examples['duplicate']['operator_message']=='This command was already committed as record BB-HR-2026-0719-A-000042. No second record was created.'
    assert 'Authoritative local storage failed' in examples['jsonl_failure']['operator_message']


def test_ui_panel_snapshot_surfaces_truth_action_and_evidence():
    snapshot=alice_panel_snapshot(robust_examples()['automatic_commit'])
    assert snapshot['truth_class']=='RECEIPT_CONFIRMED'
    assert snapshot['required_action']=='scan_barcode'
    assert 'commit_receipt' in snapshot['evidence_summary']
