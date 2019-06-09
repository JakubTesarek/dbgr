#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
'''
DBGR is a tool for testing and debugging HTTP APIs.
'''

import readline # pylint: disable=W0611
import asyncio
import colorama
import argcomplete
from dbgr.commands import argument_parser, version_command


async def main():
    parser = argument_parser()
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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print('')
    except Exception as ex:
        print(f'{colorama.Fore.RED}{ex}{colorama.Style.RESET_ALL}')

if __name__ == '__main__':
    dbgr()
