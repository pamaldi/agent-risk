"""Test offline del modulo llm: nessuna chiamata all'API."""
import importlib.util
from pathlib import Path

import pytest

from agent_risk import data, llm
from agent_risk.labels import DOMAINS, DRIVERS

needs_data = pytest.mark.skipif(
    not (data.RAW / "data" / "train.jsonl").exists(), reason="dati non scaricati: scripts/download_data.py"
)


def _script():
    path = Path(__file__).resolve().parents[1] / "scripts" / "llm_zero_shot.py"
    spec = importlib.util.spec_from_file_location("llm_zero_shot", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_schema_uses_official_labels():
    props = llm.SCHEMA["properties"]
    assert props["risk_domains"]["items"]["enum"] == list(DOMAINS)
    assert props["risk_drivers"]["items"]["enum"] == list(DRIVERS)
    assert props["risk_severity"]["enum"] == [1, 2, 3, 4, 5]
    assert all(d in llm.SYSTEM for d in DOMAINS + DRIVERS)


def test_normalize_dedupes_and_caps_at_two():
    level, dom, drv = llm.normalize(
        {"risk_severity": 3, "risk_domains": ["A", "A", "B", "C"], "risk_drivers": ["X"]}
    )
    assert (level, dom, drv) == (3, ["A", "B"], ["X"])


def test_cost():
    assert llm.cost(1_000_000, 1_000_000) == llm.PRICE_IN + llm.PRICE_OUT


@needs_data
def test_sample_is_deterministic_one_per_group():
    s = _script().sample("train", 100, 42)
    assert len(s) == 100
    assert s["scenario_group"].is_unique
    assert s["example_id"].tolist() == _script().sample("train", 100, 42)["example_id"].tolist()
