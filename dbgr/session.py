from types import SimpleNamespace
import aiohttp
from dbgr.reporting import ProgressBar, Reporter


_SESSION = None


class Session(aiohttp.ClientSession):
    async def _request(self, method, url, **kwargs): #pylint: disable=W0221
        kwargs['trace_request_ctx'] = SimpleNamespace(method=method, url=url, **kwargs)
        return await super()._request(method, url, **kwargs)


def get_session():
    global _SESSION # pylint: disable=W0603
    if not _SESSION:
        progress_bar = ProgressBar()
        reporter = Reporter()
        _SESSION = Session(
            trace_configs=[
                progress_bar.get_tracer(),
                reporter.get_tracer()
            ]
        )
    return _SESSION


async def close_session():
    global _SESSION # pylint: disable=W0603
    if _SESSION:
        await _SESSION.close()
