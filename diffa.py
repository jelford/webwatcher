from hashlib import sha256
import subprocess

from filehash import file_hash
from observation import PageObservation


class ComparisonFailureException(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg


class PageDiff:
    def __init__(self,
                 availability: bool=None,
                 screenshot_diff=None,
                 content_diff=None) -> None:
        self.availability = availability
        self.screenshot_diff = screenshot_diff
        self.content_diff = content_diff

    def differences(self):
        return {k: v for k, v in {
            'availability': self.availability,
            'screenshot': self.screenshot_diff,
            'content': self.content_diff
        }.items() if v is not None}


class ScreenshotDiff:
    def __init__(self, old, new, diff_file):
        self.old = old
        self.new = new
        self.comparison = diff_file

    def __str__(self):
        return ('ScreenshotDiff('
                'old(hash)={},'
                ' new={},'
                ' comparison={})')\
                .format(self.old, self.new, self.comparison)


def _do_diff_on_screenshots(old_screenshot, new_screenshot):
    if old_screenshot == new_screenshot:
        return None

    if old_screenshot is not None:
        old_hash = old_screenshot.content_hash
    else:
        old_hash = None

    if new_screenshot is not None:
        new_path = new_screenshot.content_path
        new_hash = file_hash(new_path).digest()
    else:
        new_path = new_hash = None

    if old_hash == new_hash:
        return None

    return ScreenshotDiff(old_hash, new_path, None)


class Diffa:
    def diff(self,
             new_observation: PageObservation,
             old_observation: PageObservation) -> PageDiff:

        if old_observation is None:
            print('No previous found')
            return PageDiff(
                    availability=new_observation.availability,
                    screenshot_diff=new_observation.screenshot,
                    content_diff=new_observation.raw_content_location)

        availability = new_observation.availability \
            if (new_observation.availability != old_observation.availability) \
            else None

        screenshot_diff = _do_diff_on_screenshots(
                            old_observation.screenshot, 
                            new_observation.screenshot)

        d = PageDiff(
            availability=availability,
            screenshot_diff=screenshot_diff,
            content_diff=None)

        return d if d.differences() else None

