import os
import json
from typing import List, Dict, Union
from collections import UserList

from elo import ELO

class Week(UserList):
    """

    """
    def __init__(self, data: List[Union[str, int]]):
        super().__init__(data)

    def ToELO(self) -> ELO:
        return ELO(*self.data)


class SeasonError(Exception):
    pass


class Season(UserList):
    """

    """
    def __init__(self, data: Dict[str, List[Union[int, List[Union[str, int]]]]]):
        super().__init__(Week(d) for d in data['schedule'])
        self.VerifyData(data['expected'])

    @classmethod
    def FromJSON(cls, json_file: str):
        """

        :param json_file:
        :return:
        """
        if not json_file.endswith(".json"):
            json_file += '.json'
        with open(json_file) as f:
            return cls(json.load(f))

    @classmethod
    def FromJSONDirectory(cls, directory: str):
        """

        :param directory:
        :return:
        """
        return cls.FromJSON(os.path.join(directory, 'schedule.json'))

    def VerifyData(self, expected=None):
        """

        :param expected:
        :return:
        """
        if len(self) != 17:
            raise SeasonError(f"Season must have 17 weeks, found {len(self)}")
        if expected is None:
            expected = [len(w) for w in self]
        if len(expected) != 17:
            raise SeasonError(f"Expected season data must have 17 weeks, found {len(expected)}")
        teams = set()
        for i, week in enumerate(self):
            if len(week) != expected[i]:
                raise SeasonError(f"Week {i+1} expected {expected[i]} games but found {len(week)} games")
            week_teams = []
            for game in week:
                if len(game) not in [2, 4]:
                    raise SeasonError(f"Week {i+1} has game with incorrect arguments, need 2 or 4")
                if not isinstance(game[0], str):
                    raise SeasonError(f"Home team is not string, found {game[0]}")
                if not isinstance(game[1], str):
                    raise SeasonError(f"Home team is not string, found {game[1]}")
                home, away = map(lambda g: g.strip("*"), game[0:2])
                teams.update([home, away])
                week_teams.append(home)
                week_teams.append(away)
                if len(game) == 2:
                    continue
                for score in game[2:4]:
                    if not isinstance(score, int):
                        raise SeasonError(f"Score must be integer, found {score}")
                    if score not in range(100):
                        raise SeasonError(f"Score must be between 0 and 99, found {score}")
            if len(week_teams) != 2 * expected[i]:
                raise SeasonError(f"Week {i+1} {expected[i]} games {week_teams}")
            if len(week_teams) != len(set(week_teams)):
                duplicates = set(filter(lambda t: week_teams.count(t) > 1, week_teams))
                raise SeasonError(f"Week {i+1} Duplicate {duplicates}")
            week_teams = set(week_teams)
            if not week_teams.issubset(teams):
                extra_teams = week_teams - teams
                raise SeasonError(f"Unexpected teams found: {extra_teams}")
        if len(teams) != 32:
            raise SeasonError(f"Must have 32 teams, found {len(teams)}")
        for team in teams:
            if len(team) not in (2, 3):
                raise SeasonError(f"Team name must be 2 or 3 characters, found {team}")
            if not team.isupper():
                raise SeasonError(f"Team name must be uppercase, found {team}")
            if not team.isalpha():
                raise SeasonError(f"Team name '{team}' not valid")
