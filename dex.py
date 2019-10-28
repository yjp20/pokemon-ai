import json

dexes = {}


def __init__():
    for gen in range(1, 7 + 1):
        with open(f'./data/dex/gen{gen}.json') as f:
            dexes[f'gen{gen}'] = json.load(f)


__init__()
