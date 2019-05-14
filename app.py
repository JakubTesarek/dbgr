#!/usr/bin/env python
'''
DBGR is a tool for testing and debugging HTTP APIs.
'''

import asyncio
import argparse
from dbgr import REQUESTS, load_requests, find_request
from dbgr.environment import Environment
from dbgr.session import get_session


async def interactive_command(args):
    while True:
        cmd = input('> ')
        if not cmd or cmd == 'exit':
            break
        await execute_request(cmd)


async def request_command(args):
    await execute_request(args.request)


async def list_command(args):
    print('\n'.join([f'{r.__module__}:{r.__name__}' for r in REQUESTS]))


async def execute_request(request):
    environment = Environment('env.json')
    request = find_request(request)
    async with get_session() as session:
        await request(environment.env, session)


async def main():
    load_requests()

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
    int_parser.set_defaults(func=interactive_command)

    req_parser = subparsers.add_parser(
        'request',
        aliases=['req', 'r'],
        help=request_command.__doc__
    )
    req_parser.add_argument('request', help='Name of the request to execute')
    req_parser.set_defaults(func=request_command)

    list_parser = subparsers.add_parser(
        'list-requests',
        aliases=['list', 'l'],
        help=list_command.__doc__)
    list_parser.add_argument('module', nargs='?', help='Filter requests by module')
    list_parser.set_defaults(func=list_command)

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
