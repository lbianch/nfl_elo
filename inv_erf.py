import math
import random


def sign(x):
    return math.copysign(1.0, x)


def inv_erf(x):
    # See https://en.wikipedia.org/wiki/Error_function#Approximation_with_elementary_functions
    log = math.log(1.0 - x**2)
    a = 8.0 * (math.pi - 3.0) / (3.0 * math.pi * (4.0 - math.pi))
    common_term = 2.0 / (math.pi * a)
    common_term += log / 2.0
    result = math.sqrt(common_term**2 - (log / a)) - common_term
    return sign(x) * math.sqrt(result)


def get_sigma(mu, prob):  # Probability of greater than zero
    den = inv_erf(1.0 - 2.0 * prob)
    den *= math.sqrt(2.0)
    try:
        return -mu / den
    except ZeroDivisionError:
        # This is what should happen for a very small point spread
        return 11.087


def get_spread(mu, prob, sigma=None):
    sigma = sigma or get_sigma(mu, prob)
    result = None
    while not result:
        result = int(round(random.gauss(mu, sigma)))
    return result


def stats(pt_spread, n_iterations):
    prob = 1.0 / (1.0 + 10.0**(-pt_spread / 16.0))
    sigma = get_sigma(pt_spread, prob)
    print('expected probability =', prob)
    print('sigma =', sigma)
    x = map(lambda _: get_spread(pt_spread, prob, sigma), range(n_iterations))
    x = list(x)
    x.sort()
    print('min =', x[0])
    print('max =', x[-1])
    print('avg =', sum(x) / n_iterations)
    for p in [0.05, 0.16, 0.50, 0.84, 0.95]:
        print('{}% ='.format(int(100*p)), x[int(p * n_iterations)])
    print('p(s > 0) =', sum(y > 0 for y in x) / n_iterations)
