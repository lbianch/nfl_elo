from elo_game import GetGame
from season import Season
from standings import Standings


class SimulationError(Exception):
    pass


class SeasonSimulator:
    """

    """
    def __init__(self, season: Season, standings: Standings):
        self.season = season
        self.standings = standings

    @classmethod
    def FromJSON(cls, season_file, standings_file):
        return cls(Season.FromJSON(season_file), Standings.FromJSON(standings_file))

    def VerifySimulation(self):
        """

        :return:
        """
        if len(self.standings) != 32:
            raise SimulationError
        totalWins = sum(map(lambda t: t.wins, self.standings.values()))
        totalLosses = sum(map(lambda t: t.losses, self.standings.values()))
        totalTies = sum(map(lambda t: t.ties, self.standings.values()))
        if totalWins != totalLosses:
            raise SimulationError('{} Wins, {} Losses'.format(totalWins, totalLosses))
        if totalWins + totalLosses + totalTies != 16 * 32:
            raise SimulationError('{} Wins, {} Losses, {} Ties'.format(totalWins, totalLosses, totalTies))
        for team in self.standings.values():
            if team.wins < 0 or team.losses < 0 or team.ties < 0:
                raise SimulationError(team)
            if team.wins + team.losses + team.ties != 16:
                raise SimulationError(team)

    def SimulateGame(self, game):
        """

        :param game:
        :return:
        """
        home, away = map(lambda k: self.standings[k], game[0:2])
        simulator = GetGame(home, away, *game[2:])
        simulator.Simulate()
        simulator.UpdateTeams()

    def SimulateWeek(self, week):
        """

        :param week:
        :return:
        """
        for game in week:
            self.SimulateGame(game)

    def SimulateSeason(self):
        """

        :return:
        """
        for week in self.season:
            self.SimulateWeek(week)
        self.VerifySimulation()
