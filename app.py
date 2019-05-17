#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
'''
DBGR is a tool for testing and debugging HTTP APIs.
'''

import asyncio
import argparse
import argcomplete
from dbgr.requests import get_requests_list, execute_request
from dbgr.environment import Environment
from dbgr.session import get_session
from dbgr.completion import RequestsCompleter, ModulesCompleter


async def prepare_and_execute_request(request, args):
    environment = Environment(args.env)
    session = get_session()
    await execute_request(session, environment, request)


async def interactive_command(args):
    while True:
        request = input('> ')
        if not request or request == 'exit':
            break
        await prepare_and_execute_request(request, args)


async def request_command(args):
    await prepare_and_execute_request(args.request, args)


async def list_command(args):
    print('\n'.join([f'{r.__module__}:{r.__name__}' for r in get_requests_list()]))


async def main():
    parser = argparse.ArgumentParser(
        prog='dbgr',
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(help='command to execute')

    int_parser = subparsers.add_parser(
        'interactive',
        aliases=['int', 'i'],
        help=interactive_command.__doc__
    )
    int_parser.add_argument(
        '-e', '--env',
        default='default',
        help='environment that will be used')
    int_parser.set_defaults(func=interactive_command)

    req_parser = subparsers.add_parser(
        'request',
        aliases=['req', 'r'],
        help=request_command.__doc__
    )
    req_parser.add_argument(
        'request',
        help='Name of the request to execute'
    ).completer=RequestsCompleter()
    req_parser.add_argument(
        '-e', '--env',
        default='default',
        help='environment that will be used')
    req_parser.set_defaults(func=request_command)

    list_parser = subparsers.add_parser(
        'list-requests',
        aliases=['list', 'l'],
        help=list_command.__doc__)
    list_parser.add_argument(
        'module',
        nargs='?',
        help='Filter requests by module'
    ).completer=ModulesCompleter()
    list_parser.set_defaults(func=list_command)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if hasattr(args, 'func'):
        await args.func(args)
    else:
        parser.print_usage()


if __name__ == '__main__':
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print('')
