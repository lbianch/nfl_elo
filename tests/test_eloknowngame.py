import unittest
import logging

from elo import ELO
from elo_game import ELOKnownGame

logging.basicConfig(level=logging.INFO)


class TestELOKnownGame(unittest.TestCase):

    def test_raises(self):
        game = ELOKnownGame(ELO('ATL', 1541, 6, 1), ELO('TB', 1351, 2, 4), 20, 23)
        game.winner = 'HOU'
        with self.assertRaises(AttributeError):
            game.loser  # Statement does have effect since this is a property it is a function call
        game.winner = ELO('HOU', 1450, 3, 5)
        with self.assertRaises(KeyError):
            game.loser
        with self.assertRaises(ValueError):
            game.UpdateTeams()

    def test_Week08_TBatATL(self):
        logging.info("Testing TB @ ATL Week 8 2015")
        logging.info("Favored: Home; Winner: Home")
        data = {'home': ELO('ATL', 1541, 6, 1),
                'away': ELO('TB', 1351, 2, 4),
                'winner': ELO('TB', 1376, 3, 4),
                'loser': ELO('ATL', 1516, 6, 2),
                'home_points': 20,
                'away_points': 23,
                'spread': 3,
                'home_win_min': 0.812,
                'home_win_max': 0.813,
                'away_win_min': 0.187,
                'away_win_max': 0.188,
                'elo_points': 25}
        game = self.run_game(data)
        self.assertLess(game.winner, game.loser,
                        "Expected {g.winner} to be less than {g.loser}".format(g=game))
        logging.info("Test Passed")

    def test_Week11_GBatMIN(self):
        # Home team favored and lost
        logging.info("Testing GB @ MIN Week 11 2015")
        logging.info("Favored: Home; Winner: Away")
        data = {'home': ELO('MIN', 1586, 7, 2),
                'away': ELO('GB', 1619, 6, 3),
                'winner': ELO('GB', 1650, 7, 3),
                'loser': ELO('MIN', 1555, 7, 3),
                'home_points': 13,
                'away_points': 30,
                'spread': 17,
                'home_win_min': 0.54,
                'home_win_max': 0.56,
                'away_win_min': 0.44,
                'away_win_max': 0.46,
                'elo_points': 31}
        game = self.run_game(data)
        self.assertLess(game.loser, game.winner,
                        "Expected {g.loser} to be less than {g.winner}".format(g=game))
        logging.info("Test Passed")

    def test_Week14_SEAatBAL(self):
        # Away team favored and won
        logging.info("Testing SEA @ BAL Week 14 2015")
        logging.info("Favored: Away; Winner: Away")
        data = {'home': ELO('BAL', 1491, 4, 8),
                'away': ELO('SEA', 1676, 7, 5),
                'winner': ELO('SEA', 1697, 8, 5),
                'loser': ELO('BAL', 1470, 4, 9),
                'home_points': 6,
                'away_points': 35,
                'spread': 29,
                'home_win_min': 0.332,
                'home_win_max': 0.334,
                'away_win_min': 0.666,
                'away_win_max': 0.667,
                'elo_points': 21}
        game = self.run_game(data)
        self.assertLess(game.loser, game.winner,
                        "Expected {g.loser} to be less than {g.winner}".format(g=game))
        logging.info("Test Passed")

    def test_Week17_NEatMIA(self):
        # Away team favored but lost
        logging.info("Testing NE @ MIA Week 17 2015")
        logging.info("Favored: Away; Winner: Home")
        data = {'home': ELO('MIA', 1361, 5, 10),
                'away': ELO('NE', 1689, 12, 3),
                'winner': ELO('MIA', 1407, 6, 10),
                'loser': ELO('NE', 1643, 12, 4),
                'home_points': 20,
                'away_points': 10,
                'spread': 10,
                'home_win_min': 0.180,
                'home_win_max': 0.181,
                'away_win_min': 0.819,
                'away_win_max': 0.820,
                'elo_points': 46}
        game = self.run_game(data)
        self.assertLess(game.winner, game.loser,
                        "Expected {g.winner} to be less than {g.loser}".format(g=game))
        logging.info("Test Passed")

    def run_game(self, data):
        g = ELOKnownGame(data['home'], data['away'], data['home_points'], data['away_points'])
        self.assertEqual(g.winner.name, data['winner'].name,
                         "Expected winner to be {} but found {}".format(data['winner'].name, g.winner.name))
        self.assertEqual(g.loser.name, data['loser'].name,
                         "Expected loser to be {} but fond {}".format(data['loser'].name, g.loser.name))
        self.assertEqual(g.spread, data['spread'],
                         "Expected spread of {}, found {}".format(data['spread'], g.spread))
        self.assertEqual(g.HomeWinProbability() + g.AwayWinProbability(), 1.0,
                         "Expected probabilities sum to 1.0, found {} and {}".format(g.HomeWinProbability(),
                                                                                     g.AwayWinProbability()))
        self.assertLess(data['home_win_min'], g.HomeWinProbability(),
                        "Expected p >= {}, found {}".format(data['home_win_min'], g.HomeWinProbability()))
        self.assertLess(g.HomeWinProbability(), data['home_win_max'],
                        "Expected p < {}, found {}".format(data['home_win_max'], g.HomeWinProbability()))
        self.assertLess(data['away_win_min'], g.AwayWinProbability(),
                        "Expected p >= {}, found {}".format(data['away_win_min'], g.AwayWinProbability()))
        self.assertLess(g.AwayWinProbability(), data['away_win_max'],
                        "Expected p < {}, found {}".format(data['away_win_max'], g.AwayWinProbability()))
        start_elo = g.home.elo
        g.UpdateTeams()
        elo_points = abs(g.home.elo - start_elo)
        self.assertEqual(elo_points, data['elo_points'],
                         "Expected {} found {}".format(data['elo_points'], elo_points))
        self.assertEqual(g.winner.elo + g.loser.elo, data['home'].elo + data['away'].elo,
                         "Expected points to sum to {} but found {} + {} = {}".format(
                             data['home'].elo + data['away'].elo,
                             g.winner.elo, g.loser.elo,
                             g.winner.elo + g.loser.elo))
        self.assertEqual(g.winner.elo, data['winner'].elo,
                         "Expected winner to have ELO {} but found {}".format(data['winner'].elo, g.winner.elo))
        self.assertEqual(g.loser.elo, data['loser'].elo,
                         "Expected loser to have ELO {} but found {}".format(data['loser'].elo, g.loser.elo))
        self.assertEqual(g.winner.wins, data['winner'].wins,
                         "Expected winner to have {} wins but found {}".format(data['winner'].wins, g.winner.wins))
        self.assertEqual(g.winner.losses, data['winner'].losses,
                         "Expected winner to have {} losses but found {}".format(data['winner'].losses, g.winner.losses))
        self.assertEqual(g.loser.wins, data['loser'].wins,
                         "Expected loser to have {} wins but found {}".format(data['loser'].wins, g.loser.wins))
        self.assertEqual(g.loser.losses, data['loser'].losses,
                         "Expected loser to have {} losses but found {}".format(data['loser'].losses, g.loser.losses))
        return g


if __name__ == '__main__':
    unittest.main()