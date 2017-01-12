import os
import json
from typing import Dict, List
from collections import UserDict

from elo import ELO


class Standings(UserDict):
    """


    """
    def __init__(self, start_elo: Dict[str, ELO]):
        super().__init__(start_elo)

    @classmethod
    def FromJSON(cls, json_file):
        """

        :param json_file:
        :return:
        """
        if not json_file.endswith('.json'):
            json_file += '.json'
        with open(json_file) as f:
            data = json.load(f)
        for team, val in data.items():
            if isinstance(val, ELO):
                continue
            if isinstance(val, int):
                data[team] = ELO(team, val)
            elif isinstance(val, List[int]):
                data[team] = ELO(team, *val)
        return cls(data)

    @classmethod
    def FromJSONDirectory(cls, directory):
        return cls.FromJSON(os.path.join(directory, 'elo_start.json'))

    def __contains__(self, item: str) -> bool:
        return item.strip("*") in self.data

    def __getitem__(self, item: str) -> ELO:
        return self.data[item.strip("*")]

    def get(self, key, default=None):
        return self.data.get(key.strip("*"), default)

    def PrintStandings(self):
        """

        :return:
        """
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
        result = filter(ELO.IsUndefeated, self.values())
        return list(result)

    def GetNumberUndefeated(self) -> int:
        return len(self.GetUndefeated())

