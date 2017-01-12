from functools import total_ordering
from typing import Optional


@total_ordering
class Record:
    """Representation of the season record of a team.  Ordering is
    provided by win percentage, with ties considered 0.5 win.

    Args:
        wins: Starting number of wins, default 0
        losses: Starting number of losses, default 0
        ties: Starting number of ties, default 0

    Attributes:
        wins: Wins thus far, should be in [0,16]
        losses: Losses thus far, should be in [0,16]
        ties: Ties thus far, should be in [0,16]

    """

    def __init__(self, wins: int=0, losses: int=0, ties: int=0):
        self.wins = wins
        self.losses = losses
        self.ties = ties
        self.Verify()

    def __lt__(self, other: 'Record') -> bool:
        """A record is considered less than another if it has a lower
        win percentage.

        """
        return self.WinPercent() < other.WinPercent()

    def __eq__(self, other: 'Record') -> bool:
        return self.__dict__ == other.__dict__

    def __str__(self):
        # return f'{self.wins}-{self.losses}-{self.ties}'
        return '{self.wins}-{self.losses}-{self.ties}'.format(self=self)

    def __repr__(self):
        # return f'Record(wins={self.wins}, losses={self.losses}, ties={self.ties})'
        return 'Record(wins={self.wins}, losses={self.losses}, ties={self.ties})'.format(self=self)

    @property
    def games(self) -> int:
        """Total number of games played thus far"""
        return self.wins + self.losses + self.ties

    def Standings(self) -> str:
        """Create a string representing the standings for fixed width output

        Returns:
            `"wins losses ties"` with each one having leading zeroes

        Examples:
            >>> r = Record(9, 6, 1)
            >>> print(r.Standings)
            09 06 01

        """
        # return f'{self.wins:02d} {self.losses:02d} {self.ties:02d}'
        return '{self.wins:02d} {self.losses:02d} {self.ties:02d}'.format(self=self)

    def Verify(self):
        """Checks if the current record is valid.

        Raises:
            ValueError: if wins, losses, ties, or their sum is less than 0 or greater than 16

        """
        if self.wins not in range(17):
            # raise ValueError(f"Wins is not between 0 and 16, found {self.wins}")
            raise ValueError("Wins is not between 0 and 16, found {self.wins}".format(self=self))
        if self.losses not in range(17):
            # raise ValueError(f"Losses is not between 0 and 16, found {self.losses}")
            raise ValueError("Losses is not between 0 and 16, found {self.losses}".format(self=self))
        if self.ties not in range(17):
            # raise ValueError(f"Ties is not between 0 and 16, found {self.ties}")
            raise ValueError("Ties is not between 0 and 16, found {self.ties}".format(self=self))
        if self.wins + self.losses + self.ties not in range(17):
            # raise ValueError(f"Total games is not between 0 and 16, found {self.wins + self.losses + self.ties}")
            raise ValueError("Total games is not between 0 and 16, found {}".format(self.games))

    def WinPercent(self) -> float:
        """Determines the win percentage for the current standings"""
        return (self.wins + 0.5 * self.ties) / self.games

    def AddWin(self):
        """Mutates the Record to add a win"""
        self.wins += 1

    def AddLoss(self):
        """Mutates the Record to add a loss"""
        self.losses += 1

    def AddTie(self):
        """Mutates the Record to add a tie"""
        self.ties += 1

    def IsUndefeated(self) -> bool:
        """Indicates whether the record corresponds to an undefeated (16-0-0) season"""
        return self.wins == 16 and self.losses == self.ties == 0


@total_ordering
class ELO:
    """Class used to represent an ELO standing.  Requires a team name and a starting ELO.
    Optionally takes either wins, losses, and tries to build a `Record` or directly takes
    a `Record`.  If both are provided, only the `record` is used.  ELO objects are ordered
    based on the team's records; if the records compare equal then the ordering is based
    on the current ELO rankings.

    Args:
        name: Team name
        starting_elo: initial ELO ranking
        wins (optional): Wins used to construct a `Record`, default 0
        losses (optional): Losses used to construct a `Record`, default 0
        ties (optional): Ties used to construct a `Record`, default 0
        record (optional): Record to use, takes priority over `wins`, `losses`, `ties`

    Attributes:
        name (str): Team name
        elo (int): current ELO ranking
        record (Record): current team standings

    """

    def __init__(self, name: str, starting_elo: int,
                 wins: int=0, losses: int=0, ties: int=0,
                 record: Optional[Record]=None):
        self.name = name.strip("*")
        self.elo = starting_elo
        self.record = record or Record(wins, losses, ties)

    @property
    def wins(self) -> int:
        return self.record.wins

    @property
    def losses(self) -> int:
        return self.record.losses

    @property
    def ties(self) -> int:
        return self.record.ties

    def __lt__(self, other: 'ELO') -> bool:
        """Enable sorting by default from teams with highest to lowest win percentage.
        If teams have the same win percentage, sorting follows by ELO rank.

        """
        if self.record < other.record:
            return True
        if self.record > other.record:
            return False
        return self.elo < other.elo

    def __eq__(self, other: 'ELO'):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "ELO(name='{self.name}', starting_elo={self.elo}, record={self.record!r})".format(self=self)

    def __str__(self):
        return "{self.name} ({self.record}) ELO: {self.elo}".format(self=self)

    def UpdateWin(self, points: float):
        """Updates the ELO and record for the current team assuming a win.

        Args:
            points: The number of ELO points the victory is worth, calculated elsewhere

        """
        self.elo += rounded_int(points)
        self.record.AddWin()

    def UpdateLoss(self, points: float):
        """Updates the ELO and record for the current team assuming a loss.

        Args:
            points: The number of ELO points the loss is worth, calculated elsewhere

        """
        self.elo -= rounded_int(points)
        self.record.AddLoss()

    def UpdateTies(self):
        """Updates the record for the current team assuming a tie.  No ELO points are exchanged."""
        self.record.AddTie()

    def IsUndefeated(self) -> bool:
        return self.record.IsUndefeated()


def rounded_int(value: float) -> int:
    """Rounds a floating point number before converting to int.

    Args:
        value: arbitrary number, should be non-inf and non-NaN

    Returns:
        Nearest integer to input

    """
    return int(round(value))


def probability(elo_margin: int) -> float:
    """Calculates the probability of a win given an ELO difference.
    Formula is 1.0 / (1.0 + 10^(-d/400)) for an ELO difference `d`.

    Args:
        elo_margin: The pre-game ELO difference between the two teams,
                    allowing for home team advantage or other modifiers

    Returns:
        Probability of a win

    Examples:
        >>> p = probability(75)
        >>> print("{:0.3f}".format(p))
        0.606

    """
    exponent = -elo_margin / 400.0
    den = 1.0 + 10.0**exponent
    return 1.0 / den


def probability_points(pt_margin: float) -> float:
    """Calculates the probability of a win given by an expected point differential.
    The point differential and ELO difference are related by a factor of 25.

    Args:
        pt_margin: Expected margin of victory in NFL game points

    Returns:
        Probability of winning

    Examples:
        >>> p = probability_points(3.)
        >>> print("{:0.3f}".format(p))
        0.606

    """
    return probability(25 * pt_margin)
