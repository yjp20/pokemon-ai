"""
This module loads the pokemon dexes from the `pokemon-ai/data/dex` directory as
a global variable of this module. The data files must be pre-generated with the
`build_dexes.py` script.
"""

import json
import os

dexes = {}


def __init__():
    for gen in range(1, 7 + 1):
        with open(os.path.join(os.path.dirname(__file__), f'../data/dex/gen{gen}.json')) as dex_file:
            dexes[f'gen{gen}'] = json.load(dex_file)


__init__()
