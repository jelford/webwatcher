"""
Utility for storing files on disk that are expected
to get cleaned up as part of the application lifecycle
"""
from contextlib import contextmanager
from pathlib import Path
import tempfile
from typing import IO, cast, Iterator
from typing_extensions import Protocol


class TemporaryDirectory(Protocol):
    name = None  # type: str

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, traceback):
        ...


class TemporaryStorage:
    def __init__(self, dir):
        self._dir = dir

    def new_file(self, leave_open=True, **kwargs) -> IO:

        kwargs['delete'] = kwargs.get('delete', not leave_open)
        kwargs['dir'] = kwargs.get('dir', self._dir)
        f = tempfile.NamedTemporaryFile(**kwargs)

        if not leave_open:
            f.close()
        return f

    def new_folder(self, **kwargs) -> TemporaryDirectory:
        if 'dir' in kwargs:
            return tempfile.TemporaryDirectory(**kwargs)
        else:
            d = tempfile.mkdtemp(dir=self._dir, **kwargs)
            return _AttachedTemporaryDirectory(d)


@contextmanager
def temporary_storage() -> Iterator[TemporaryStorage]:
    with tempfile.TemporaryDirectory() as d:
        temp = TemporaryStorage(dir=d)
        yield temp


class _AttachedTemporaryDirectory:
    """
    Analogous to tempfile.TemporaryDirectory, but lives under
    the root of an existing _TemporaryStorage. If used as a
    Context Manager, behaves exactly as tempfile.TemporaryDirectory
    but if __exit__ is never called, does not clean itself up
    with a finilizer (and warn) -- its cleanup will be dealt with
    by the containing _TemporaryStorage
    """

    def __init__(self, name):
        self.name = name

    def __enter__(self) -> str:
        return self.name

    def __exit__(self, *args, **kwargs):
        pass
