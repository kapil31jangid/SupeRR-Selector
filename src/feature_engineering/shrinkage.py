"""
Bayesian Shrinkage Transformation Module
"""

import pandas as pd
import numpy as np


def apply_empirical_bayes_shrinkage(
    observed_rates: pd.Series,
    sample_sizes: pd.Series,
    prior_mean: float,
    k_factor: float = 60.0
) -> pd.Series:
    """
    Stabilizes noisy low-sample rate metrics by pulling towards global prior mean:
    lambda_i = N_i / (N_i + k_factor)
    shrunk_i = lambda_i * observed_i + (1 - lambda_i) * prior_mean
    """
    lam = sample_sizes / (sample_sizes + k_factor)
    shrunk = lam * observed_rates + (1.0 - lam) * prior_mean
    return shrunk
