#!/bin/python3

"""
The CLI tool to interface with the pokemon-dl application
"""

import argparse
import sys


def get_command(choices):
    """
    get_command returns which command it is from sys.argv
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('command', type=str, choices=choices)
    args = parser.parse_args(sys.argv)
    return args.command

def main():
    """
    The
    """
    cmd = get_command(['showdown', 'local'])
    if cmd == 'showdown':
        pass
    if cmd == 'local':
        pass
