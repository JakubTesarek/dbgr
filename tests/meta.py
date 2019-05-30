import re
from dbgr.meta import __version__


def test_version_format():
    assert re.match('^[1-9]\.(0|([1-9]\d*))\.(0|([1-9]\d*))$', __version__)
