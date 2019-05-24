#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
'''
DBGR is a tool for testing and debugging HTTP APIs.
'''

import readline
import asyncio
import argparse
import argcomplete
import colorama
import sys
import traceback
import textwrap
from dbgr.requests import get_requests, execute_request, RequestNotFoundError, parse_cmd_arguments
from dbgr.environment import Environment, get_environments
from dbgr.session import get_session
from dbgr.completion import RequestsCompleter, ModulesCompleter, EnvironmentsCompleter


async def prepare_and_execute_request(request, args):
    try:
        session = get_session()
        environment = Environment(args.env)
        arguments = parse_cmd_arguments(args.arguments)
        await execute_request(
            session, environment, request, use_defaults=args.use_defaults, **arguments)
    except AssertionError as e:
        _, _, tb = sys.exc_info()
        tb_info = traceback.extract_tb(tb)
        filename, line, func, text = tb_info[-1]
        print(f'{colorama.Fore.RED}Assertion error in {filename}:{line}:')
        print(f'{colorama.Fore.RED}{text}')
    except Exception as e:
        print(f'{colorama.Fore.RED}{e}')
    finally:
        await session.close()


async def interactive_command(args):
    ''' Run requests in interactive mode '''
    print(f'{colorama.Style.DIM}Dbgr interactive mode; press ^C to exit.')
    while True:
        request = input('> ')
        await prepare_and_execute_request(request, args)


async def request_command(args):
    ''' Execute request '''
    await prepare_and_execute_request(args.request, args)


async def list_command(args):
    ''' List all available requests and their arguments '''
    for module, requests in get_requests().items():
        if not args.module or module == args.module:
            print(f'{colorama.Style.BRIGHT}{module}:')
            for request in requests.values():
                print(textwrap.indent(str(request), ' '), end='')


async def environments_command(args):
    ''' List all available environments '''
    for env in get_environments():
        print(f'- {env}')


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
        '-e', '--env', default='default',
        help='Environment that will be used (default: "default")'
    ).completer=EnvironmentsCompleter()
    int_parser.add_argument(
        '-d', '--use-defaults', action='store_true',
        help='Use default values when possible')
    int_parser.set_defaults(func=interactive_command, arguments=[])

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
        '-e', '--env', default='default',
        help='Environment that will be used'
    ).completer=EnvironmentsCompleter()
    req_parser.add_argument(
        '-d', '--use-defaults', action='store_true',
        help='Use default values when possible')
    req_parser.add_argument(
        '-a', '--arg', dest='arguments', action='append', default=[],
        help='Arguments for requests execution')
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

    environments_parser = subparsers.add_parser(
        'list-environments',
        aliases=['envs', 'e'],
        help=environments_command.__doc__)
    environments_parser.set_defaults(func=environments_command)

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
