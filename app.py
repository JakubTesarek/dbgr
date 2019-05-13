import asyncio
import aiohttp
import json
import requests
import functools
import argparse
from dbg.progress_bar import ProgressBar
from dbg.reporting import get_request_finish_tracer


REQUESTS = set()
with open('conf.env.json', 'r') as f:
    ENV = json.load(f)


def request(request):
    @functools.wraps(request)
    async def wrapper_decorator(*args, **kwargs):
        await request(*args, **kwargs)
    REQUESTS.add(wrapper_decorator)
    return wrapper_decorator


async def execute_request(cmd):
    for request in REQUESTS:
        if request.__name__ == cmd:
            progress_bar = ProgressBar()
            async with aiohttp.ClientSession(trace_configs=[
                progress_bar.get_tracer(),
                get_request_finish_tracer()
            ]) as session:
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
    await session.get(f'{env["url"]}/config/state')


@request
async def slow_response(env, session):
    await session.get(f'http://slowwly.robertomurray.co.uk/delay/1000/url/http://slowwly.robertomurray.co.uk/delay/3000/url/http://www.google.co.uk')


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
