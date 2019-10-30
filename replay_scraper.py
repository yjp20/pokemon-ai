#!/bin/python3

# This module should be run anywhere from every two hours to half a day.

import sqlite3
import requests
import re

testing = False
generations = []
formats = []
query = 10
conn = None
c = None

create_table_string = '''
CREATE TABLE IF NOT EXISTS replays (
    name text PRIMARY KEY,
    gameformat text,
    log text
)
'''

if testing:
    generations = [1]
    formats = ['randombattle']
    query = 4
    conn = sqlite3.connect('data/testing.db')
    c = conn.cursor()
else:
    generations = [1, 2, 3, 4, 5, 6, 7]
    formats = ['randombattle', 'ou']
    conn = sqlite3.connect('data/data.db')
    c = conn.cursor()


def process_url(url, gameformat):
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f'Failed to get {url}')
    body = str(r.content)
    games = re.findall(r'/gen\d[a-z]+-\d+', body)
    for game in games:
        print(game)
        q = c.execute(
            'SELECT EXISTS (SELECT 1 FROM replays where name=? limit 1)',
            (game, ))
        if q.fetchone()[0] == 0:  # if entry doesn't already exist in database
            print(f'Fetching {game}')
            sr = requests.get(f'https://replay.pokemonshowdown.com{game}.log')
            if sr.status_code != 200:
                raise Exception(f'Failed to get {game}')
            obj = (game, gameformat, sr.content)
            c.execute('INSERT INTO replays VALUES (?,?,?)', obj)
            conn.commit()


def main():
    c.execute(create_table_string)

    for g in generations:
        for f in formats:
            for i in range(1, query + 1):
                fmt = f'gen{g}{f}'
                url = f'https://replay.pokemonshowdown.com/search'
                f'?user=&format={fmt}&page={i}&output=html'
                process_url(url, fmt)
    conn.close()


if __name__ == '__main__':
    main()
