import os
import collections
import functools

from season import Season
from standings import Standings
from simulator import Simulator


class Multisimulator:
    """

    """
    def __init__(self, season, standings, simulations, experiments):
        self.season = season
        self.standings = standings
        self.simulations = simulations
        self.experiments = experiments
        self.undefeated = None

    @classmethod
    def FromJSON(cls, season_file, standings_file, simulations, experiments):
        return cls(Season.FromJSON(season_file),
                   Standings.FromJSON(standings_file),
                   simulations,
                   experiments)

    @classmethod
    def FromJSONDirectory(cls, directory, simulations, experiments):
        return cls(Season.FromJSONDirectory(directory),
                   Standings.FromJSONDirectory(directory),
                   simulations,
                   experiments)

    def Simulate(self):
        """

        :return:
        """
        undefeated = {'ANY': []}
        for i in range(self.experiments):
            simulator = Simulator(self.season, self.standings, self.simulations)
            simulator.Simulate()
            count_undefeated = collections.Counter(simulator.undefeated)
            for team in count_undefeated:
                if team in undefeated:
                    undefeated[team].append(count_undefeated[team])
                else:
                    undefeated[team] = [count_undefeated[team]]
            undefeated['ANY'].append(collections.Counter(simulator.nUndefeated)[1])
        self.undefeated = {team: sorted(undefeated[team]) for team in undefeated}

    def _PrintUndefeated(self, percentile, do_range=True):
        """

        :param percentile:
        :param do_range:
        :return:
        """
        def GetPercentile(result, p):
            percentile = result[int(len(result) * p)] * 100.0
            percentile /= self.simulations
            #return f'{percentile:.3}'
            return '{:.3}'.format(percentile)

        if self.undefeated is None:
            self.Simulate()
        for team in self.undefeated:
            result = self.undefeated[team]
            Percentile = functools.partial(GetPercentile, result)
            if do_range:
                p_min = Percentile((1.0 - percentile) / 2.0)
                p_max = Percentile((1.0 + percentile) / 2.0)
                print(f'{team:<3} [{int(100 * percentile)}%]: {p_min}% - {p_max}%')
            else:
                print(f'{team:<3} [{int(100 * percentile)}%]: {GetPercentile(percentile)}%')

    def PrintUndefeated(self):
        """

        :return:
        """
        for percentile in [0.50, 0.68, 0.95]:
            self._PrintUndefeated(percentile)
        self._PrintUndefeated(0.50, do_range=False)
