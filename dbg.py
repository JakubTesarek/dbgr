import requests


def print_response(response):
    print(f'status: {response.status_code}')
    print(f'time: {response.elapsed}')
    print(f'content: {response.raw}')

    for name, value in response.headers.items():
        print(f'{name}: {value}')


def get_state(env):
    response = requests.get(f'{env["url"]}/config/state')
    print_response(response)


if __name__ == '__main__':
    env = {
        'url': 'http://127.0.0.1:9777'
    }
    get_state(env)
