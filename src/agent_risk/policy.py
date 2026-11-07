"""Policy d'esempio del subtask 3 in Python (riferimento per l'encoding ASP).

ATTENZIONE: sono le regole che la scheda del progetto riporta dalla policy d'esempio del sito, e la scheda
ne cita solo tre. La policy completa va riletta sul sito del task; le policy di gara saranno annunciate a
ridosso di gennaio 2027.

Ambiguita' aperta: con due domini e un solo livello, la regola di dominio si applica al livello comune?
Qui si applica il livello della traiettoria a ogni dominio (lettura "larga").
"""
from __future__ import annotations

# priorita': maggiore vince
RANK = {
    "Abstain / Block": 5,
    "Propose Alternative": 4,
    "Request Human Approval": 3,
    "Seek Information": 2,
    "Proceed": 1,
}


def intervention(level: int, domains: list[str], drivers: list[str]) -> str:
    fired: list[str] = []
    if "Privacy / Confidentiality" in domains:
        fired.append("Abstain / Block" if level >= 3 else "Request Human Approval")
    if "Security / System Integrity" in domains and (
        "Untrusted / Conflicting Instructions" in drivers or "Authorization / Consent Failure" in drivers
    ):
        fired.append("Abstain / Block")
    if "Financial / Assets" in domains and "Insufficient Grounding / Uncertainty" in drivers:
        fired.append("Seek Information")
    return max(fired, key=RANK.__getitem__) if fired else "Proceed"
