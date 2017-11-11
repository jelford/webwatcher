
from typing import Collection, Dict
from typing_extensions import Protocol

import base64
from datetime import datetime, date
from hashlib import blake2b
import json
import os
from pathlib import Path
import shutil
from urllib.parse import urlparse, unquote
import uuid


class LocalFile(Protocol):
    def get_url(self) -> str:
        ...


class Persistable(Protocol):
    def artefacts(self) -> Dict[str, str]:
        ...

    def get_meta_info(self) -> Dict[str, object]:
        ...


class Storage:
    _storage_dir = Path.home() / '.local' / 'webwatcher' / 'storage'
    _meta_info_path = _storage_dir / 'record.dat'
    _artefact_storage_dir = _storage_dir / 'artefacts'

    def persist(self, persistable: Persistable):
        try:
            os.makedirs(self._artefact_storage_dir)
        except FileExistsError:
            pass

        persisted_locations = dict()
        for name, location in persistable.artefacts().items():
            storage_filename = _storage_filename_for(location)
            storage_location = self._artefact_storage_dir / storage_filename

            shutil.move(location, storage_location)
            persisted_locations[name] = storage_location.as_uri()

        meta_info = _json_safe(persistable.get_meta_info())
        if persisted_locations:
            meta_info['_storage'] = persisted_locations

        with open(self._meta_info_path, mode='a', encoding='utf-8') as f:
            f.write(json.dumps(meta_info))
            f.write('\n')

    def find(self, **kwargs):
        return StorageQuery(self, kwargs)


class FromPersistence:
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data.get(key)

    def fetch_local(self, key):
        if '_storage' not in self.data:
            return None
        elif key not in self.data['_storage']:
            return None

        storage_url = self.data['_storage'][key]
        local_path = urlparse(storage_url).path
        return unquote(local_path)


class StorageQuery:
    def __init__(self, backing_storage, filter_args):
        self.storage = backing_storage
        self.filter_args = filter_args
        self.required_fields = []
        self.order_fields = []

    def having(self, *args):
        self.required_fields = args
        return self

    def order_by(self, *order_fields, desc=False):
        self.order_fields = order_fields
        self.desc = desc
        return self

    def fetch(self):
        try:
            all_data = []
            with open(self.storage._meta_info_path, 'r', encoding='utf-8') as f:
                for line in f:
                    all_data.append(_de_jsonsafe(json.loads(line)))
        except FileNotFoundError:
            return []

        filtered = [d for d in all_data
                    if _filter_match(self.filter_args, d) and
                    all(required in d for required in self.required_fields)]

        sorted_data = sorted(filtered,
                             key=lambda d: [d[k] for k in self.order_fields],
                             reverse=self.desc)

        return [FromPersistence(d) for d in sorted_data]


_json_dateformat = '%Y-%m-%d %H:%M:%S.%f%z'


def _de_jsonsafe(jsonsafe_data) -> Dict[str, object]:
    result = dict()
    for k, v in jsonsafe_data.items():
        if isinstance(v, dict):
            if '__date' in v:
                v = datetime.strptime(v['__date'], _json_dateformat)
        result[k] = v
    return result


def _filter_match(filters, data):
    for filter_key, filter_value in filters.items():
        try:
            if data[filter_key] != filter_value:
                return False
        except KeyError:
            return False
    else:
        return True


def _json_safe(v):
    if type(v) in (str, int, float, bool):
        return v
    if isinstance(v, dict):
        return {k: _json_safe(nested_val) for k, nested_val in v.items()}

    if isinstance(v, datetime):
        return {'__date': v.strftime(_json_dateformat)}

    raise RuntimeError('Don\'t know how to jsonize: {v}'.format(v=type(v)))


def _read_file_chunks(fileobject):
    while True:
        chunk = fileobject.read(8192)
        if not chunk:
            break
        yield chunk


def _storage_filename_for(existing_file):
    if os.path.getsize(existing_file) == 0:
        return '_empty_file'

    hasher = blake2b()
    with open(existing_file, 'rb') as f:
        for chunk in _read_file_chunks(f):
            hasher.update(chunk)

    return base64.b64encode(
            hasher.digest(),
            altchars=b'_-').decode('utf-8')
