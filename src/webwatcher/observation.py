from datetime import datetime


class Screenshot:
    def __init__(self, content_hash, content_path=None):
        self.content_hash = content_hash
        self.content_path = content_path

    def __hash__(self):
        return hash(self.content_hash)

    def __eq__(self, other):
        try:
            return self.content_hash == other.content_hash
        except AttributeError:
            return False

    def __str__(self):
        return 'Screenshot{{hash={hash}}}'.format(hash=self.content_hash)


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
        artefacts = dict()
        if self.screenshot is not None:
            artefacts['screenshot'] = self.screenshot.content_path
        if self.raw_content_location is not None:
            artefacts['raw_content'] = self.raw_content_location

        return artefacts

    def get_meta_info(self):
        meta = {
            'type': 'observation',
            'url': self.url,
            'timestamp': self.observation_time,
            'was_available': self.availability,
        }
        if self.screenshot:
            meta['screenshot_content'] = self.screenshot.content_hash
        return meta
