
from webwatcher import filehash


def test_can_hash_empty_file(tmpdir):
    target_file = tmpdir.join('some_file').ensure()

    assert filehash.file_hash(str(target_file)).hexdigest() \
            == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'  # noqa


def test_can_hash_file_with_content(tmpdir):
    target_file = tmpdir.join('some_file')
    target_file.write('hello world')

    assert filehash.file_hash(str(target_file)).hexdigest() \
            == 'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'  # noqa
