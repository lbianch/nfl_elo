from season import Season
from standings import Standings

class Simulator:
    def __init__(self, season: Season, standings: Standings, simulations: int):
        self.undefeated = []
        self.nUndefeated = []
        self.season = season
        self.standings = standings
        self.simulations = simulations

    @classmethod
    def FromJSON(cls, season_file, elo_file, simulations):
        return cls(Season.FromJSON(season_file), Standings.FromJSON(elo_file), simulations)

    @classmethod
    def FromString(cls, season_str, elo_str, simulations):
        return cls(Season.FromString(season_str), Standings.FromString(elo_str), simulations)

    @classmethod
    def FromFile(cls, season_f, elo_f, simulations):
        return cls(Season.FromFile(season_f), Standings.FromFile(elo_f), simulations)

    @classmethod
    def FromList(cls, season_data, standings_data, simulations):
        return cls(Season.FromList(season_data), Standings.FromDict(standings_data), simulations)

    def Simulate(self, simulations=None):
        if simulations:
            self.simulations = simulations
        for i in range(self.simulations):
            simulation = SeasonSimulator(self.season, copy.deepcopy(self.standings))
            simulation.SimulateSeason()
            simulation.VerifySimulation()
            standings = simulation.standings
            self.undefeated += standings.GetUndefeated()
            self.nUndefeated += range(1, standings.GetNumberUndefeated() + 1)

    def GetPercent(self, value):
        if 0.0 <= value <= self.simulations:
            return 100.0 * value / self.simulations
        raise ValueError("Expected value in [0,{}], received {}".format(self.simulations, value))

    def PrintUndefeated(self):
        undefeated = collections.Counter(self.undefeated)
        nUndefeated = collections.Counter(self.nUndefeated)
        for team in undefeated:
            print('{} {}%'.format(team, self.GetPercent(undefeated[team])))
        for n in nUndefeated:
            print('Probability of >= {} undefeated teams: {}%'.format(n, self.GetPercent(nUndefeated[n])))

