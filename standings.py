import json
from typing import Dict, List

from elo import ELO


class Standings(dict):  # Use with `elo_start.json`
    def __init__(self, start_elo: Dict[str, List[int]]):
        super().__init__()
        for team in start_elo:
            self[team] = ELO(team, *start_elo[team])

    @staticmethod
    def _FormatDict(data):
        for team, val in data.items():
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

    def __contains__(self, item: str) -> bool:
        return dict.__contains__(self, item.strip("*"))

    def __getitem__(self, item: str) -> ELO:
        return dict.__getitem__(self, item.strip("*"))

    def PrintStandings(self):
        # Note this relies on ELO.__lt__
        for team in sorted(self.values(), reverse=True):
            print('{:3} {}'.format(team.name, team.record.Standings()))

    def Wins(self, team: str) -> int:
        return self[team].wins

    def Losses(self, team: str) -> int:
        return self[team].losses

    def Ties(self, team: str) -> int:
        return self[team].ties

    def GetUndefeated(self) -> List[ELO]:
        return filter(ELO.IsUndefeated, self.values())

    def GetNumberUndefeated(self) -> int:
        return len(self.GetUndefeated())
