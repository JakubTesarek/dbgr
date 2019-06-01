import aiohttp
from dbgr.reporting import ProgressBar, Reporter


_SESSION = None


def get_session():
    global _SESSION # pylint: disable=W0603
    if not _SESSION:
        progress_bar = ProgressBar()
        reporter = Reporter()
        _SESSION = aiohttp.ClientSession(
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
