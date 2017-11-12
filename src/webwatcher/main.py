"""
webwatcher

Usage:
    webwatcher [--config=<config>]
    webwatcher --show-config-template

Options:
    --config=<config>           Specify a path to a configuration file that 
                                tells webwatcher which parts of the web to 
                                watch
    --show-config-template      Print out a sample configuration file

"""

from typing import Collection

from datetime import datetime, timezone
import functools
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import Iterable

import docopt
import requests
from requests.exceptions import ConnectionError

from webwatcher.diffa import Diffa
from webwatcher.observation import PageObservation, Screenshot
from webwatcher.screenshotter import Screenshotter
from webwatcher.storage import Storage
from webwatcher.temporarystorage import temporary_storage
from webwatcher.webfetcher import WebFetcher
from webwatcher.watchconfiguration import \
    PageUnderObsevation, watched_pages, print_config_template


def get_previous_observation(storage: Storage, page: PageUnderObsevation) \
        -> PageObservation:
    persisted_data = storage.find(url=page.url) \
        .having('timestamp') \
        .order_by('timestamp',
                  desc=True) \
        .fetch()
    if not persisted_data:
        return None
    else:
        persisted_data = persisted_data[0]

    screenshot_content_hash = persisted_data['screenshot_content']
    if screenshot_content_hash is not None:
        screenshot = Screenshot(content_hash=screenshot_content_hash)
    else:
        screenshot = None

    return PageObservation(
        url=persisted_data['url'],
        observation_time=persisted_data['timestamp'],
        availability=persisted_data['was_available'],
        screenshot=screenshot,
        raw_content_location=persisted_data.fetch_local('raw_content')
    )


class Observer:
    def __init__(self, screenshotter, webfetcher):
        self.screenshotter = screenshotter
        self.webfetcher = webfetcher

    def observe(self, page: PageUnderObsevation) -> PageObservation:
        was_available, raw_content = self.webfetcher.fetch(page.url)
        screenshot = self.screenshotter.take_screenshot_of(page.url)

        return PageObservation(
            url=page.url,
            observation_time=datetime.now(timezone.utc),
            availability=was_available,
            screenshot=screenshot,
            raw_content_location=raw_content)


def _raise_first(errors: Iterable[Exception]):
    for e in errors:
        raise e


def observe_the_web(
        diffa: Diffa,
        storage: Storage,
        watcher: Observer,
        under_observation: Iterable[PageUnderObsevation]) -> None:

    diffs = dict()
    errors = dict()

    for page in under_observation:
        try:
            observation = watcher.observe(page)
            previous_observation = get_previous_observation(storage, page)
            diff = diffa.diff(observation, previous_observation)
            if diff:
                diffs[page.url] = diff
            storage.persist(observation)
        except Exception as ex:
            errors[page.url] = ex

    for url, diff in diffs.items():
        print('Differences in {url}'.format(url=url))
        for k, v in diff.differences().items():
            print('\t{k}: {v}'.format(**locals()))

    if errors:
        print('Errors:')
    for url, e in errors.items():
        print('While inspecting', url)
        print('\t {type} {args}'.format(type=type(e), args=e.args))
    _raise_first(errors.values())


def run_web_watcher(config_file) -> None:
    with temporary_storage() as temp_storage:
        diffa = Diffa()
        storage = Storage()
        screenshotter = Screenshotter(temp_storage)
        fetcher = WebFetcher(temp_storage)
        watcher = Observer(screenshotter, fetcher)

        under_observation = watched_pages(config_file)
        if under_observation is None:
            sys.exit(1)

        observe_the_web(
            diffa,
            storage,
            watcher,
            under_observation)


def main() -> None:
    args = docopt.docopt(__doc__)
    if args['--show-config-template']:
        print_config_template()
        sys.exit(0)
    else:
        run_web_watcher(config_file=args['--config'])


if __name__ == '__main__':
    main()
