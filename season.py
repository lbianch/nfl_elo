import json
from typing import Dict
from collections import UserList


class Week(UserList):
    def __init__(self, data: list):
        super().__init__(data)


class Season(UserList):  # Use with `schedule.json`
    def __init__(self, data: Dict[str, list]):
        super().__init__([Week(d) for d in data['schedule']])
        self.VerifyData(data['expected'])

    @classmethod
    def FromJSON(cls, json_file: str):
        if not json_file.endswith(".json"):
            json_file += '.json'
        with open(json_file) as f:
            data = json.load(f)
        return cls(data)

    def VerifyData(self, expected=None):
        assert len(self) == 17
        if expected is None:
            expected = [len(w) for w in self]
        assert len(expected) == 17, expected
        teams = set()
        for i, week in enumerate(self):
            assert len(week) == expected[i], "Week {}".format(i + 1)
            week_teams = []
            for game in week:
                assert len(game) == 2 or len(game) == 4, game
                assert isinstance(game[0], str), game
                assert isinstance(game[1], str), game
                home, away = map(lambda g: g.strip("*"), game[0:2])
                teams.update([home, away])
                week_teams.append(home)
                week_teams.append(away)
                if len(game) == 2:
                    continue
                scores = game[2:4]
                for score in scores:
                    assert isinstance(score, int), game
                    assert 0 <= score < 100, game
            assert len(week_teams) == 2 * expected[i], \
                "Week {} {} games {}".format(i + 1, expected[i], week_teams)
            assert len(week_teams) == len(set(week_teams)), \
                "Week {} Duplicate {}".format(i + 1, set([t for t in week_teams if week_teams.count(t) > 1]))
            week_teams = set(week_teams)
            assert week_teams.issubset(teams)
        assert len(teams) == 32, teams
        for team in teams:
            assert len(team) in (2, 3), team
            assert team.isupper(), team
            assert team.isalpha(), team
