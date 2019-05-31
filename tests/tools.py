import re
from dbgr.tools import uuid4


def test_uuid4():
    uuids = set()
    regex = re.compile(r'^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}$', re.I)
    for i in range(1000):
        uuid = uuid4()
        assert bool(regex.match(uuid))
        assert uuid not in uuids
        uuids.add(uuid)
