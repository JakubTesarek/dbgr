import asyncio
import aiohttp
import json
import requests
import functools
import argparse

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
    print(f'status: {response.status_code}')
    print(f'time: {response.elapsed}')
    print(f'content: {response.raw}')

    for name, value in response.headers.items():
        print(f'{name}: {value}')


async def execute_request(cmd):
    for request in REQUESTS:
        if request.__name__ == cmd:
            await request(ENV)


async def interactive_mode():
    while True:
        cmd = input('> ')
        if not cmd or cmd == 'exit':
            break
        await execute_request(cmd)


def list_requests():
    return '\n'.join([n.__name__ for n in REQUESTS])


@request
async def get_state(env):
    response = requests.get(f'{env["url"]}/config/state')
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
