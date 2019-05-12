import json
import requests
import functools
import argparse

REQUESTS = set()
with open('conf.env.json', 'r') as f:
    ENV = json.load(f)


def request(request):
    @functools.wraps(request)
    def wrapper_decorator(*args, **kwargs):
        request(*args, **kwargs)
    REQUESTS.add(wrapper_decorator)
    return wrapper_decorator


def print_response(response):
    print(f'status: {response.status_code}')
    print(f'time: {response.elapsed}')
    print(f'content: {response.raw}')

    for name, value in response.headers.items():
        print(f'{name}: {value}')


def execute_request(cmd):
    for request in REQUESTS:
        if request.__name__ == cmd:
            return request(ENV)


def interactive_mode():
    while True:
        cmd = input('> ')
        if not cmd or cmd == 'exit':
            break
        execute_request(cmd)


def list_requests():
    return '\n'.join([n.__name__ for n in REQUESTS])


@request
def get_state(env):
    response = requests.get(f'{env["url"]}/config/state')
    print_response(response)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='\n'.join([n.__name__ for n in REQUESTS])
    )
    parser.add_argument('cmd', nargs='?', help='Name of a request to execute')
    args = parser.parse_args()
    if args.cmd:
        execute_request(args.cmd)
    else:
        interactive_mode()


if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        print('')
