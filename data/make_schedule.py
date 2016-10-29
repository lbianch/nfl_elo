import os
import json
import itertools

from data import get_data


def dereference(data: dict):
    teams = get_teams(data)
    venues = get_venues(data)
    for game in data['games']:
        game['home_team'] = teams[game['home_team_id']]
        game['away_team'] = teams[game['away_team_id']]
        game['venue'] = venues[game['venue_id']]
        del game['home_team_id']
        del game['away_team_id']
        del game['venue_id']
        yield game


def get_teams(data: dict):
    teams = itertools.chain(data['home_teams'], data['away_teams'])
    return {team['id']: team for team in teams}


def get_team_name(team: dict):
    team = team['slug'][4:].upper()
    if team == 'STL':
        return 'LA'
    return team


def get_venues(data: dict):
    return {venue['id']: venue for venue in data['venues']}


def get_game(game: dict):
    home = get_team_name(game['home_team'])
    away = get_team_name(game['away_team'])
    if game['venue']['country'] != "USA":
        home = '*' + home
    if game['status'] == 'upcoming':
        return [home, away]
    home_score = int(game['home_team_score'])
    away_score = int(game['away_team_score'])
    return [home, away, home_score, away_score]


def get_week(week: int, year: int=2016):
    payload = {'season_id': 'nfl-{}-{}'.format(year, year + 1),
               'week': str(week)}
    data = get_data.get_data(payload)
    data = dereference(data)
    for game in data:
        yield get_game(game)


def get_season(year: int=2016):
    data = [list(get_week(week, year)) for week in range(1, 18)]
    return {'expected': [len(week) for week in data],
            'schedule': data}


def create_season(year: int=2016):
    data = get_season(year)
    data = json.dumps(data, sort_keys=True)
    data = data.replace('[[[', '[\n[[')
    data = data.replace(']],', ']\n],')
    data = data.replace('],', '],\n')
    with open(os.path.join(str(year), 'schedule.json'), 'w') as output:
        output.write(data)


if __name__ == '__main__':
    create_season(2016)
