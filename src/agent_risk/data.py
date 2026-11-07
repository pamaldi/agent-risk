"""Caricamento di train, dev e manifest, con interazione scomposta in passi."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"

_STEP = re.compile(r"^Step (\d+)\. \[(USER|THOUGHT|ACTION|OBSERVATION)\]: ", re.M)


@dataclass(frozen=True)
class Step:
    n: int
    kind: str
    text: str


def parse_steps(interaction: str) -> list[Step]:
    """Scompone `formatted_interaction` in passi (numero, tipo, testo)."""
    marks = list(_STEP.finditer(interaction))
    steps = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(interaction)
        steps.append(Step(int(m.group(1)), m.group(2), interaction[m.end():end].strip()))
    return steps


def _jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_split(split: str, raw: Path = RAW) -> pd.DataFrame:
    """`split` in {"train", "dev"}. Aggiunge `scenario_group` e `n_steps`."""
    df = pd.DataFrame(_jsonl(raw / "data" / f"{split}.jsonl"))
    manifest = pd.DataFrame(_jsonl(raw / "metadata" / "split_manifest.jsonl"))
    df = df.merge(manifest[["example_id", "scenario_group"]], on="example_id", how="left")
    df["n_steps"] = df["formatted_interaction"].map(lambda s: len(parse_steps(s)))
    return df


def load_all(raw: Path = RAW) -> dict[str, pd.DataFrame]:
    return {s: load_split(s, raw) for s in ("train", "dev")}


def revision(raw: Path = RAW) -> str:
    """SHA della revisione Hugging Face scaricata."""
    return (raw / "REVISION.txt").read_text(encoding="utf-8").split()[1]
