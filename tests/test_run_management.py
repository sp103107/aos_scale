import json
from pathlib import Path
import pytest
from best_buds_weight_station.run_manager import RunDefinition, RunManager
from best_buds_weight_station.settings import AppSettings, SettingsStore
from tests.v013_helpers import definition


def test_data_location_created_and_persisted(tmp_path):
    store = SettingsStore(tmp_path/'config')
    settings = store.save(AppSettings(data_root=str(tmp_path/'data')))
    assert Path(settings.data_root).is_dir() and store.load().data_root == str((tmp_path/'data').resolve())


def test_invalid_data_location_file_rejected(tmp_path):
    target=tmp_path/'file'; target.write_text('x')
    with pytest.raises(ValueError): SettingsStore.validate_data_root(target)


def test_new_run_creates_real_files_and_pointer(tmp_path):
    settings=SettingsStore(tmp_path/'config'); settings.save(AppSettings(data_root=str(tmp_path/'data')))
    loaded=RunManager(settings).create(RunDefinition(**definition('manual','SESSION-1')))
    assert loaded.manifest_path.exists() and loaded.store.records_path.parent.exists()
    pointer=settings.read_recent_run(); assert pointer['session_id']=='SESSION-1' and pointer['last_sequence']==0


def test_new_run_does_not_overwrite_existing(tmp_path):
    settings=SettingsStore(tmp_path/'config'); settings.save(AppSettings(data_root=str(tmp_path/'data')))
    manager=RunManager(settings); manager.create(RunDefinition(**definition('manual','SAME')))
    with pytest.raises(FileExistsError): manager.create(RunDefinition(**definition('manual','SAME')))


def test_load_run_validates_chain(tmp_path):
    settings=SettingsStore(tmp_path/'config'); settings.save(AppSettings(data_root=str(tmp_path/'data')))
    manager=RunManager(settings); created=manager.create(RunDefinition(**definition('manual','LOAD-1')))
    loaded=manager.load(created.manifest_path)
    assert loaded.store.verify_chain()==(True,'ok') and loaded.definition.run_id=='HR-2026-TEST'


def test_load_invalid_manifest_rejected(tmp_path):
    path=tmp_path/'session_manifest.json'; path.write_text('{}')
    settings=SettingsStore(tmp_path/'config'); settings.save(AppSettings(data_root=str(tmp_path/'data')))
    with pytest.raises((TypeError,ValueError)): RunManager(settings).load(path)


def test_resume_latest_uses_durable_pointer(tmp_path):
    settings=SettingsStore(tmp_path/'config'); settings.save(AppSettings(data_root=str(tmp_path/'data')))
    manager=RunManager(settings); manager.create(RunDefinition(**definition('manual','RESUME-1')))
    resumed=RunManager(SettingsStore(tmp_path/'config')).resume_latest()
    assert resumed.store.context.session_id=='RESUME-1'


def test_finish_run_is_durable_and_idempotent(tmp_path):
    settings=SettingsStore(tmp_path/'config'); settings.save(AppSettings(data_root=str(tmp_path/'data')))
    manager=RunManager(settings); loaded=manager.create(RunDefinition(**definition('manual','FINISH-1')))
    first=manager.finish(loaded); second=manager.finish(loaded)
    assert first['status']==second['status']=='finished'


def test_finished_run_rejected_for_resume(tmp_path):
    settings=SettingsStore(tmp_path/'config'); settings.save(AppSettings(data_root=str(tmp_path/'data')))
    manager=RunManager(settings); loaded=manager.create(RunDefinition(**definition('manual','FINISH-2'))); manager.finish(loaded)
    with pytest.raises(ValueError): manager.load(loaded.manifest_path)


@pytest.mark.parametrize('field,value', [('run_id','../bad'),('operator_id','A/B'),('container_id','..')])
def test_path_unsafe_identifiers_rejected(field,value):
    data=definition(); data[field]=value
    with pytest.raises(ValueError): RunDefinition(**data).validate()
