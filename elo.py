from functools import total_ordering


@total_ordering
class Record:
    def __init__(self, wins: int=0, losses: int=0, ties: int=0):
        self.wins = wins
        self.losses = losses
        self.ties = ties
        self.Verify()

    def __lt__(self, other) -> bool:
        return self.WinPercent() < other.WinPercent()

    def __eq__(self, other) -> bool:
        return self.__dict__ == other.__dict__

    def __str__(self):
        return '{s.wins}-{s.losses}-{s.ties}'.format(s=self)

    def __repr__(self):
        return 'Record(wins={s.wins}, losses={s.losses}, ties={s.ties}'.format(s=self)

    def Standings(self) -> str:
        return '{s.wins:02d} {s.losses:02d} {s.ties:02d}'.format(s=self)

    def Verify(self):
        assert 0 <= self.wins <= 16, self
        assert 0 <= self.losses <= 16, self
        assert 0 <= self.ties <= 16, self

    def WinPercent(self) -> float:
        return self.wins / (self.wins + self.losses + self.ties)

    def AddWin(self):
        self.wins += 1

    def AddLoss(self):
        self.losses += 1

    def AddTie(self):
        self.ties += 1

    def IsUndefeated(self) -> bool:
        return self.wins == 16 and self.losses == self.ties == 0


@total_ordering
class ELO:
    def __init__(self, name: str, starting_elo: int, wins: int=0, losses: int=0, ties: int=0, record: Record=None):
        self.name = name.strip("*")
        self.elo = starting_elo
        self.record = record or Record(wins, losses, ties)
        self.neutral = name.startswith("*")

    @staticmethod
    def abs(x: float) -> int:
        return int(round(x))

    @property
    def wins(self):
        return self.record.wins

    @property
    def losses(self):
        return self.record.losses

    @property
    def ties(self):
        return self.record.ties

    def __lt__(self, other) -> bool:
        """Enable sorting by default from teams with most wins to fewest wins.
        If teams have the same number of wins, sorting would occur by ELO rank.
        """
        if self.record < other.record:
            return True
        if self.record > other.record:
            return False
        return self.elo < other.elo

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "ELO(name='{s.name}', starting_elo={s.elo}, wins={s.wins}, losses={s.losses}, ties={s.ties})".format(s=self)

    def __str__(self):
        return "{s.name} ({s.record}) ELO: {s.elo}".format(s=self)

    def UpdateWin(self, points: float):
        self.elo += ELO.abs(points)
        self.record.AddWin()

    def UpdateLoss(self, points: float):
        self.elo -= ELO.abs(points)
        self.record.AddLoss()

    def UpdateTies(self):
        # No ELO exchange for ties
        self.record.AddTie()

    def IsUndefeated(self) -> bool:
        return self.record.IsUndefeated()


def probability(elo_margin: int) -> float:
    exponent = -elo_margin / 400.0
    den = 1.0 + 10.0**exponent
    return 1.0 / den

def probability_points(pt_margin: float) -> float:
    return probability(25 * pt_margin)
