import functools
import os
import re
import shutil
import subprocess
import tempfile

import attr
import requests

from observation import Screenshot


_FIREFOX_BETA_DOWNLOAD_URL = \
    'https://ftp.mozilla.org/pub/firefox/releases/' \
    '57.0b14/linux-x86_64/en-US/firefox-57.0b14.tar.bz2'


def take_screenshot_of(url: str) -> Screenshot:
    with tempfile.TemporaryDirectory() as profile_dir:
        output = tempfile.NamedTemporaryFile(
            delete=False, suffix='_screenshot.png')
        output.close()
        ff_path = _path_to_modern_firefox()
        try:
            subprocess.check_call(
                [
                    ff_path,
                    '--screenshot',
                    output.name,
                    url,
                    '--no-remote',
                    '--profile',
                    profile_dir
                ],
                stdout=None,
                stderr=None,
                timeout=2
            )
        except subprocess.TimeoutExpired:
            return None
    return Screenshot(path=output.name)


def _download_firefox_package():
    webwatcher_cache_dir = os.path.join(
        os.path.expanduser('~'),
        '.cache',
        'webwatcher')
    extracted_firefox_bin = os.path.join(webwatcher_cache_dir,
                                         'firefox',
                                         'firefox')

    if os.path.isfile(extracted_firefox_bin):
        if os.access(extracted_firefox_bin, os.X_OK):
            return extracted_firefox_bin

    download_cache_dir = os.path.join(
        webwatcher_cache_dir,
        'downloads')
    try:
        os.makedirs(download_cache_dir)
    except FileExistsError:
        pass

    download_path = os.path.join(download_cache_dir, 'firefox.tar.bz2')

    if not os.path.exists(download_path):
        firefox_download_url = os.getenv('FIREFOX_DOWNLOAD_URL') or \
            _FIREFOX_BETA_DOWNLOAD_URL
        with open(download_path, 'wb') as download_file:
            with http_session.get(firefox_download_url, stream=True) as r:
                shutil.copyfileobj(r.raw, download_file)

    downloaded_package = tarfile.open(name=download_path, mode='r:bz2')
    downloaded_package.extractall(path=webwatcher_cache_dir)

    return extracted_firefox_bin


@functools.lru_cache()
def _path_to_modern_firefox() -> str:
    ff_path = shutil.which('firefox')
    if ff_path:
        version_text = subprocess.check_output([ff_path, '--version'])
        vnumber = re.search(b'Mozilla Firefox ([\.\d]+)', version_text)
        if vnumber:
            version = vnumber.group(1)
            parsed_version_info = version.split(b'.')
            if parsed_version_info >= [b'57', b'0']:
                return ff_path

    return _download_firefox_package()
