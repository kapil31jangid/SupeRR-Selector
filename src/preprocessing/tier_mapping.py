"""
Competition Tier Classification and Strength Multipliers
"""

from typing import Dict

COMPETITION_TIERS: Dict[str, str] = {
    # Tier 1: Premier Franchise Benchmark
    "Indian Premier League": "T1",
    "IPL": "T1",

    # Tier 2: Major Full-Member Franchise & International T20
    "Big Bash League": "T2",
    "BBL": "T2",
    "Pakistan Super League": "T2",
    "PSL": "T2",
    "SA20": "T2",
    "The Hundred": "T2",
    "International T20": "T2",
    "T20I": "T2",

    # Tier 3: Emerging Commercial Leagues
    "Caribbean Premier League": "T3",
    "CPL": "T3",
    "Bangladesh Premier League": "T3",
    "BPL": "T3",
    "Lanka Premier League": "T3",
    "LPL": "T3",
    "Super Smash": "T3",

    # Tier 4: Associate T20Is
    "ICC Men's T20 World Cup Qualifier": "T4",
    "Associate T20I": "T4",

    # Tier 5: Domestic T20 Tournaments
    "Syed Mushtaq Ali Trophy": "T5",
    "SMAT": "T5",
    "Vitality Blast": "T5",
    "National T20 Cup": "T5"
}

TIER_MULTIPLIERS: Dict[str, float] = {
    "T1": 1.00,
    "T2": 0.92,
    "T3": 0.84,
    "T4": 0.76,
    "T5": 0.68
}


def get_competition_tier(competition_name: str) -> str:
    """Return competition tier (T1 to T5), default T3."""
    return COMPETITION_TIERS.get(competition_name.strip(), "T3")


def get_tier_multiplier(tier_code: str) -> float:
    """Return strength factor for tier code."""
    return TIER_MULTIPLIERS.get(tier_code.strip().upper(), 0.84)
