import aiohttp
from dbgr.reporting import ProgressBar, Reporter


def get_session():
    progress_bar = ProgressBar()
    reporter = Reporter()
    return aiohttp.ClientSession(
        trace_configs=[
            progress_bar.get_tracer(),
            reporter.get_tracer()
        ]
    )
