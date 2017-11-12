
from mocking import MockPersistable


def test_can_query_by_meta_attributes(local_storage):
    storage = local_storage
    
    storage.persist(_persisted_thing(attrib1='foo', attrib2='bar'))
    storage.persist(_persisted_thing(attrib1='frub', attrib2='bar'))
    storage.persist(_persisted_thing(attrib1='foo', attrib2='baz'))

    results = storage.find(attrib1='foo').fetch()

    assert len(results) == 2
    assert has({'attrib1': 'foo', 'attrib2': 'bar'}, results)
    assert has({'attrib1': 'foo', 'attrib2': 'baz'}, results)


def test_query_ordering(local_storage):
    storage = local_storage

    storage.persist(_persisted_thing(attrib1='c', attrib2='a'))
    storage.persist(_persisted_thing(attrib1='b', attrib2='a'))
    storage.persist(_persisted_thing(attrib1='a', attrib2='b'))

    results = storage.find().order_by('attrib2', 'attrib1').fetch()

    a, b, c = results

    assert a['attrib1'] == 'b'
    assert b['attrib1'] == 'c'
    assert c['attrib1'] == 'a'


def _persisted_thing(**kwargs):
    return MockPersistable(meta=kwargs)


def has(target, under_test):
    for elem in under_test:
        try:
            if all(elem[k] == v for k, v in target.items()):
                return True
        except KeyError:
            continue
    else:
        return False
