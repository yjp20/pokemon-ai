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
    parser.add_argument('--bot1', default='gen1/baseline', type=str)
    parser.add_argument('--bot2', default='gen1/baseline', type=str)
    parser.add_argument('--gamemode', default='gen1randombattle', type=str)
    parser.add_argument('--loglevel', default='INFO', type=str)
    args = parser.parse_args(sys.argv[1:])

    numeric_level = getattr(logging, args.loglevel.upper())
    if not isinstance(numeric_level, int):
        raise ValueError('invalid log level: %s' % args.loglevel.upper())
    logging.basicConfig(level=numeric_level)

    if args.command == 'showdown':
        logging.info("Starting Showdown")
        showdown.Showdown(showdown.HTTP_URI, showdown.WS_URI)
    if args.command == 'local':
        logging.info("Starting Local")
        bot1 = bots.Bot("p1", args.bot1, True)
        bot2 = bots.Bot("p2", args.bot2, True)
        local.Local(bot1, bot2, args.gamemode)

if __name__ == '__main__':
    main()
