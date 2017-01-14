import math
import random
from typing import Optional

import scipy.stats

import elo


def sign(x: float) -> float:
    """Returns +1.0 for positive `x` and -1.0 for negative `x`"""
    return math.copysign(1., x)


def inv_erf(x: float) -> float:
    """Function implementing the inverse error function via approximation.

    For more information, see
        https://en.wikipedia.org/wiki/Error_function#Approximation_with_elementary_functions

    Args:
        x: argument to the inverse error function, must be between -1 and 1

    Returns:
        Inverse error function evaluated at `x`

    Raises:
        ValueError: if the argument `x` is less than -1 or greater than 1

    Examples:
        >>> inv_erf(0.0)
        0.0

        >>> inv_erf(0.5) + inv_erf(-0.5)
        0.0

    """
    if abs(x) > 1.0:
        raise ValueError(f"Input argument must be between -1 and 1, found {x}")
    log = math.log(1.0 - x**2)
    a = 8.0 * (math.pi - 3.0) / (3.0 * math.pi * (4.0 - math.pi))
    common_term = 2.0 / (math.pi * a)
    common_term += log / 2.0
    result = math.sqrt(common_term**2 - (log / a)) - common_term
    return sign(x) * math.sqrt(result)


def get_sigma(mu: float, prob: float) -> float:
    """Assumes a Gaussian distribution with mean `mu` and an integral from
    zero to infinity of `prob`, calculates the parameter sigma describing
    such a Gaussian.

    Arguments:
        mu: Mean of the Gaussian distribution
        prob: Probability of the distribution producing a value greater
              than zero, or the integral from 0 to infinity

    Returns:
        Gaussian distribution parameter sigma

    """
    den = inv_erf(1.0 - 2.0 * prob)
    den *= math.sqrt(2.0)
    try:
        return -mu / den
    except ZeroDivisionError:
        # For the case where mu = 0 and prob = elo.win_probability(0) = 0.5
        # sigma ~11.087 taken via limit
        return 11.087


def get_spread(mu: float,
               prob: Optional[float]=None,
               sigma: Optional[float]=None,
               random_state: Optional[int]=None) -> int:
    """Get a random variable from a Gaussian distribution defined either by
    `mu` and `sigma` or by `mu` and `prob`.  Note the outcome is rounded so
    an exact Gaussian distribution will not be produced.

    Returning a value of 0 is suppressed since these correspond to a tie, yet
    for `mu` approximately 0 this would naively be likely.  Here, since there
    have been 5 actual tied games since 2012 (rule change) through week 11 of
    2016, this represents ~79 overtime games.  If a zero point margin is randomly
    selected, this is interpreted as entering overtime.  A tie is declared at
    a rate consistent with 5/79 games using a Beta distribution.  Non-ties are
    selected using the actual overtime results since 2012, where a FG is about
    twice as likely as a TD and a safety is rarer than a tie.  The winning team
    is chosen at random, indicated via return value sign.

    Args:
        mu: Mean of the Gaussian distribution
        prob (optional): Probability of the outcome being positive, see `get_sigma`
        sigma (optional): Standard deviation of the Gaussian distribution
        random_state (optional): Random state used by `scipy.stats.beta.rvs`

    Returns:
        Random integer corresponding to the described Gaussian distribution

    Raises:
        ValueError: If both `prob` and `sigma` are `None`

    """
    if prob is None and sigma is None:
        raise ValueError("Must provide one of `mu` or `sigma`")
    if sigma is None:
        sigma = get_sigma(mu, prob)
    result = elo.rounded_int(random.gauss(mu, sigma))
    if result != 0:
        return result
    if random.random() < scipy.stats.beta(5, 74).rvs(random_state=random_state):
        return 0
    # Overtime games have resulted in 1 SAF win, 22 FG wins, and 52 TD wins
    # Choose a random representative outcome
    return random.choice([1, -1]) * random.choice([2] + 52*[3] + 22*[6])
