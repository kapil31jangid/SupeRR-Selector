"""
Match State and Game Situation Reconstruction Module
"""

import pandas as pd
import numpy as np


def classify_delivery_phase(over_num: int) -> str:
    """
    Classify delivery by formal match phase:
    - Powerplay: Overs 0 to 5 (Balls 0.1 to 5.6)
    - Middle: Overs 6 to 15 (Balls 6.1 to 15.6)
    - Death: Overs 16 to 19 (Balls 16.1 to 19.6)
    """
    if over_num < 6:
        return 'powerplay'
    elif over_num < 16:
        return 'middle'
    else:
        return 'death'


def is_high_extreme_pressure(
    inning: int,
    over_num: int,
    required_run_rate: float,
    wickets_down: int
) -> bool:
    """
    Identify High-Extreme Pressure situations based on win probability differential:
    - 2nd Innings (Chase): Overs 15-19 with RRR >= 10.0 or wickets >= 5
    - 1st Innings: Overs 16-19 with wickets >= 4 (finishing under collapse pressure)
    """
    if inning == 2:
        if over_num >= 15 and (required_run_rate >= 10.0 or wickets_down >= 5):
            return True
    elif inning == 1:
        if over_num >= 16 and wickets_down >= 4:
            return True
    return False
