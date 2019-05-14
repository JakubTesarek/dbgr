import aiohttp
import asyncio
import colorama
from datetime import datetime, timedelta
from itertools import cycle


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
        return tracer

    async def report_request_finished(self, session, trace_config_ctx, params):
        colorama.init(autoreset=True)
        response = params.response
        print(f'< {response.method} {response.url}')
        print(f'< {response.status} {response.reason}')
        print('< Headers:')
        for name, value in response.headers.items():
            print(f'<  {name}: {value}')
