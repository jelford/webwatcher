import functools
import logging
import os
import re
import shutil
import subprocess
import tarfile
import tempfile

import attr
import requests

from webwatcher.environment import cache_folder
from webwatcher.filehash import file_hash
from webwatcher.http_session import http_session
from webwatcher.observation import Screenshot


_FIREFOX_BETA_DOWNLOAD_URL = \
    'https://ftp.mozilla.org/pub/firefox/releases/' \
    '57.0b14/linux-x86_64/en-US/firefox-57.0b14.tar.bz2'
_FIREFOX_BETA_DOWNLOAD_HASH = \
    '772c307edcbdab9ba9bf652c44b69b6c014b831f28cf91a958de67ea6d42ba5f'


class Screenshotter:
    def __init__(self, temp_dir):
        self.temp_dir = temp_dir

    def take_screenshot_of(self, url: str) -> Screenshot:
        output = tempfile.NamedTemporaryFile(
            suffix='.png', dir=self.temp_dir, delete=False)
        output.close()

        ff_path = _path_to_modern_firefox()
        with tempfile.TemporaryDirectory(suffix='_ff_profile') as profile_dir:
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
            except:
                logging.warn('Error while calling to firefox at: {}', ff_path)
                raise

        return Screenshot(
            content_hash=file_hash(output.name).hexdigest(),
            content_path=output.name)


def _download_firefox_package():
    firefox_extraction_path = cache_folder('firefox')
    extracted_firefox_bin = firefox_extraction_path / 'firefox' / 'firefox'

    if extracted_firefox_bin.is_file():
        if os.access(extracted_firefox_bin, os.X_OK):
            return extracted_firefox_bin

    download_cache_dir = cache_folder('downloads')
    try:
        os.makedirs(download_cache_dir)
    except FileExistsError:
        pass

    download_path = download_cache_dir / 'firefox.tar.bz2'

    if download_path.exists():
        downloaded_hash = file_hash(download_path).hexdigest()
        need_to_download = downloaded_hash != _FIREFOX_BETA_DOWNLOAD_HASH
    else:
        logging.debug('Need to download firefox as the following'
                      'arent present or dont hash right:',
                      download_path, extracted_firefox_bin)

        need_to_download = True

    if need_to_download:
        firefox_download_url = os.getenv('FIREFOX_DOWNLOAD_URL') or \
            _FIREFOX_BETA_DOWNLOAD_URL
        with open(download_path, 'wb') as download_file:
            with http_session.get(firefox_download_url, stream=True) as r:
                shutil.copyfileobj(r.raw, download_file)

    downloaded_package = tarfile.open(name=download_path, mode='r:bz2')
    downloaded_package.extractall(path=firefox_extraction_path)

    return extracted_firefox_bin


@functools.lru_cache()
def _path_to_modern_firefox() -> str:
    ff_path = shutil.which('firefox')
    if ff_path:
        try:
            version_text = \
                subprocess.check_output([ff_path, '--version'], timeout=1)
        except:
            pass
        else:
            vnumber = re.search(b'Mozilla Firefox ([\.\d]+)', version_text)
            if vnumber:
                version = vnumber.group(1)
                parsed_version_info = version.split(b'.')
                if parsed_version_info >= [b'57', b'0']:
                    return ff_path

    return _download_firefox_package()
