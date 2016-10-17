
class Multisimulator:
    def __init__(self, season, standings, simulations, experiments):
        self.season = season
        self.standings = standings
        self.simulations = simulations
        self.experiments = experiments

    @classmethod
    def FromJSON(cls, season_file, standings_file, simulations, experiments):
        return cls(Season.FromJSON(season_file), Standings.FromJSON(standings_file), simulations, experiments)

    # @classmethod
    # def FromSeason(cls, season, simulations, experiments):
    # 	return cls(season, simulations, experiments)

    # @classmethod
    # def FromFile(cls, f, simulations, experiments):
    # 	return cls(Season.FromFile(f), simulations, experiments)

    # @classmethod
    # def FromList(cls, data, simulations, experiments):
    # 	return cls(Season.FromList(data), simulations, experiments)

    # @classmethod
    # def FromString(cls, string, simulations, experiments):
    # 	return cls(Season.FromString(string), simulations, experiments)

    def Simulate(self):
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
        for team in self.undefeated:
            result = self.undefeated[team]
            GetPercentile = lambda p: str(100.0*result[int(len(result)*p)]/self.simulations)[0:5]
            if do_range:
                p_min = GetPercentile((1.0 - percentile) / 2.0)
                p_max = GetPercentile((1.0 + percentile) / 2.0)
                print('{} [{}%]: {}% - {}%'.format(team.ljust(3), int(100 * percentile), p_min, p_max))
            else:
                print('{} [{}%]: {}%'.format(team.ljust(3), int(100 * percentile), GetPercentile(percentile)))

    def PrintUndefeated(self):
        try:
            for percentile in [0.50, 0.68, 0.95]:
                self._PrintUndefeated(percentile)
            self._PrintUndefeated(0.50, do_range=False)
        except AttributeError:
            self.Simulate()
            self.PrintUndefeated()
