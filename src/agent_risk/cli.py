"""Comando `agent-risk`: statistiche e baseline sui dati scaricati."""
from __future__ import annotations

import collections

import typer
from rich import print
from rich.table import Table

from . import data
from .baselines import constant_baselines

app = typer.Typer(help="SemEval 2027 Task 10 - AgentRisk")


@app.command()
def stats() -> None:
    """Statistiche descrittive di train e dev."""
    d = data.load_all()
    print(f"Revisione dati: {data.revision()}")
    for name, df in d.items():
        t = Table(title=f"{name}: {len(df)} esempi")
        t.add_column("misura")
        t.add_column("valore")
        t.add_row("livello", str(sorted(collections.Counter(df["risk_severity"]).items())))
        t.add_row("domini", str(collections.Counter(x for r in df["risk_domains"] for x in r).most_common()))
        t.add_row("fattori", str(collections.Counter(x for r in df["risk_drivers"] for x in r).most_common()))
        t.add_row("passi", str(sorted(collections.Counter(df["n_steps"]).items())))
        t.add_row("gruppi di scenario", str(df["scenario_group"].nunique()))
        print(t)


@app.command()
def baselines() -> None:
    """Baseline costanti sul dev (attese: MAE 1,217; Jaccard 0,455 e 0,455)."""
    d = data.load_all()
    for k, v in constant_baselines(d["train"], d["dev"]).items():
        print(f"{k}: {v:.3f}")


if __name__ == "__main__":
    app()
