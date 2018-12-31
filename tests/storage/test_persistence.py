
from pathlib import Path

from mocking import MockPersistable


def test_empty_thing_can_persist(local_storage):
    storage = local_storage

    to_persist = MockPersistable()

    assert storage.find().fetch() == []
    storage.persist(to_persist)
    assert len(storage.find().fetch()) == 1


def test_can_retrieve_thing_from_storage(local_storage, tmpdir):
    storage = local_storage
    artefact = tmpdir.join('some_file')
    artefact.write('sample_data')

    to_persist = MockPersistable(
        artefacts={
            'some_file': str(artefact)
        }
    )

    assert storage.find().fetch() == []
    storage.persist(to_persist)

    retreived = storage.find().fetch()[0]
    assert Path(retreived.fetch_local('some_file')).exists()

