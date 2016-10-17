from season import Season
from standings import Standings
import elo_game


class SeasonSimulator:
    def __init__(self, season: Season, standings: Standings):
        self.season = season
        self.standings = standings

    @classmethod
    def FromJSON(cls, season_file, standings_file):
        return cls(Season.FromJSON(season_file), Standings.FromJSON(standings_file))

    @classmethod
    def FromFile(cls, season_f, standings_f):
        return cls(Season.FromFile(season_f), Standings.FromFile(standings_f))

    @classmethod
    def FromString(cls, season_str, standings_str):
        return cls(Season.FromString(season_str), Standings.FromString(standings_str))

    @classmethod
    def FromList(cls, season_data, standings_data):
        return cls(Season.FromList(season_data), Standings.FromDict(standings_data))

    def VerifySimulation(self):
        assert len(self.standings) == 32
        totalWins = sum(team.wins for team in self.standings.values())
        totalLosses = sum(team.losses for team in self.standings.values())
        assert totalWins == totalLosses == 16 * 16
        for team in self.standings.values():
            assert team.wins >= 0
            assert team.losses >= 0
            assert team.wins + team.losses == 16

    def SimulateGame(self, game):
        simulator = elo_game.GetGame(*game)
        simulator.Simulate()
        simulator.UpdateTeams()

    def SimulateWeek(self, week):
        for game in week:
            self.SimulateGame(game)

    def SimulateSeason(self):
        for week in self.season:
            self.SimulateWeek(week)
        self.VerifySimulation()
