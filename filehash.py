from hashlib import sha256


def _read_file_chunks(fileobject):
    while True:
        chunk = fileobject.read(8192)
        if not chunk:
            break
        yield chunk


def file_hash(path):

    hasher = sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in _read_file_chunks(f):
                hasher.update(chunk)
    except FileNotFoundError:
        raise ComparisonFailureException(
                'Unable to open {path} for hashing'.format(path=path))

    return hasher
