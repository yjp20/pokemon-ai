# Pokemon-ai

This is a project that allows a more systematic approach to training Pokemon bots. Frankly, the code quality is rather shabby, but that is under constant improvement.

The framework was written in an effort to create our own ultimate bot. While that is currently under progress, when it is done the white paper will be available in this repository. Writing your own bots is pretty simple too, and we welcome any contributions or ideas.

## Prerequisites

* Python >3.6. While this may work with older version of Python, it is entirely untested.
* Node.js. The local simulator uses the official showdown code, which is written in js.

## Setup

1. Make sure to get the Pokemon-Showdown submodule: `git submodule update --init --recursive`
2. Build the Pokemon-Showdown module through `npm i` and `npm build` inside `thirdparty/Pokemon-Showdown`
3. Build the pokemon-showdown-client module through `npm run build full` inside `web/pokemon-showdown-client/`
3. Generate the local dex through `node build_dex.js`
4. Install required python modules `websocket`, `requests`, and `coloredlogs`.

## Project Architecture

Pokemon-Showdown does all of its communications through text streams, so we can use their code to run local simulations to run much, much faster self-play training while also easily maintaininj:g compatability with the official server.

Bot the Showdown and Local "adapters" load different bots based upon the arguments that are given, which are then dynamically loaded from the `ai` folder. Each file in the `ai` folder represents one implementation of a bot, and it should export one main function that either the local or showdown adapters will call.

The training of the bots are done externally to the core of the project structure, but the specific implementation is TBD.

## Files
* `pokemon_ai.py` this file handles all the simulations, both running locally and externally.
* `replay_scraper.py` this file scrapes replay.pokemonshowdown.com for all the files for gen 1~7 randombattle and ou. Unfortunately, this method can only save replays that were manually saved and can only go back so far. This means that compared to the theoretical maximum, there is far less data available using this method.
* `replay_watcher.py` this file is the better brother to replay_scraper. Instead of running periodically, it is run as a service, where it keeps watching through the showdown websocket protocol to look for new games. This means that this should theoretically manage to catch all games that are played in a certain timespan. The main limitation of this system is that it is more intensive than the scraper and also not yet implemented.
