class ELO:

    @staticmethod
    def abs(x: float) -> int:
        return int(round(x))

    def __init__(self, name: str, starting_elo: int, wins: int=0, losses: int=0):
        self.name = name
        self.elo = starting_elo
        self.wins = wins
        self.losses = losses

    def __lt__(self, other) -> bool:
        if self.wins < other.wins:
            return True
        if self.wins > other.wins:
            return False
        return self.elo > other.elo

    def __str__(self):
        return "{s.name} ({s.wins}-{s.losses}) ELO: {s.elo}".format(s=self)

    def UpdateWin(self, points: float):
        self.elo += ELO.abs(points)
        self.wins += 1

    def UpdateLoss(self, points: float):
        self.elo -= ELO.abs(points)
        self.losses += 1

