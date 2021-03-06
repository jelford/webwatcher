
import requests
from requests.exceptions import ConnectionError
import shutil
import tempfile

from webwatcher.http_session import http_session


class WebFetcher:
    def __init__(self, temp):
        self._temp = temp

    def fetch(self, url):
        try:
            response = http_session.get(url, stream=True)
        except ConnectionError:
            return False, None
        else:
            was_available = response.status_code in range(200, 300)
            raw_content_file = self._temp.new_file(delete=False)
            shutil.copyfileobj(response.raw, raw_content_file)
            raw_content_file.flush()
            return True, raw_content_file.name
