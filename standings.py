import json
from typing import Dict, List

from elo import ELO


class Standings(dict):
    def __init__(self, start_elo: Dict[str, List[int]]):
        super().__init__()
        for team in start_elo:
            self[team] = ELO(team, *start_elo[team])

    @staticmethod
    def _FormatDict(data):
        for team, val in data:
            if not isinstance(val, list):
                data[team] = [val]
        return data

    @classmethod
    def FromJSON(cls, json_file):
        if not json_file.endswith('.json'):
            json_file += '.json'
        with open(json_file) as f:
            data = json.load(f)
        return cls(Standings._FormatDict(data))

    @classmethod
    def FromFile(cls, f):
        return cls(Standings._FormatDict(json.load(f)))

    @classmethod
    def FromDict(cls, d):
        return cls(Standings._FormatDict(d))

    @classmethod
    def FromString(cls, string):
        return cls(Standings._FormatDict(json.loads(string)))

    def PrintStandings(self):
        for team in sorted(self.values()):
            wins = str(team.wins).rjust(3)
            losses = str(team.losses).rjust(3)
            print('{} {} {}'.format(team.name.ljust(3), wins, losses))

    def Wins(self, team: str):
        return self[team].wins

    def Losses(self, team: str):
        return self[team].losses

    def IsUndefeated(self, team: str):
        return self.Wins(team) == 16 and self.Losses(team) == 0

    def GetUndefeated(self):
        return list(filter(self.IsUndefeated, self))

    def GetNumberUndefeated(self):
        return len(self.GetUndefeated())
