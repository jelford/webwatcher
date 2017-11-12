

class MockPersistable:
    def __init__(self, artefacts=None, meta=None):
        self._artefacts = artefacts or dict()
        self._meta = meta or dict()

    def artefacts(self):
        return self._artefacts

    def get_meta_info(self):
        return self._meta

