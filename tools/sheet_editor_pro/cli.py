# -*- coding: utf-8 -*-
"""
Created on Wed May 20 13:46:14 2020

@author: Dripta
"""

import argparse
from Editor_backend import checker, updater, sheet_save
import sys


def main():
    parser = argparse.ArgumentParser(
        prog='Google sheet updater')
    subparsers = parser.add_subparsers(
        help='sub-command for cov-server', dest="command")
    parser_a = subparsers.add_parser('update', help='updates the google sheet')
    parser_a.add_argument('--skip', action='store_true',
                          help='Skips the error')
    parser_a.add_argument('--save', action='store_true',
                          help='Save the google sheet as csv format')

    args = parser.parse_args()

    if args.command == 'update':
        if '--skip' in sys.argv:
            if '--save' in sys.argv:
                updater(skip=True)
                sheet_save()
            else:
                updater(skip=True)
        else:
            updater()


if __name__ == '__main__':
    main()

