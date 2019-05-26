import asyncio
import json
from datetime import datetime
from itertools import cycle
import aiohttp
from pygments import highlight
from pygments.lexers import JsonLexer, XmlLexer # pylint: disable=E0611
from pygments.formatters import TerminalFormatter # pylint: disable=E0611
from colorama import Style, Fore


class ProgressBar():
    def __init__(self):
        self.message = ''

    def start(self):
        asyncio.ensure_future(self.render())

    async def render(self):
        start = datetime.now()
        for symbol in cycle(['\\', '-', '/', '|']):
            elapsed = datetime.now() - start
            print(f'{self.message} {symbol} [{elapsed}]', end='\r')
            await asyncio.sleep(0.1)

    async def on_request_start(self, session, trace_ctx, params): # pylint: disable=W0613
        self.message = 'request send'
        self.start()

    async def on_request_redirect(self, session, trace_ctx, params): # pylint: disable=W0613
        self.message = 'redirecting'

    async def on_request_end(self, session, trace_ctx, params): # pylint: disable=W0613
        print('', end='\r')

    def get_tracer(self):
        tracer = aiohttp.TraceConfig()
        tracer.on_request_start.append(self.on_request_start)
        tracer.on_request_end.append(self.on_request_end)
        tracer.on_request_redirect.append(self.on_request_redirect)
        return tracer


class Reporter():
    def get_tracer(self):
        tracer = aiohttp.TraceConfig()
        tracer.on_request_end.append(self.report_request_finished)
        tracer.on_request_redirect.append(self.on_request_redirect)
        return tracer

    async def print_request(self, response):
        print(f'{Style.DIM}>{Style.RESET_ALL} {Style.BRIGHT}{response.method} {response.url}')

    async def print_info(self, response):
        if response.status < 400:
            color = Fore.GREEN
        else:
            color = Fore.RED
        print(f'{Style.DIM}<{Style.RESET_ALL} {color}{response.status} {response.reason}')

    async def print_headers(self, response):
        print(f'{Style.DIM}<')
        print(f'{Style.DIM}<{Style.RESET_ALL} {Style.BRIGHT}Headers:')
        for name, value in response.headers.items():
            print(f'{Style.DIM}<{Style.RESET_ALL}  {name}: {value}')

    async def print_response(self, response):
        print(f'{Style.DIM}<')
        print(
            f'{Style.DIM}<{Style.RESET_ALL} {Style.BRIGHT}Content{Style.RESET_ALL}'
            f'{Style.DIM}({response.headers["Content-Type"]}){Style.RESET_ALL}:'
        )
        if 'application/json' in response.headers['Content-Type']:
            output = json.dumps(await response.json(), sort_keys=True, indent=2)
            print(highlight(output, JsonLexer(), TerminalFormatter()))
        elif 'application/xml' in response.headers['Content-Type']:
            output = await response.text()
            print(highlight(output, XmlLexer(), TerminalFormatter()))
        elif 'text/plain' in response.headers['Content-Type']:
            output = await response.text()
            print(output)


    async def report_request_finished(self, session, trace_ctx, params): # pylint: disable=W0613
        response = params.response
        await self.print_request(response)
        await self.print_info(response)
        await self.print_headers(response)
        await self.print_response(response)

    async def on_request_redirect(self, session, trace_ctx, params): # pylint: disable=W0613
        print(f'Redirect -> {params.url}')
