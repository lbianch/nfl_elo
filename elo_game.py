import logging
import math

from elo import ELO
import inv_erf

class ELOGameSimulator:
    K = 20.0

    def __init__(self, home: ELO, away: ELO):
        self.home = home
        self.away = away
        self.winner = None
        self.spread = 0

    def ELOMargin(self) -> int:
        # 65 Point advantage for home teams
        logging.debug("Game %s @ %s", self.away, self.home)
        margin = 65 + self.home.elo - self.away.elo
        logging.debug("ELO Margin = %d", margin)
        return margin

    def PointMargin(self) -> float:
        margin = self.ELOMargin() / 25.0
        logging.debug("Expected point margin = %f", margin)
        return margin

    def HomeWinProbability(self) -> float:
        exponent = -self.ELOMargin() / 400.0
        den = 1.0 + 10.0**exponent
        prob = 1.0 / den
        logging.debug("Home probability = %f", prob)
        return prob

    def AwayWinProbability(self) -> float:
        prob = 1.0 - self.HomeWinProbability()
        logging.debug("Away probability = %f", prob)
        return prob

    def Simulate(self):
        """ELO gives us the expected point margin and the probability that
        the home team (or away team) would win.  What we want is to simulate
        the point difference in the game such that the mean is the point margin
        and the probability the home team wins is what we expect.  This implies
        that the mean is given and the integral of the probability distribution
        from -infinity to 0 is also given.  Model this as a Gaussian distribution
        and use functionality from `inv_erf` to solve.
        """
        if self.winner is not None:
            logging.debug("Winner already known - %s", self.winner)
            return
        pt_margin = self.PointMargin()
        prob = self.HomeWinProbability()
        logging.debug("Point margin = %d", pt_margin)
        logging.debug("Home win probability = %f", prob)
        self.spread = inv_erf.get_spread(pt_margin, prob)
        self.winner = self.home if self.spread > 0.0 else self.away
        logging.debug("Spread = %d", self.spread)
        logging.debug("Winner = %s", self.winner.name)

    @property
    def loser(self) -> ELO:
        return {self.home.name: self.away, self.away.name: self.home}[self.winner.name]

    def UpdateTeams(self):
        if self.winner is None:
            self.Simulate()
        if self.winner == self.home:
            prob = self.HomeWinProbability()
        elif self.winner == self.away:
            prob = self.AwayWinProbability()
        else:
            raise ValueError("Winner is {s.winner} but must be one of {s.home} or {s.away}".format(s=self))
        elo_points = ELOGameSimulator.K * math.log(abs(self.spread) + 1.0)
        elo_points /= 1.0 + ((self.winner.elo - self.loser.elo) / 2200.0)
        elo_points *= 1.0 - prob
        logging.debug("Updating with points = %f * %f * (1.0 - %f) / (1.0 + %f/2200.) = %f",
                      ELOGameSimulator.K, math.log(abs(self.spread) + 1), prob,
                      self.winner.elo - self.loser.elo, elo_points)
        self.winner.UpdateWin(elo_points)
        self.loser.UpdateLoss(elo_points)


class ELOKnownGame(ELOGameSimulator):
    def __init__(self, home: ELO, away: ELO, home_score: int, away_score: int):
        super().__init__(home, away)
        self.winner = self.home if home_score > away_score else self.away
        self.spread = abs(home_score - away_score)

def GetGame(*args):
    if len(args) == 2:
        return ELOGameSimulator(*args)
    if len(args) == 4:
        return ELOKnownGame(*args)
    raise ValueError("Requires either two or four arguments")