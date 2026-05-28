import math


def calculate_predictive_interval(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(1.0, current_vix / avg_vix)

    # Apply scaled smoothing (Alpha and Beta priors)
    alpha = 1.0 * volatility_factor
    beta = 1.0 * volatility_factor

    smoothed_probability = (wins + alpha) / (total + alpha + beta)

    # Calculate variance for confidence intervals
    # Variance of Beta distribution: (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
    alpha_post = wins + alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev
