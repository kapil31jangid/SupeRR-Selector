"""
Rajasthan Royals Talent Scouting Model (40/30/20/10)
===================================================
Translates historical pressure performance and talent runway metrics into 
Rajasthan Royals long-term auction scouting priority scores.

Scouting Dimensions:
- 40%: Validated Historical Pressure Performance (or Evidence-Qualified Bowling Score)
- 30%: Age & Career Development Potential (Calculated as of 1 April 2027)
- 20%: Skill Ceiling & Tactical Squad Role Fit
- 10%: Recent Match Form & Competitive Trajectory (2025-2026 Season Cycle)

Formula:
RR_Score = 0.40 * DimA + 0.30 * DimB + 0.20 * DimC + 0.10 * DimD
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import datetime
import pandas as pd
import numpy as np


@dataclass
class ScoutingWeights:
    DIM_A_PRESSURE: float = 0.40
    DIM_B_AGE_DEV: float = 0.30
    DIM_C_SKILL_CEILING: float = 0.20
    DIM_D_CURRENT_FORM: float = 0.10


class RRScoutingModel:
    """
    Rajasthan Royals Long-Term Talent Identification and Auction Scouting Engine.
    """

    REFERENCE_DATE = datetime.date(2027, 4, 1)

    # Standardized Age & Runway scoring thresholds
    AGE_BENCHMARKS = {
        'emerging': (23, 100.0, "Emerging (<=23 yrs): 8-10+ year franchise development runway"),
        'young_dev': (26, 85.0, "Young Development Candidate (24-26 yrs): 6-8 year prime runway"),
        'prime_age': (30, 65.0, "Prime-Age Performer (27-30 yrs): 3-5 year peak performance window"),
        'experienced': (100, 50.0, "Experienced Tactical Asset (31+ yrs): Immediate 1-2 year impact")
    }

    def __init__(self, weights: Optional[ScoutingWeights] = None):
        self.weights = weights or ScoutingWeights()

    @classmethod
    def calculate_age(cls, dob_str: str) -> int:
        """Calculate exact integer age as of reference date 1 April 2027."""
        parts = [int(p) for p in str(dob_str).split('-')]
        dob = datetime.date(parts[0], parts[1], parts[2])
        age = cls.REFERENCE_DATE.year - dob.year
        if (cls.REFERENCE_DATE.month, cls.REFERENCE_DATE.day) < (dob.month, dob.day):
            age -= 1
        return age

    @classmethod
    def categorize_career_stage(cls, age: int) -> str:
        """Classify candidate into standard career development bucket."""
        if age <= 23:
            return "Emerging"
        elif age <= 26:
            return "Young development candidate"
        elif age <= 30:
            return "Prime-age performer"
        else:
            return "Experienced performer"

    def calculate_composite_scouting_score(
        self,
        dim_a_pressure: float,
        dim_b_age_dev: float,
        dim_c_ceiling: float,
        dim_d_form: float
    ) -> float:
        """
        Compute unrounded composite scouting score using 40/30/20/10 weighting.
        """
        score = (
            self.weights.DIM_A_PRESSURE * float(dim_a_pressure) +
            self.weights.DIM_B_AGE_DEV * float(dim_b_age_dev) +
            self.weights.DIM_C_SKILL_CEILING * float(dim_c_ceiling) +
            self.weights.DIM_D_CURRENT_FORM * float(dim_d_form)
        )
        return score

    def evaluate_candidate(self, candidate_data: Dict) -> Dict:
        """
        Evaluate a single player dictionary and return calculated metrics.
        """
        age = self.calculate_age(candidate_data['dob'])
        category = self.categorize_career_stage(age)

        dim_a = candidate_data.get('hist_pressure_score', candidate_data.get('eq_bowling_score', 50.0))
        dim_b = candidate_data.get('dev_potential_score', 50.0)
        dim_c = candidate_data.get('composite_skill_ceiling', 50.0)
        dim_d = candidate_data.get('form_score', 50.0)

        unrounded = self.calculate_composite_scouting_score(dim_a, dim_b, dim_c, dim_d)
        rounded = round(unrounded, 2)

        return {
            'player_id': candidate_data['player_id'],
            'player_name': candidate_data['player_name'],
            'role': candidate_data['role'],
            'country': candidate_data['country'],
            'nationality': candidate_data['nationality'],
            'age_as_of_2027_04_01': age,
            'development_category': category,
            'dimA_pressure': dim_a,
            'dimB_age_dev': dim_b,
            'dimC_skill_ceiling': dim_c,
            'dimD_current_form': dim_d,
            'unrounded_scouting_score': unrounded,
            'verified_rr_scouting_score': rounded,
            'eligibility_status': candidate_data.get('eligibility_status', 'ELIGIBLE')
        }
