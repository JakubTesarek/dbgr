import aiohttp

def get_request_finish_tracer():
    tracer = aiohttp.TraceConfig()
    tracer.on_request_end.append(report_request_finished)
    return tracer


async def report_request_finished(session, trace_config_ctx, params):
    response = params.response
    print(f'{response.method} {response.url}')
    print(f'{response.status} {response.reason}')
    for name, value in response.headers.items():
        print(f'{name}: {value}')


