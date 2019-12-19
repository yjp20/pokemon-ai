#!/bin/python3
"""
The CLI tool to interface with the pokemon-dl application
"""

import argparse
import sys
import logging
import coloredlogs

import lib.bots
import lib.showdown
import lib.local

LOGGER = logging.getLogger('pokemon-ai')


def main():
    """
    The main function takes in arguments and runs them in accordance to what
    those arguments dictate. It is essentially a simple CLI adapter to the
    rest of this project.
    """
    parser = argparse.ArgumentParser(
        description="Connect bots locally or externally on showdown."
    )
    parser.add_argument('command', type=str, choices=['showdown', 'local'])
    parser.add_argument('--gen', default='gen1', type=str)
    parser.add_argument('--num', default=1, type=int)
    parser.add_argument('--name', default=None, type=str)
    parser.add_argument('--bot1', default='default', type=str)
    parser.add_argument('--bot2', default='default', type=str)
    parser.add_argument('--gamemode', default='gen1randombattle', type=str)
    parser.add_argument('--loglevel', default='INFO', type=str)
    parser.add_argument('--savereplay', default=False, type=bool)
    parser.add_argument('--challenge', type=str)
    args = parser.parse_args(sys.argv[1:])

    numeric_level = getattr(logging, args.loglevel.upper())
    if not isinstance(numeric_level, int):
        raise ValueError('invalid log level: %s' % args.loglevel.upper())
    coloredlogs.install(numeric_level)

    if args.command == 'showdown':
        LOGGER.info("Starting Showdown")
        bot1 = lib.bots.Bot("p1", args.gen, args.bot1)
        lib.showdown.Showdown(bot1, name=args.name, challenge=args.challenge)

    if args.command == 'local':
        LOGGER.info("Starting Local")
        bot1 = lib.bots.Bot("b1", args.gen, args.bot1)
        bot2 = lib.bots.Bot("b2", args.gen, args.bot2)
        lib.local.Local([bot1, bot2], args.gamemode, args.num, args.savereplay)


if __name__ == '__main__':
    main()
