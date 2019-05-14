#!/usr/bin/env python

import asyncio
import argparse
from dbgr import REQUESTS, load_requests, find_request
from dbgr.configuration import Configuration
from dbgr.session import get_session


async def execute_request(cmd, configuration):
    request = find_request(cmd)
    async with get_session() as session:
        await request(configuration.conf, session)


async def interactive_mode(configuration):
    while True:
        cmd = input('> ')
        if not cmd or cmd == 'exit':
            break
        await execute_request(cmd, configuration)


def list_requests():
    return '\n'.join([n.__name__ for n in REQUESTS])


async def main():
    load_requests()
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='\n'.join([n.__name__ for n in REQUESTS])
    )
    parser.add_argument('cmd', nargs='?', help='Name of a request to execute')
    args = parser.parse_args()
    configuration = Configuration('env.json')
    if args.cmd:
        await execute_request(args.cmd, configuration)
    else:
        await interactive_mode(configuration)


if __name__ == '__main__':
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print('')
