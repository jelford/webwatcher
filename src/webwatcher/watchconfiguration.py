
import logging
import os
from pathlib import Path
import pkgutil
import sys
from typing import Collection, Optional, Dict, Iterable, Union

import toml


_CONFIG_PATH_ENV_VAR = 'WEBWATCHER_CONFIG_PATH'


class PageUnderObsevation:
    def __init__(self, url):
        self.url = url


def _if_exists_or_none(p: Optional[Union[Path, str]]) -> Optional[Path]:
    if p is None:
        return None
    p = Path(p)
    return p if p.is_file() else None


def _find_wach_confguration_path(config_path: Optional[Path]) \
        -> Optional[Path]:
    from_config = _if_exists_or_none(config_path)
    if from_config is not None:
        return from_config

    working_dir_config = _if_exists_or_none(
                            Path('.').joinpath('config.toml'))
    if working_dir_config is not None:
        return working_dir_config

    return _if_exists_or_none(os.getenv(_CONFIG_PATH_ENV_VAR))


def _config_to_page_specification(sites: Dict[str, Dict]) \
        -> Iterable[PageUnderObsevation]:

    for name, data in sites.items():
        try:
            yield PageUnderObsevation(url=data['url'])
        except:
            logging.warn('No url specified for {}', name)
            raise


def _print_err(msg: str='') -> None:
    print(msg, file=sys.stderr)


def print_config_template() -> None:
    print(
        pkgutil.get_data('webwatcher', 'config.toml.template').decode('utf-8'))


def watched_pages(config_path: Optional[Path]) \
        -> Iterable[PageUnderObsevation]:
    watch_config_path = _find_wach_confguration_path(config_path)
    if watch_config_path:
        config = toml.load(str(watch_config_path))
        try:
            sites = config['site']
        except KeyError:
            logging.warn(
                'Found a configuration file at {} but no sites were specified',
                watch_config_path)
            raise
        return _config_to_page_specification(sites)
    else:
        _print_err("Hey there! I see you're trying to use webwatcher (yay! ♥)")
        _print_err("However (uh oh! 🤔) it looks like I don't have any ")
        _print_err("configuration about what sites you'd like to look at. ")
        _print_err("Don't worry, we can totally fix this (🦄) - I just need ")
        _print_err("you to plonk down a configuration file.")
        _print_err("You have bare options:")
        _print_err("* on the command line with --config=<some file>")
        _print_err(
            "* put a file called `config.toml` in the current directory")
        _print_err("* tell me a path as an environment variable "
                   "(WEBWATCHER_CONFIG_PATH)")
        _print_err("To see a sample configuration file, re-run with:")
        _print_err("\twebwatcher --show-config-template")
        _print_err()
        return None
