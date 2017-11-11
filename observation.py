from datetime import datetime

import attr


class Screenshot:
    def __init__(self, path):
        self.path = path

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        try:
            return self.path == other.path
        except AttributeError:
            return False

    def __str__(self):
        return 'Screenshot{{path={path}}}'.format(path=self.path)


class PageObservation:
    def __init__(self,
                 url: str,
                 observation_time: datetime,
                 availability: bool,
                 screenshot,
                 raw_content_location: str) -> None:
        self.url = url
        self.observation_time = observation_time
        self.availability = availability
        self.screenshot = screenshot
        self.raw_content_location = raw_content_location

    def artefacts(self):
        return {k: v for k, v in {
            'screenshot': self.screenshot.path if self.screenshot else None,
            'raw_content': self.raw_content_location
        }.items() if v is not None}

    def get_meta_info(self):
        return {
            'type': 'observation',
            'url': self.url,
            'timestamp': self.observation_time,
            'was_available': self.availability
        }
