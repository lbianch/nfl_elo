import requests


URL = 'https://api.stattleship.com/football/nfl/games'
with open('api_token.txt') as f:
    API_TOKEN = f.read().strip()
HEADERS = {'Content-Type': 'application/json',
           'Accept': 'application/vnd.stattleship.com; version=1',
           'Authorization': 'Token token={}'.format(API_TOKEN)}

def get_data(payload):
    r = requests.get(URL, params=payload, headers=HEADERS)
    r.raise_for_status()
    return r.json()