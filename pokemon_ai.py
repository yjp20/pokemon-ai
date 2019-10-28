#!/bin/python3
"""
The CLI tool to interface with the pokemon-dl application
"""

import argparse
import sys
import logging

import bots
import local
import showdown

LOGGER = logging.getLogger('pokemon-ai')


def main():
    """
    The main function
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('command', type=str, choices=['showdown', 'local'])
    parser.add_argument('--gen', default='gen1', type=str)
    parser.add_argument('--num', default=1, type=int)
    parser.add_argument('--name', default=None, type=str)
    parser.add_argument('--bot1', default='default', type=str)
    parser.add_argument('--bot2', default='default', type=str)
    parser.add_argument('--gamemode', default='gen1randombattle', type=str)
    parser.add_argument('--loglevel', default='INFO', type=str)
    parser.add_argument('--challenge', type=str)
    args = parser.parse_args(sys.argv[1:])

    numeric_level = getattr(logging, args.loglevel.upper())
    if not isinstance(numeric_level, int):
        raise ValueError('invalid log level: %s' % args.loglevel.upper())
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.info("HELLO")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    LOGGER.addHandler(console_handler)

    if args.command == 'showdown':
        LOGGER.info("Starting Showdown")
        bot1 = bots.Bot("p1", args.gen, args.bot1)
        showdown.Showdown(bot1, name=args.name, challenge=args.challenge)
    if args.command == 'local':
        LOGGER.info("Starting Local")
        bot1 = bots.Bot("b1", args.gen, args.bot1)
        bot2 = bots.Bot("b2", args.gen, args.bot2)
        local.Local([bot1, bot2], args.gamemode, args.num)


if __name__ == '__main__':
    main()
