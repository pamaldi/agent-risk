"""Metriche ufficiali dei subtask 1, 2a, 2b (MAE e Jaccard medio) e F1 per il subtask 3."""
from __future__ import annotations

from collections.abc import Sequence

from sklearn.metrics import f1_score


def mae(gold: Sequence[int], pred: Sequence[float]) -> float:
    return sum(abs(g - p) for g, p in zip(gold, pred, strict=True)) / len(gold)


def jaccard(gold: Sequence[Sequence[str]], pred: Sequence[Sequence[str]]) -> float:
    total = 0.0
    for g, p in zip(gold, pred, strict=True):
        g, p = set(g), set(p)
        total += len(g & p) / len(g | p)
    return total / len(gold)


def intervention_f1(gold: Sequence[str], pred: Sequence[str], average: str = "macro") -> float:
    """Il sito non dice se l'F1 sia macro o pesato: domanda aperta da fare sul Discord del task."""
    return f1_score(gold, pred, average=average, zero_division=0)
