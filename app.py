import asyncio
import functools
import argparse
from dbgr.configuration import Configuration
from dbgr.session import get_session


REQUESTS = set()


def request(request):
    @functools.wraps(request)
    async def wrapper_decorator(*args, **kwargs):
        await request(*args, **kwargs)
    REQUESTS.add(wrapper_decorator)
    return wrapper_decorator


async def execute_request(cmd, configuration):
    for request in REQUESTS:
        if request.__name__ == cmd:
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


@request
async def get_state(conf, session):
    await session.get(f'{conf["url"]}/config/state')


@request
async def slow_response(conf, session):
    await session.get(f'http://slowwly.robertomurray.co.uk/delay/1000/url/http://slowwly.robertomurray.co.uk/delay/3000/url/http://www.google.co.uk')


@request
async def google(conf, session):
    await session.get(f'http://google.com')


async def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='\n'.join([n.__name__ for n in REQUESTS])
    )
    parser.add_argument('cmd', nargs='?', help='Name of a request to execute')
    args = parser.parse_args()
    configuration = Configuration('conf/conf.env.json')
    if args.cmd:
        await execute_request(args.cmd, configuration)
    else:
        await interactive_mode(configuration)


if __name__ == '__main__':
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print('')
