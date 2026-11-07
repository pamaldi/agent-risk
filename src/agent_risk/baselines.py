"""Baseline costanti: la costante migliore sul train, valutata sul dev."""
from __future__ import annotations

import pandas as pd

from .labels import NO_HARM, NO_RISK
from .metrics import jaccard, mae


def constant_baselines(train: pd.DataFrame, dev: pd.DataFrame) -> dict[str, float]:
    best = min(range(1, 6), key=lambda c: mae(train["risk_severity"], [c] * len(train)))
    return {
        f"subtask1_mae_livello_{best}": mae(dev["risk_severity"], [best] * len(dev)),
        "subtask2a_jaccard_no_harm": jaccard(dev["risk_domains"], [[NO_HARM]] * len(dev)),
        "subtask2b_jaccard_no_risk": jaccard(dev["risk_drivers"], [[NO_RISK]] * len(dev)),
    }
