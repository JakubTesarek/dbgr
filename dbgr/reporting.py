import asyncio
import json
from datetime import datetime
from itertools import cycle
import cgi
import aiohttp
from pygments import highlight
from pygments.lexers import JsonLexer, XmlLexer, HtmlLexer # pylint: disable=E0611
from pygments.formatters import TerminalFormatter # pylint: disable=E0611
from colorama import Style, Fore


class ProgressBar():
    def __init__(self):
        self.message = ''
        self.running = False
        self.message_length = 0

    def start(self):
        self.running = True
        asyncio.ensure_future(self.render())

    def stop(self):
        self.running = False

    async def render(self):
        start = datetime.now()
        for symbol in cycle(['\\', '-', '/', '|']):# pragma: no cover
            if not self.running:
                return
            elapsed = datetime.now() - start
            message = f'\r{self.message} {symbol} [{elapsed}]'
            self.message_length = len(message)
            print(message, end='')
            await asyncio.sleep(0.1)

    async def on_request_start(self, session, trace_ctx, params): # pylint: disable=W0613
        self.message = 'request send'
        self.start()

    async def on_request_redirect(self, session, trace_ctx, params): # pylint: disable=W0613
        self.message = 'redirecting'

    async def on_request_end(self, session, trace_ctx, params): # pylint: disable=W0613
        self.stop()
        print(f'\r{" "*self.message_length}', end='\r')

    def get_tracer(self):
        tracer = aiohttp.TraceConfig()
        tracer.on_request_start.append(self.on_request_start)
        tracer.on_request_end.append(self.on_request_end)
        tracer.on_request_redirect.append(self.on_request_redirect)
        return tracer


class Reporter():
    def get_tracer(self):
        tracer = aiohttp.TraceConfig()
        tracer.on_request_end.append(self.on_request_end)
        return tracer

    def p_out(self, text='', indent=0):
        print(f'{Style.DIM}>{Style.RESET_ALL}{" "*(indent+1)}{text}'.strip())

    def p_in(self, text='', indent=0):
        print(f'{Style.DIM}<{Style.RESET_ALL}{" "*(indent+1)}{text}'.strip())

    def p_in_h1(self, text, sup=None, indent=0):
        if sup:
            self.p_in(
                f'{Fore.YELLOW}{text}{Style.RESET_ALL} {Style.DIM}({sup}){Style.RESET_ALL}:',
                indent=indent
            )
        else:
            self.p_in(f'{Fore.YELLOW}{text}:', indent=indent)

    def p_out_h1(self, text, sup=None, indent=0):
        if sup:
            self.p_out(
                f'{Fore.YELLOW}{text}{Style.RESET_ALL} {Style.DIM}({sup}){Style.RESET_ALL}:',
                indent=indent
            )
        else:
            self.p_out(f'{Fore.YELLOW}{text}:', indent=indent)

    def p_out_h2(self, text, sup):
        self.p_out(
            f'{Style.BRIGHT}{text} {Style.RESET_ALL}{Style.DIM}({sup}){Style.RESET_ALL}:',
            indent=1
        )

    def p_json(self, json_data):
        output = json.dumps(json_data, sort_keys=True, indent=2)
        print(highlight(output, JsonLexer(), TerminalFormatter()).strip())

    def p_xml(self, xml_data):
        print(highlight(xml_data, XmlLexer(), TerminalFormatter()).strip())

    def p_html(self, html_data):
        print(highlight(html_data, HtmlLexer(), TerminalFormatter()).strip())

    def p_text(self, text_data):
        print(text_data)

    async def print_request(self, response):
        self.p_out(f'{Style.BRIGHT}{response.method} {response.url}')

    async def print_info(self, response):
        if response.status < 400:
            color = Fore.GREEN
        else:
            color = Fore.RED
        self.p_out(f'{color}{response.status} {response.reason}')

    async def print_response_headers(self, response):
        self.p_in()
        self.p_in_h1('Response headers')
        for name, value in response.headers.items():
            self.p_in(f'{name}: {value}', indent=1)

    async def print_response(self, response):
        self.p_in()
        self.p_in_h1(f'Response data', sup=response.headers["Content-Type"])
        if 'application/json' in response.headers['Content-Type']:
            self.p_json(await response.json())
        elif 'application/xml' in response.headers['Content-Type']:
            self.p_xml(await response.text())
        elif 'text/plain' in response.headers['Content-Type']:
            self.p_text(await response.text())
        elif 'text/html' in response.headers['Content-Type']:
            self.p_html(await response.text())
        else:
            self.p_text(await response.text())

    async def print_request_headers(self, response):
        self.p_out()
        self.p_out_h1('Request headers')
        for name, value in response.request_info.headers.items():
            self.p_out(f'{name}: {value}', indent=1)

    def get_part_name(self, part):
        _, params = cgi.parse_header(part.headers['content-disposition'])
        return params.get('name', '# Part')

    async def print_request_data(self, response, request_context):
        if hasattr(request_context, 'json') or hasattr(request_context, 'data'):
            self.p_out()
            self.p_out_h1('Request data', sup=response.request_info.headers['content-type'])
        if hasattr(request_context, 'json'):
            self.p_json(request_context.json)
        elif hasattr(request_context, 'data') and request_context.data:
            data = request_context.data
            if isinstance(data, aiohttp.multipart.MultipartWriter):
                for part, _, __ in data:
                    self.p_out_h2(self.get_part_name(part), sup=part.content_type)
                    if part.filename:
                        self.p_out(f'- Filename: {part.filename}', indent=1)
                    if part.encoding:
                        self.p_out(f'- Encoding: {part.encoding}', indent=1)
                    self.p_out(f'- Size: {part.size}B', indent=1)
                    self.p_out(f'- Headers:', indent=1)
                    for key, value in part.headers.items():
                        self.p_out(f'{key}: {value}', indent=4)
                    self.p_out(f'- Content:', indent=1)
                    if isinstance(part, aiohttp.payload.JsonPayload):
                        self.p_json(json.loads(part._value))
                    elif isinstance(part, aiohttp.payload.BufferedReaderPayload):
                        print(f'{Style.DIM}Contents of "{part._value.name}"')
                    else:
                        self.p_text(part._value)
            else:
                self.p_text(request_context.data)

    async def on_request_end(self, session, trace_ctx, params): # pylint: disable=W0613
        response = params.response
        await self.print_request(response)
        await self.print_info(response)
        await self.print_request_headers(response)
        await self.print_request_data(response, trace_ctx.trace_request_ctx)
        await self.print_response_headers(response)
        await self.print_response(response)
