import unittest
import logging

from elo import ELO
from elo_game import ELOKnownGame

logging.basicConfig(level=logging.INFO)


class TestELOKnownGame(unittest.TestCase):

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
        self.run_game(data)
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
        self.run_game(data)
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
        self.run_game(data)
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
        self.run_game(data)
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
        self.assertTrue(data['home_win_min'] < g.HomeWinProbability() < data['home_win_max'],
                        "Expected p in [{},{}], found {}".format(data['home_win_min'],
                                                                 data['home_win_max'],
                                                                 g.HomeWinProbability()))
        self.assertTrue(data['away_win_min'] < g.AwayWinProbability() < data['away_win_max'],
                        "Expected p in [{},{}], found {}".format(data['away_win_min'],
                                                                 data['away_win_max'],
                                                                 g.AwayWinProbability()))
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


if __name__ == '__main__':
    unittest.main()