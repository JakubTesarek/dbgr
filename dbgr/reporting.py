import aiohttp
import asyncio
from datetime import datetime, timedelta
from itertools import cycle
from pygments import highlight, lexers, formatters
import json
from colorama import Style, Fore

class ProgressBar():
    def start(self):
        asyncio.ensure_future(self.render())

    async def render(self):
        start = datetime.now()
        for bar in cycle(['\\', '-', '/', '|']):
            elapsed = datetime.now() - start
            print(f'{self.message} {bar} [{elapsed}]', end='\r')
            await asyncio.sleep(0.1)

    async def on_request_start(self, session, trace_config_ctx, params):
        self.message = 'request send'
        self.start()

    async def on_request_redirect(self, session, trace_config_ctx, params):
        self.message = 'redirecting'

    async def on_request_end(self, session, trace_config_ctx, params):
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
        if 'application/json' in response.headers['Content-Type']:
            print(f'{Style.DIM}<')
            print(
                f'{Style.DIM}<{Style.RESET_ALL} {Style.BRIGHT}Content{Style.RESET_ALL}'
                f'{Style.DIM}(application/json){Style.RESET_ALL}:'
            )
            output = json.dumps(await response.json(), sort_keys=True, indent=2)
            print(highlight(output, lexers.JsonLexer(), formatters.TerminalFormatter()))

    async def report_request_finished(self, session, trace_config_ctx, params):
        response = params.response
        await self.print_request(response)
        await self.print_info(response)
        await self.print_headers(response)
        await self.print_response(response)

    async def on_request_redirect(self, session, trace_config_ctx, params):
        print(f'Redirect -> {params.url}')
