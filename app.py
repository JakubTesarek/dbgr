#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
'''
DBGR is a tool for testing and debugging HTTP APIs.
'''

import asyncio
import argparse
import argcomplete
import colorama
from dbgr.requests import get_requests_list, execute_request, RequestNotFoundError
from dbgr.environment import Environment
from dbgr.session import get_session
from dbgr.completion import RequestsCompleter, ModulesCompleter


async def prepare_and_execute_request(request, args):
    try:
        environment = Environment(args.env)
        session = get_session()
        await execute_request(session, environment, request)
    except Exception as e:
        print(f'{colorama.Fore.RED}{e}')
    finally:
        await session.close()


async def interactive_command(args):
    print(f'{colorama.Style.DIM}Dbgr interactive mode; press ^C to exit.')
    while True:
        request = input('> ')
        await prepare_and_execute_request(request, args)


async def request_command(args):
    await prepare_and_execute_request(args.request, args)


async def list_command(args):
    last_module = None
    for r in get_requests_list():
        if args.module is None or r.__module__ == args.module:
            if r.__module__ != last_module:
                print(f'{r.__module__}:')
            last_module = r.__module__
            print(f' - {r.__name__}')


async def main():
    parser = argparse.ArgumentParser(
        prog='dbgr',
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(help='Command to execute')

    int_parser = subparsers.add_parser(
        'interactive',
        aliases=['int', 'i'],
        help=interactive_command.__doc__
    )
    int_parser.add_argument(
        '-e', '--env',
        default='default',
        help='Environment that will be used (default: "default"')
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
        help='Environment that will be used')
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
    colorama.init(autoreset=True)
    if hasattr(args, 'func'):
        await args.func(args)
    else:
        parser.print_usage()


if __name__ == '__main__':
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print('')
    except Exception as e:
        print(f'{colorama.Fore.RED}{e}')
