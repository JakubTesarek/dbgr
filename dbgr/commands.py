import argparse
import sys
import traceback
import textwrap
import colorama
from dbgr.requests import get_requests, execute_request, parse_cmd_arguments, parse_module_name
from dbgr.environment import init_environment, get_environments, DEFAULT_ENVIRONMENT, Environment
from dbgr.session import close_session
from dbgr.completion import RequestsCompleter, ModulesCompleter, EnvironmentsCompleter


def version_command():
    ''' Display version of DBGR '''
    from dbgr.meta import __version__
    print(__version__)


async def prepare_and_execute_request(request, args):
    try:
        init_environment(args.env)
        arguments = parse_cmd_arguments(args.arguments)
        await execute_request(request, use_defaults=args.use_defaults, **arguments)
    except AssertionError:
        _, _, trace = sys.exc_info()
        trace_info = traceback.extract_tb(trace)
        filename, line, function, text = trace_info[-1] # pylint: disable=W0612
        print(f'{colorama.Fore.RED}Assertion error in {filename}:{line}:')
        print(f'{colorama.Fore.RED}{text}')
    except Exception as ex:
        print(f'{colorama.Fore.RED}{ex}')


async def interactive_command(args):
    ''' Run requests in interactive mode '''
    print(f'{colorama.Style.DIM}Dbgr interactive mode; press ^C to exit.')
    try:
        while True:
            request = input('> ').strip()
            await prepare_and_execute_request(request, args)
    finally:
        await close_session()


async def request_command(args):
    ''' Execute request '''
    try:
        await prepare_and_execute_request(args.request, args)
    finally:
        await close_session()


async def list_command(args):
    ''' List all available requests and their arguments '''
    l_module, l_request = parse_module_name(args.module)
    requests = get_requests()
    if not requests:
        print(f'{colorama.Fore.RED}No requests found.')
        return
    if l_module and l_module not in requests:
        print(f'{colorama.Fore.RED}Module "{l_module}" does not exist.')
        return
    if l_module and l_request and l_request not in requests[l_module]:
        print(f'{colorama.Fore.RED}Request "{l_request}" does not exist in module "{l_module}".')
        return
    request_printed = False
    for module, requests in requests.items():
        module_printed = False
        if not l_module or module == l_module:
            for request in requests.values():
                if not l_request or request.name == l_request:
                    if not module_printed:
                        print(f'{colorama.Style.BRIGHT}{module}:')
                        module_printed = True
                        request_printed = True
                    print(textwrap.indent(str(request), ' '), end='')
        if not request_printed and l_request:
            print(f'{colorama.Fore.RED}Request "{l_request}" does not exist in any module.')

async def environments_command(args): # pylint: disable=W0613
    '''
        List available environments. With optional <environment> argument
        lists all defined variables and values
    '''
    if args.environment:
        env = Environment(args.environment)
        for section in env.sections():
            print(f'{colorama.Style.BRIGHT}{section}')
            for key, value in env.items(section):
                print(f'- {key}: {value}')
    else:
        for env in get_environments():
            if env == DEFAULT_ENVIRONMENT:
                print(f'- {colorama.Style.BRIGHT}{env}')
            else:
                print(f'- {env}')


def argument_parser():
    parser = argparse.ArgumentParser(
        prog='dbgr',
        description='DBGR is a tool for testing and debugging HTTP APIs.',
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
        '-e', '--env', default=DEFAULT_ENVIRONMENT,
        help=f'Environment that will be used (default: "{DEFAULT_ENVIRONMENT}")'
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
        '-e', '--env', default=DEFAULT_ENVIRONMENT,
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
        help=(
            'Module name or fully qualified request name `module:request`. '
            'Optinally you can omit the module name: `:request`'
        )
    ).completer = ModulesCompleter()
    list_parser.set_defaults(func=list_command)

    environments_parser = subparsers.add_parser(
        'list-environments',
        aliases=['envs', 'e'],
        help=environments_command.__doc__)
    environments_parser.add_argument(
        'environment',
        nargs='?',
        help='Name of environment to list'
    ).completer = EnvironmentsCompleter()
    environments_parser.set_defaults(func=environments_command)
    return parser
