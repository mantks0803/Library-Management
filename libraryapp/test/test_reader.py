from libraryapp.dao.readers import get_reader, get_list_readers, count_readers
from libraryapp.test.test_base import test_app, test_session, sample_reader

def test_get_reader(test_session, sample_reader):
    reader = get_reader(sample_reader.id)

    assert reader is not None
    assert reader.id == sample_reader.id

def test_get_list_readers_full(test_session, sample_reader):
    readers = get_list_readers(full=True, page=1)

    assert len(readers) >= 1

def test_get_list_readers_current_user(test_session, mocker, sample_reader):
    fake_user = mocker.Mock()
    fake_user.id = sample_reader.id

    mocker.patch("libraryapp.dao.readers.current_user", fake_user)

    readers = get_list_readers(full=False, page=1)

    assert len(readers) == 1
    assert readers[0].id == sample_reader.id

def test_count_readers_full(test_session, sample_reader):
    count = count_readers(full=True)

    assert count >= 1

def test_count_readers_current_user(test_session, mocker, sample_reader):
    fake_user = mocker.Mock()
    fake_user.id = sample_reader.id

    mocker.patch("libraryapp.dao.readers.current_user", fake_user)

    count = count_readers(full=False)

    assert count == 1

def test_count_readers_user_not_found(test_session, mocker):
    fake_user = mocker.Mock()
    fake_user.id = 9999

    mocker.patch("libraryapp.dao.readers.current_user", fake_user)

    count = count_readers(full=False)

    assert count == 0