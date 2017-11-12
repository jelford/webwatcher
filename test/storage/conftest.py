from pathlib import Path

import pytest

from webwatcher.storage import Storage


@pytest.fixture
def local_storage(tmpdir):
    return Storage(storage_root=Path(str(tmpdir)))
