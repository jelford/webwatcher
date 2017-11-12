""" 
environment.py - contains methods for interacting with local
environment, e.g. local cache dirs, state directories, ...
"""
import functools
import os
from pathlib import Path
import tempfile
from typing import Callable

import appdirs

from __version__ import version


def cache_folder(name) -> Path:
    d = _cache_root() / name
    _ensure_exists(d)
    return d


def data_folder(name) -> Path:
    d = _data_root() / name
    _ensure_exists(d)
    return d


def _ensure_exists(folder: Path) -> None:
    try:
        os.makedirs(folder)
    except FileExistsError:
        if folder.is_dir():
            return
        raise


@functools.lru_cache()
def _appdir_with_override(
        env_var_name: str,
        default_app_dir: str) -> Path:

    user_supplied_path = \
        os.getenv('WEBWATCHER_{env_var_name}'.format(**locals()))

    if user_supplied_path:
        root = Path(user_supplied_path)
    else:
        root = Path(default_app_dir)

    try:
        _ensure_exists(root)
    except:
        root = Path(tempfile.gettempdir()) / 'webwatcher'
        _ensure_exists(root)

    return root


def _data_root() -> Path:
    r = _appdir_with_override('DATA_ROOT', appdirs.user_data_dir('webwatcher'))
    print('Setting up data root:', r)
    return r


def _cache_root() -> Path:
    return _appdir_with_override('CACHE_ROOT',
                                    appdirs.user_cache_dir('webwatcher'))
