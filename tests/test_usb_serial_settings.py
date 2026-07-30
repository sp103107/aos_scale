"""USB serial settings regressions for selectable 115200/9600 baud."""

from __future__ import annotations

import pytest

from best_buds_weight_station.settings import ALLOWED_BAUD_RATES, AppSettings, SettingsStore


def test_default_baud_is_115200():
    settings = AppSettings(updated_at="2026-07-29T00:00:00Z")
    settings.validate()
    assert settings.baud_rate == 115200
    assert 115200 in ALLOWED_BAUD_RATES
    assert 9600 in ALLOWED_BAUD_RATES


def test_allowed_baud_rates_accepted(tmp_path):
    store = SettingsStore(tmp_path / "config")
    for baud in (115200, 9600):
        saved = store.save(AppSettings(data_root=str(tmp_path / "data"), baud_rate=baud))
        assert saved.baud_rate == baud
        loaded = store.load()
        assert loaded.baud_rate == baud


def test_unsupported_baud_rate_rejected():
    settings = AppSettings(baud_rate=57600, updated_at="2026-07-29T00:00:00Z")
    with pytest.raises(ValueError, match="baud"):
        settings.validate()


def test_persisted_port_and_baud_restore(tmp_path):
    store = SettingsStore(tmp_path / "config")
    store.save(
        AppSettings(
            data_root=str(tmp_path / "data"),
            serial_port="COM5",
            baud_rate=115200,
        )
    )
    loaded = store.load()
    assert loaded.serial_port == "COM5"
    assert loaded.baud_rate == 115200
