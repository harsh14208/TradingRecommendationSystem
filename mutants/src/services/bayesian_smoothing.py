import math


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_calculate_predictive_interval__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_calculate_predictive_interval__mutmut)
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


def x_calculate_predictive_interval__mutmut_orig(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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


def x_calculate_predictive_interval__mutmut_1(wins: int, total: int, current_vix: float, avg_vix: float = 21.0):
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


def x_calculate_predictive_interval__mutmut_2(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = None

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


def x_calculate_predictive_interval__mutmut_3(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(None, current_vix / avg_vix)

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


def x_calculate_predictive_interval__mutmut_4(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(1.0, None)

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


def x_calculate_predictive_interval__mutmut_5(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(current_vix / avg_vix)

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


def x_calculate_predictive_interval__mutmut_6(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(1.0, )

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


def x_calculate_predictive_interval__mutmut_7(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(2.0, current_vix / avg_vix)

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


def x_calculate_predictive_interval__mutmut_8(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(1.0, current_vix * avg_vix)

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


def x_calculate_predictive_interval__mutmut_9(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(1.0, current_vix / avg_vix)

    # Apply scaled smoothing (Alpha and Beta priors)
    alpha = None
    beta = 1.0 * volatility_factor

    smoothed_probability = (wins + alpha) / (total + alpha + beta)

    # Calculate variance for confidence intervals
    # Variance of Beta distribution: (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
    alpha_post = wins + alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_10(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(1.0, current_vix / avg_vix)

    # Apply scaled smoothing (Alpha and Beta priors)
    alpha = 1.0 / volatility_factor
    beta = 1.0 * volatility_factor

    smoothed_probability = (wins + alpha) / (total + alpha + beta)

    # Calculate variance for confidence intervals
    # Variance of Beta distribution: (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
    alpha_post = wins + alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_11(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(1.0, current_vix / avg_vix)

    # Apply scaled smoothing (Alpha and Beta priors)
    alpha = 2.0 * volatility_factor
    beta = 1.0 * volatility_factor

    smoothed_probability = (wins + alpha) / (total + alpha + beta)

    # Calculate variance for confidence intervals
    # Variance of Beta distribution: (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
    alpha_post = wins + alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_12(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(1.0, current_vix / avg_vix)

    # Apply scaled smoothing (Alpha and Beta priors)
    alpha = 1.0 * volatility_factor
    beta = None

    smoothed_probability = (wins + alpha) / (total + alpha + beta)

    # Calculate variance for confidence intervals
    # Variance of Beta distribution: (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
    alpha_post = wins + alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_13(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(1.0, current_vix / avg_vix)

    # Apply scaled smoothing (Alpha and Beta priors)
    alpha = 1.0 * volatility_factor
    beta = 1.0 / volatility_factor

    smoothed_probability = (wins + alpha) / (total + alpha + beta)

    # Calculate variance for confidence intervals
    # Variance of Beta distribution: (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
    alpha_post = wins + alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_14(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
    """
    Calculates a volatility-scaled Bayesian probability of success.
    In high volatility, the prior weight increases (widening the confidence interval).
    """
    # Baseline Laplace smoothing uses +1 / +2
    # We scale this based on how elevated VIX is compared to its historical average
    volatility_factor = max(1.0, current_vix / avg_vix)

    # Apply scaled smoothing (Alpha and Beta priors)
    alpha = 1.0 * volatility_factor
    beta = 2.0 * volatility_factor

    smoothed_probability = (wins + alpha) / (total + alpha + beta)

    # Calculate variance for confidence intervals
    # Variance of Beta distribution: (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
    alpha_post = wins + alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_15(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    smoothed_probability = None

    # Calculate variance for confidence intervals
    # Variance of Beta distribution: (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
    alpha_post = wins + alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_16(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    smoothed_probability = (wins + alpha) * (total + alpha + beta)

    # Calculate variance for confidence intervals
    # Variance of Beta distribution: (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
    alpha_post = wins + alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_17(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    smoothed_probability = (wins - alpha) / (total + alpha + beta)

    # Calculate variance for confidence intervals
    # Variance of Beta distribution: (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
    alpha_post = wins + alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_18(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    smoothed_probability = (wins + alpha) / (total + alpha - beta)

    # Calculate variance for confidence intervals
    # Variance of Beta distribution: (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
    alpha_post = wins + alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_19(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    smoothed_probability = (wins + alpha) / (total - alpha + beta)

    # Calculate variance for confidence intervals
    # Variance of Beta distribution: (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
    alpha_post = wins + alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_20(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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
    alpha_post = None
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_21(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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
    alpha_post = wins - alpha
    beta_post = (total - wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_22(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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
    beta_post = None

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_23(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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
    beta_post = (total - wins) - beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_24(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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
    beta_post = (total + wins) + beta

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_25(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    variance = None
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_26(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    variance = (alpha_post * beta_post) * ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_27(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    variance = (alpha_post / beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_28(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 / (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_29(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) * 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_30(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    variance = (alpha_post * beta_post) / ((alpha_post - beta_post) ** 2 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_31(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 3 * (alpha_post + beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_32(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post - 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_33(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post - beta_post + 1))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_34(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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

    variance = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 2))
    std_dev = math.sqrt(variance)

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_35(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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
    std_dev = None

    return smoothed_probability, std_dev


def x_calculate_predictive_interval__mutmut_36(wins: int, total: int, current_vix: float, avg_vix: float = 20.0):
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
    std_dev = math.sqrt(None)

    return smoothed_probability, std_dev

mutants_x_calculate_predictive_interval__mutmut['_mutmut_orig'] = x_calculate_predictive_interval__mutmut_orig # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_1'] = x_calculate_predictive_interval__mutmut_1 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_2'] = x_calculate_predictive_interval__mutmut_2 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_3'] = x_calculate_predictive_interval__mutmut_3 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_4'] = x_calculate_predictive_interval__mutmut_4 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_5'] = x_calculate_predictive_interval__mutmut_5 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_6'] = x_calculate_predictive_interval__mutmut_6 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_7'] = x_calculate_predictive_interval__mutmut_7 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_8'] = x_calculate_predictive_interval__mutmut_8 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_9'] = x_calculate_predictive_interval__mutmut_9 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_10'] = x_calculate_predictive_interval__mutmut_10 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_11'] = x_calculate_predictive_interval__mutmut_11 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_12'] = x_calculate_predictive_interval__mutmut_12 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_13'] = x_calculate_predictive_interval__mutmut_13 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_14'] = x_calculate_predictive_interval__mutmut_14 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_15'] = x_calculate_predictive_interval__mutmut_15 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_16'] = x_calculate_predictive_interval__mutmut_16 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_17'] = x_calculate_predictive_interval__mutmut_17 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_18'] = x_calculate_predictive_interval__mutmut_18 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_19'] = x_calculate_predictive_interval__mutmut_19 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_20'] = x_calculate_predictive_interval__mutmut_20 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_21'] = x_calculate_predictive_interval__mutmut_21 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_22'] = x_calculate_predictive_interval__mutmut_22 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_23'] = x_calculate_predictive_interval__mutmut_23 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_24'] = x_calculate_predictive_interval__mutmut_24 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_25'] = x_calculate_predictive_interval__mutmut_25 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_26'] = x_calculate_predictive_interval__mutmut_26 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_27'] = x_calculate_predictive_interval__mutmut_27 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_28'] = x_calculate_predictive_interval__mutmut_28 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_29'] = x_calculate_predictive_interval__mutmut_29 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_30'] = x_calculate_predictive_interval__mutmut_30 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_31'] = x_calculate_predictive_interval__mutmut_31 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_32'] = x_calculate_predictive_interval__mutmut_32 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_33'] = x_calculate_predictive_interval__mutmut_33 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_34'] = x_calculate_predictive_interval__mutmut_34 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_35'] = x_calculate_predictive_interval__mutmut_35 # type: ignore # mutmut generated
mutants_x_calculate_predictive_interval__mutmut['x_calculate_predictive_interval__mutmut_36'] = x_calculate_predictive_interval__mutmut_36 # type: ignore # mutmut generated
