from best_buds_weight_station.alice import TruthClass, robust_examples


def test_truth_classes_are_not_overloaded():
    examples = robust_examples()
    firmware = examples['firmware_blocked']
    assert firmware['truth_class'] == TruthClass.BLOCKED.value
    refs = {item['evidence_type']: item['truth_class'] for item in firmware['evidence_refs']}
    assert refs == {
        'firmware_source': TruthClass.SOURCE_PRESENT.value,
        'firmware_compile': TruthClass.BLOCKED.value,
        'physical_hardware': TruthClass.NOT_RUN.value,
    }
    assert examples['simulator_vs_physical']['truth_class'] == TruthClass.SIMULATOR_PASS.value


def test_simulator_statement_preserves_physical_non_claim():
    example = robust_examples()['simulator_vs_physical']
    assert 'serial simulator' in example['statement']
    assert 'No physical UNO R3' in example['statement']
    assert example['non_claims']
