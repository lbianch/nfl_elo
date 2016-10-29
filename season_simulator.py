import os

from elo_game import GetGame
from season import Season
from standings import Standings


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
        totalWins = sum(map(lambda t: t.wins, self.standings.values()))
        totalLosses = sum(map(lambda t: t.losses, self.standings.values()))
        totalTies = sum(map(lambda t: t.ties, self.standings.values()))
        assert totalWins == totalLosses, '{} Wins, {} Losses'.format(totalWins, totalLosses)
        assert totalWins + totalLosses + totalTies == 16 * 32, \
            '{} Wins, {} Losses, {} Ties'.format(totalWins, totalLosses, totalTies)
        for team in self.standings.values():
            assert team.wins >= 0, team
            assert team.losses >= 0, team
            assert team.ties >= 0, team
            assert team.wins + team.losses + team.ties == 16, team

    def SimulateGame(self, game):
        home, away = map(lambda k: self.standings[k], game[0:2])
        simulator = GetGame(home, away, *game[2:])
        simulator.Simulate()
        simulator.UpdateTeams()

    def SimulateWeek(self, week):
        for game in week:
            self.SimulateGame(game)

    def SimulateSeason(self):
        for week in self.season:
            self.SimulateWeek(week)
        self.VerifySimulation()
