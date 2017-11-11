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
from screenshotter import take_screenshot_of
from storage import Storage

http_session = requests.session()

storage = Storage()


class PageUnderObsevation:
    def __init__(self, url):
        self.url = url


def get_previous_observation(page: PageUnderObsevation) -> PageObservation:
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


def observe(page: PageUnderObsevation) -> PageObservation:
    try:
        response = http_session.get(page.url, stream=True)
    except ConnectionError:
        raw_content = None
        was_available = False
    else:
        was_available = response.status_code in range(200, 300)
        raw_content_file = tempfile.NamedTemporaryFile(delete=False)
        shutil.copyfileobj(response.raw, raw_content_file)
        raw_content = raw_content_file.name

    screenshot = take_screenshot_of(page.url)

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
                'http://localhost:8080'
    )]


def main() -> None:
    diffa = Diffa()
    diffs = dict()
    errors = []
    for page in watched_pages():
        try:
            observation = observe(page)
            previous_observation = get_previous_observation(page)
            diff = diffa.diff(observation, previous_observation)
            if diff:
                diffs[page.url] = diff
            storage.persist(observation)
        except Exception as ex:
            msg = getattr(ex, 'msg', str(type(ex)))
            errors.append(f'{msg} while checking on {page.url}')

    for url, diff in diffs.items():
        print('Differences in {url}'.format(url=url))
        for k, v in diff.differences().items():
            print('\t{k}: {v}'.format(**locals()))

    if errors:
        print('Errors:')
    for e in errors:
        print('\t', e)

if __name__ == '__main__':
    main()
