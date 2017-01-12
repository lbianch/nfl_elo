import os
import copy
import collections

from season import Season
from standings import Standings
from season_simulator import SeasonSimulator

class Simulator:
    """

    """
    def __init__(self, season: Season, standings: Standings, simulations: int):
        self.undefeated = []
        self.nUndefeated = []
        self.season = season
        self.standings = standings
        self.simulations = simulations

    @classmethod
    def FromJSONDirectory(cls, directory: str, simulations: int):
        season = os.path.join(directory, 'schedule.json')
        standings = os.path.join(directory, 'elo_start.json')
        return cls(Season.FromJSON(season), Standings.FromJSON(standings), simulations)

    def Simulate(self, simulations=None):
        """

        :param simulations:
        :return:
        """
        if simulations:
            self.simulations = simulations
        for i in range(self.simulations):
            simulation = SeasonSimulator(self.season, copy.deepcopy(self.standings))
            simulation.SimulateSeason()
            standings = simulation.standings
            self.undefeated += standings.GetUndefeated()
            self.nUndefeated += range(1, standings.GetNumberUndefeated() + 1)

    def GetPercent(self, value):
        """

        :param value:
        :return:
        """
        if 0.0 <= value <= self.simulations:
            return 100.0 * value / self.simulations
        raise ValueError("Expected value in [0,{}], received {}".format(self.simulations, value))

    def PrintUndefeated(self):
        """

        :return:
        """
        undefeated = collections.Counter(self.undefeated)
        nUndefeated = collections.Counter(self.nUndefeated)
        for team in undefeated:
            print('{} {}%'.format(team, self.GetPercent(undefeated[team])))
        for n in nUndefeated:
            print('Probability of >= {} undefeated teams: {}%'.format(n, self.GetPercent(nUndefeated[n])))

