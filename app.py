import asyncio
import aiohttp
import json
import requests
import functools
import argparse
from itertools import cycle
from datetime import datetime, timedelta


REQUESTS = set()
with open('conf.env.json', 'r') as f:
    ENV = json.load(f)


def request(request):
    @functools.wraps(request)
    async def wrapper_decorator(*args, **kwargs):
        await request(*args, **kwargs)
    REQUESTS.add(wrapper_decorator)
    return wrapper_decorator


def print_response(response):
    print(f'{response.method} {response.url}')
    print(f'{response.status} {response.reason}')
    for name, value in response.headers.items():
        print(f'{name}: {value}')



async def progress_bar():
    start = datetime.now()
    for bar in cycle(['\\', '-', '/', '|']):
        elapsed = datetime.now() - start
        print(f'in progress {bar} [{elapsed}]', end='\r')
        await asyncio.sleep(0.1)


async def execute_request(cmd):
    for request in REQUESTS:
        if request.__name__ == cmd:
            asyncio.ensure_future(progress_bar())
            async with aiohttp.ClientSession() as session:
                await asyncio.sleep(3)
                await request(ENV, session)


async def interactive_mode():
    while True:
        cmd = input('> ')
        if not cmd or cmd == 'exit':
            break
        await execute_request(cmd)


def list_requests():
    return '\n'.join([n.__name__ for n in REQUESTS])


@request
async def get_state(env, session):
    async with session.get(f'{env["url"]}/config/state') as response:
        print_response(response)


async def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='\n'.join([n.__name__ for n in REQUESTS])
    )
    parser.add_argument('cmd', nargs='?', help='Name of a request to execute')
    args = parser.parse_args()
    if args.cmd:
        await execute_request(args.cmd)
    else:
        await interactive_mode()


if __name__ == '__main__':
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print('')
