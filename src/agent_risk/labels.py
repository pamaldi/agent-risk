"""Tassonomie del task, come definite dalla scheda del dataset."""

LEVELS = (1, 2, 3, 4, 5)  # Minimal, Low, Moderate, High, Critical

NO_HARM = "No Material Harm"
NO_RISK = "No Material Risk"

DOMAINS = (
    "Physical / Health",
    "Privacy / Confidentiality",
    "Security / System Integrity",
    "Financial / Assets",
    "Operational / Service",
    "Legal / Compliance",
    "Information Quality",
    "Reputational / Social / Psychological",
    "Discrimination / Fairness",
    "Environmental",
    NO_HARM,
)

DRIVERS = (
    "Risky Requested Outcome",
    "Untrusted / Conflicting Instructions",
    "Authorization / Consent Failure",
    "Insufficient Grounding / Uncertainty",
    "Scope / Safeguard Failure",
    "Execution / Action Hazard",
    NO_RISK,
)

INTERVENTIONS = (
    "Proceed",
    "Seek Information",
    "Request Human Approval",
    "Propose Alternative",
    "Abstain / Block",
)

STEP_TYPES = ("USER", "THOUGHT", "ACTION", "OBSERVATION")


def is_consistent(level: int, domains: list[str], drivers: list[str]) -> bool:
    """Vincolo congiunto della classe "senza rischio".

    Nei 711 esempi pubblicati No Material Harm compare se e solo se compare No Material Risk, sempre da
    sole e sempre a livello 1 (il contrario non vale: 4 esempi di livello 1 hanno un danno).
    """
    no_harm, no_risk = domains == [NO_HARM], drivers == [NO_RISK]
    if no_harm or no_risk:
        return no_harm and no_risk and level == 1
    return (
        NO_HARM not in domains
        and NO_RISK not in drivers
        and 1 <= len(domains) <= 2
        and 1 <= len(drivers) <= 2
    )
