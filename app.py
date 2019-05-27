#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
'''
DBGR is a tool for testing and debugging HTTP APIs.
'''

import readline # pylint: disable=W0611
import asyncio
import argparse
import sys
import traceback
import textwrap
import argcomplete
import colorama
from dbgr.requests import get_requests, execute_request, parse_cmd_arguments
from dbgr.environment import Environment, get_environments
from dbgr.session import get_session
from dbgr.completion import RequestsCompleter, ModulesCompleter, EnvironmentsCompleter


def version_command():
    ''' Display version of DBGR '''
    from dbgr.meta import __version__
    print(__version__)


async def prepare_and_execute_request(request, args):
    try:
        session = get_session()
        environment = Environment(args.env)
        arguments = parse_cmd_arguments(args.arguments)
        await execute_request(
            session, environment, request, use_defaults=args.use_defaults, **arguments)
    except AssertionError:
        _, _, trace = sys.exc_info()
        trace_info = traceback.extract_tb(trace)
        filename, line, function, text = trace_info[-1] # pylint: disable=W0612
        print(f'{colorama.Fore.RED}Assertion error in {filename}:{line}:')
        print(f'{colorama.Fore.RED}{text}')
    except Exception as ex:
        print(f'{colorama.Fore.RED}{ex}')
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


async def environments_command(args): # pylint: disable=W0613
    ''' List all available environments '''
    for env in get_environments():
        print(f'- {env}')


async def main():
    parser = argparse.ArgumentParser(
        prog='dbgr',
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-v', '--version', action='store_true', help=version_command.__doc__
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
    ).completer = EnvironmentsCompleter()
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
    ).completer = RequestsCompleter()
    req_parser.add_argument(
        '-e', '--env', default='default',
        help='Environment that will be used'
    ).completer = EnvironmentsCompleter()
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
    ).completer = ModulesCompleter()
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
    elif args.version:
        version_command()
    else:
        parser.print_usage()

def dbgr():
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print('')
    except Exception as ex:
        print(f'{colorama.Fore.RED}{ex}')

if __name__ == '__main__':
    dbgr()
