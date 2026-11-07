import pytest

from agent_risk import data
from agent_risk.asp.runner import intervention_asp
from agent_risk.baselines import constant_baselines
from agent_risk.labels import NO_HARM, NO_RISK, is_consistent
from agent_risk.metrics import jaccard, mae
from agent_risk.policy import intervention

needs_data = pytest.mark.skipif(
    not (data.RAW / "data" / "train.jsonl").exists(), reason="dati non scaricati: scripts/download_data.py"
)


def test_metrics():
    assert mae([1, 3], [2, 3]) == 0.5
    assert jaccard([["a", "b"]], [["a"]]) == 0.5


def test_parse_steps():
    s = data.parse_steps("Step 1. [USER]: ciao\nStep 2. [ACTION]: fai\ncosa")
    assert [(x.n, x.kind, x.text) for x in s] == [(1, "USER", "ciao"), (2, "ACTION", "fai\ncosa")]


@pytest.mark.parametrize(
    "level,domains,drivers",
    [
        (4, ["Privacy / Confidentiality"], ["Authorization / Consent Failure"]),
        (2, ["Privacy / Confidentiality"], ["Scope / Safeguard Failure"]),
        (3, ["Security / System Integrity"], ["Untrusted / Conflicting Instructions"]),
        (3, ["Financial / Assets"], ["Insufficient Grounding / Uncertainty"]),
        (1, [NO_HARM], [NO_RISK]),
    ],
)
def test_asp_matches_python_policy(level, domains, drivers):
    assert intervention_asp(level, domains, drivers)[0] == intervention(level, domains, drivers)


@needs_data
def test_dataset_shape_and_baselines():
    d = data.load_all()
    assert (len(d["train"]), len(d["dev"])) == (568, 143)
    assert set(d["train"].scenario_group).isdisjoint(d["dev"].scenario_group)
    b = constant_baselines(d["train"], d["dev"])
    assert round(b["subtask1_mae_livello_2"], 3) == 1.217
    assert round(b["subtask2a_jaccard_no_harm"], 3) == 0.455


@needs_data
def test_labels_respect_joint_constraint():
    d = data.load_all()
    bad = [
        r.example_id
        for df in d.values()
        for r in df.itertuples()
        if not is_consistent(r.risk_severity, list(r.risk_domains), list(r.risk_drivers))
    ]
    assert bad == []
