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

def main():
    """
    The main function
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('command', type=str, choices=['showdown', 'local'])
    parser.add_argument('--gen', default='gen1', type=str)
    parser.add_argument('--name', default='battleboy21', type=str)
    parser.add_argument('--bot1', default='baseline', type=str)
    parser.add_argument('--bot2', default='baseline', type=str)
    parser.add_argument('--gamemode', default='gen1randombattle', type=str)
    parser.add_argument('--loglevel', default='INFO', type=str)
    parser.add_argument('--challenge', type=str)
    args = parser.parse_args(sys.argv[1:])

    numeric_level = getattr(logging, args.loglevel.upper())
    if not isinstance(numeric_level, int):
        raise ValueError('invalid log level: %s' % args.loglevel.upper())
    logger = logging.getLogger('pokemon-ai')
    logger.setLevel(numeric_level)

    if args.command == 'showdown':
        logging.info("Starting Showdown")
        bot1 = bots.Bot("p1", args.gen, args.bot1)
        showdown.Showdown(args.name,
                          bot1,
                          showdown.WS_URI,
                          showdown.HTTP_URI,
                          args.challenge)
    if args.command == 'local':
        logging.info("Starting Local")
        bot1 = bots.Bot("p1", args.gen, args.bot1)
        bot2 = bots.Bot("p2", args.gen, args.bot2)
        local.Local(bot1, bot2, args.gamemode)

if __name__ == '__main__':
    main()
