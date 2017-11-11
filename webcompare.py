from typing import Collection

from datetime import datetime, timezone
import functools
import os
import re
import shutil
import subprocess
import tarfile
import tempfile

import attr
import requests
from requests.exceptions import ConnectionError

from diffa import Diffa
from observation import PageObservation, Screenshot
from screenshotter import Screenshotter
from storage import Storage
from webfetcher import WebFetcher


class PageUnderObsevation:
    def __init__(self, url):
        self.url = url


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

    screenshot_path = persisted_data.fetch_local('screenshot')
    screenshot = Screenshot(screenshot_path) \
        if screenshot_path is not None else None

    return PageObservation(
        url=persisted_data['url'],
        observation_time=persisted_data['timestamp'],
        availability=persisted_data['was_available'],
        screenshot=screenshot,
        raw_content_location=persisted_data.fetch_local('raw_content')
    )


class WebWatcher:
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


def watched_pages() -> Collection[PageUnderObsevation]:
    return [PageUnderObsevation(url=u) for u in
            (
                'https://google.com',
                'http://icanhazip.com',
                'http://localhost:8080',
    )]


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        diffa = Diffa()
        storage = Storage()
        screenshotter = Screenshotter(temp_dir)
        fetcher = WebFetcher(temp_dir)
        watcher = WebWatcher(screenshotter, fetcher)
        diffs = dict()
        errors = []
        for page in watched_pages():
            try:
                observation = watcher.observe(page)
                previous_observation = get_previous_observation(storage, page)
                diff = diffa.diff(observation, previous_observation)
                if diff:
                    diffs[page.url] = diff
                storage.persist(observation)
            except Exception as ex:
                msg = getattr(ex, 'msg', str(type(ex)))
                errors.append(
                    ('{} while checking on {}'.format(msg, page.url), ex))

        for url, diff in diffs.items():
            print('Differences in {url}'.format(url=url))
            for k, v in diff.differences().items():
                print('\t{k}: {v}'.format(**locals()))

        if errors:
            print('Errors:')
        for msg, e in errors:
            print('\t', msg)
            raise e

if __name__ == '__main__':
    main()
