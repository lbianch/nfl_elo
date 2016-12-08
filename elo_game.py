import logging
import math
from typing import Optional

import elo
import inv_erf
ELO = elo.ELO

logging.basicConfig(level=logging.DEBUG)

class ELOGameSimulator:
    """Simulates a game between two teams represented by `ELO` objects.

    Args:
        home: Home team
        away: Away team

    Attributes:
        K (float): Class attribute controlling the scaling of ELO point exchange
        home: Home team
        away: Away team
        winner (ELO): After simulation, contains either the home or away team
        spread (int): Simulated margin of victory for the winning team
        tie (bool): Indicates whether the result is a tie

    """
    K = 20.0

    def __init__(self, home: ELO, away: ELO, **kwargs):
        self.home = home
        self.away = away
        self.winner = None
        self.spread = None
        self.tie = False

    def ELOMargin(self) -> int:
        """Calculates the ELO advantage for the home team, taking into account
        a 65 point home field advantage.  If the home team is favored, then this
        will be a positive value.  If the away team is favored, then this is a
        negative value.

        Returns:
            ELO ranking advantage for the home team; can be negative

        """
        logging.debug("Game %s @ %s", self.away, self.home)
        margin = 65 + self.home.elo - self.away.elo
        logging.debug("ELO Margin = %d", margin)
        return margin

    def PointMargin(self) -> float:
        """Calculates the expected margin of victory for the home team; negative
        numbers indicated an expected loss.

        Returns:
            Expected margin of victory for the home team
        """
        margin = self.ELOMargin() / 25.0
        logging.debug("Expected point margin = %f", margin)
        return margin

    def HomeWinProbability(self) -> float:
        prob = elo.probability(self.ELOMargin())
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
        from 0 to infinity is also given.  Model this as a Gaussian distribution
        and use functionality from `inv_erf` to solve.

        Mutates the object by assigning to the `winner` and `spread` attributes.
        Subsequent calls will not re-simulate the game.

        """
        if self.winner is not None:
            logging.debug("Winner already known: %s", self.winner)
            return
        pt_margin = self.PointMargin()
        prob = self.HomeWinProbability()
        logging.debug("Point margin = %d", pt_margin)
        logging.debug("Home win probability = %f", prob)
        spread = inv_erf.get_spread(pt_margin, prob)
        self.winner = self.home if spread >= 0.0 else self.away
        self.tie = spread == 0.0
        self.spread = abs(self.spread)
        logging.debug("Spread = %d", self.spread)
        logging.debug("Winner = %s", self.winner.name)
        logging.debug("Tie = %s", self.tie)

    @property
    def loser(self) -> ELO:
        """After simulation, obtain the loser of the game"""
        return {self.home.name: self.away, self.away.name: self.home}[self.winner.name]

    def UpdateTeams(self):
        """Once a winner and spread have been determined, this exchanges ELO
        points between the two teams.  If there was a tie, the tie is handled.
        If simulation was not yet performed, the `Simulate` method is called first.

        Raises:
            ValueError: If the winner isn't the home or away team, perhaps from
                        explicitly setting the `winner` attribute

        """
        if self.winner is None:
            self.Simulate()
        if self.tie:
            self.winner.UpdateTie()
            self.loser.UpdateTie()
            return
        # General case of non-ties
        if self.winner is self.home:
            prob = self.HomeWinProbability()
        elif self.winner is self.away:
            prob = self.AwayWinProbability()
        else:
            raise ValueError("Winner is {self.winner} but must be one of {self.home} or {self.away}".format(self=self))
        elo_points = ELOGameSimulator.K * (1.0 - prob)
        elo_points *= math.log(abs(self.spread) + 1.0)
        elo_points /= 1.0 + (self.winner.elo - self.loser.elo) / 2200.0
        logging.debug("Updating with points = %f * %f * (1.0 - %f) / (1.0 + %f/2200.) = %f",
                      ELOGameSimulator.K, math.log(abs(self.spread) + 1), prob,
                      self.winner.elo - self.loser.elo, elo_points)
        self.winner.UpdateWin(elo_points)
        self.loser.UpdateLoss(elo_points)


class ELONeutralGameSimulator(ELOGameSimulator):
    """Simulates a game between two teams represented by `ELO` objects at a neutral site,
    where the home field advantage is removed.

    See `ELOGameSimulator` for more details.

    """

    def __init__(self, home: ELO, away: ELO, **kwargs):
        super().__init__(home, away, **kwargs)

    def ELOMargin(self) -> int:
        """Overrides the method for the base class, removing home field advantage.

        Returns:
             The ELO point margin where positive values indicate an advantage
             for the designated home team.

        """
        # Neutral game, no home field advantage
        logging.debug("Game %s @ %s", self.away, self.home)
        margin = self.home.elo - self.away.elo
        logging.debug("ELO Margin = %d", margin)
        return margin


class ELOKnownGame(ELOGameSimulator):
    """Provides a simulator-like interface to an already played game where simulation
    should not allow for an outcome that doesn't align with reality.

    See `ELOGameSimulator` for more details.  The initializer will set the `winner` attribute
    based on the team scores, and determine the point spread but will not update the teams
    until `UpdateTeams` is called.

    Args:
        home: Home team
        away: Away team
        home_score: Home team score from actual game
        away_score: Away team score from actual game

    """

    def __init__(self, home: ELO, away: ELO, home_score: int, away_score: int):
        super().__init__(home, away, home_score=home_score, away_score=away_score)
        self.winner = self.home if home_score > away_score else self.away
        self.spread = abs(home_score - away_score)


class ELONeutralKnownGame(ELONeutralGameSimulator, ELOKnownGame):
    """Provides a simulator-like interface for an already played game at a neutral site.

    See `ELOKnownGame` and `ELONeutralGameSimulator` for more details.  The initializer
    is inherited from `ELOKnownGame` while `ELOMargin` is inherited from `ELONeutralGameSimulator`
    while the remaining methods are inherited from `ELOGameSimulator`.

    """
    def __init__(self, home: ELO, away: ELO, home_score: int, away_score: int):
        super().__init__(home, away, home_score=home_score, away_score=away_score)


def GetGame(home: ELO, away: ELO, home_score: Optional[int]=None, away_score: Optional[int]=None) -> ELOGameSimulator:
    """Determines the appropriate class to use to represent this game, creates
    an instance of that type and returns it.  This serves as the public API of
    the module and should be the interface used to produce these objects.

    Note that a neutral site is signaled by pre-pending the home team's name
    with an asterisk.

    Args:
        home: Home team
        away: Away team
        home_score: If the game is already played, the home team's score
        away_score: If the game is already played, the away team's score

    Returns:
        Simulator of the game, possibly of a type derived from `ELOGameSimulator`

    """
    if home_score is not None and away_score is not None:
        if home.name.startswith("*"):
            home.name = home.name.strip("*")
            return ELONeutralKnownGame(home, away, home_score, away_score)
        return ELOKnownGame(home, away, home_score, away_score)
    if home.name.startswith("*"):
        home.name = home.name.strip("*")
        return ELONeutralGameSimulator(home, away)
    return ELOGameSimulator(home, away)
