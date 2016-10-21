import unittest
import logging
import pickle

import inv_erf

logging.basicConfig(level=logging.INFO)


def prob(mu: float) -> float:
    return 1.0 / (1.0 + 10.0**(-mu / 16.0))


class TestInvErf(unittest.TestCase):
    def setUp(self):
        with open('random_state.pickle', 'rb') as f:
            state = pickle.load(f)
        inv_erf.random.setstate(state)

    def test_sign(self):
        self.assertEqual(inv_erf.sign(2.1), 1.0)
        self.assertEqual(inv_erf.sign(-4.5), -1.0)
        with self.assertRaises(TypeError):
            inv_erf.sign('test')

    def test_inv_erf(self):
        self.assertEqual(inv_erf.inv_erf(0.0), 0.0)
        with self.assertRaises(ValueError):
            inv_erf.inv_erf(1.5)
        with self.assertRaises(ValueError):
            inv_erf.inv_erf(-1.5)
        with self.assertRaises(TypeError):
            inv_erf.inv_erf('0.0')
        from math import erf
        for x in [0.1, 0.25, 0.4, 0.6, 0.75, 0.9]:
            self.assertAlmostEqual(inv_erf.inv_erf(erf(x)), x, 3)

    def test_get_sigma(self):
        with self.assertRaises(ValueError):
            inv_erf.get_sigma(13.0, 1.2)
        with self.assertRaises(ValueError):
            inv_erf.get_sigma(-3.0, -0.2)
        for pts in [3, 7, 13, 21, 45]:
            self.assertGreater(prob(pts), 0.5)
            self.assertGreater(inv_erf.get_sigma(pts, prob(pts)), 11.08)
            self.assertLess(prob(-pts), 0.5)
            # Sigma is always positive
            self.assertGreater(inv_erf.get_sigma(-pts, prob(-pts)), 11.08)

    def test_spread(self):
        # Seed was fixed in `setUp`, exploit it:
        self.assertEqual(inv_erf.get_spread(10.0, prob(10.0)), 16)
        # Now try to aggregate using known random values
        N = 10000
        pt = 14.0
        random_data = [inv_erf.get_spread(pt, prob(pt)) for _ in range(N)]
        self.assertEqual(sum(random_data), 143046)
        # Now try to aggregate using unknown random values
        inv_erf.random.seed()
        random_data = sum(inv_erf.get_spread(pt, prob(pt)) for _ in range(N))
        self.assertGreater(random_data, (pt - 0.5) * N)
        self.assertLess(random_data, (pt + 0.5) * N)
        # Test using known-value for `sigma`; sigma = 0.0 is non-random
        self.assertEqual(inv_erf.get_spread(8.0, prob(8.0), 0.0), 8)
        with self.assertRaises(TypeError):
            inv_erf.get_spread('test', 0.75)
        with self.assertRaises(TypeError):
            inv_erf.get_spread(3.4, 'test')
        with self.assertRaises(TypeError):
            inv_erf.get_spread(3.4, 0.6, 'test')

if __name__ == '__main__':
    unittest.main()
