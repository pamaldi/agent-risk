"""Esegue un programma clingo su fatti (livello, domini, fattori) e restituisce l'intervento."""
from __future__ import annotations

from pathlib import Path

import clingo

ASP_DIR = Path(__file__).parent
POLICY_EXAMPLE = ASP_DIR / "policy_example.lp"


def _q(s: str) -> str:
    return '"' + s.replace('"', '\\"') + '"'


def intervention_asp(
    level: int, domains: list[str], drivers: list[str], program: Path = POLICY_EXAMPLE
) -> tuple[str, list[str]]:
    """Restituisce (intervento, regole scattate)."""
    facts = [f"level({level})."]
    facts += [f"domain({_q(d)})." for d in domains]
    facts += [f"driver({_q(f)})." for f in drivers]
    ctl = clingo.Control(["--warn=none"])
    ctl.load(str(program))
    ctl.add("base", [], "\n".join(facts))
    ctl.ground([("base", [])])
    atoms: list[clingo.Symbol] = []
    ctl.solve(on_model=lambda m: atoms.extend(m.symbols(shown=True)))
    chosen = [a for a in atoms if a.name == "intervention"]
    rules = [a.arguments[1].name for a in atoms if a.name == "fires"]
    return chosen[0].arguments[0].string, rules
