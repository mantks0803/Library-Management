from datetime import datetime, timedelta
from idlelib.query import Query
from unittest.mock import MagicMock

from libraryapp import db
from libraryapp.dao.borrow_history import count_reader_borrowing_books, get_all_reader_borrow_details, \
    get_borrow_slip_details, get_reader_borrow_slips
from libraryapp.models import BorrowSlip, BorrowSlipDetail, Book, BorrowSlipStatus, UserRole, ReaderStatus, Reader, User
from libraryapp.test.test_base import test_session, test_app, sample_reader, sample_books_borrow, sample_slip,\
    sample_slip_pending, sample_borrow_details, test_client
from libraryapp.dao.borrow_slips import create_borrow_slip_multiple, request_return_borrow_slip, \
    confirm_return_borrow_slip


def test_empty_borrow_book(test_session, sample_reader):
    slip, details = create_borrow_slip_multiple(
        reader_id=sample_reader.id, book_ids=[]
    )
    assert slip is None
    assert details == []


def test_creates_slip_persisted_in_db(test_session, sample_reader, sample_books_borrow):
    book_a = sample_books_borrow[0]
    slip, details = create_borrow_slip_multiple(
        reader_id=sample_reader.id, book_ids=[book_a.id]
    )

    assert slip is not None
    db_slip = BorrowSlip.query.get(slip.id)
    assert db_slip is not None
    assert db_slip.reader_id == sample_reader.id
    assert db_slip.status == BorrowSlipStatus.BORROWING
    assert db_slip.penalty_fee == 0


def test_due_date_defaults_to_7_days(test_session, sample_reader, sample_books_borrow):
    book_a = sample_books_borrow[0]
    before = datetime.now()
    slip, _ = create_borrow_slip_multiple(
        reader_id=sample_reader.id, book_ids=[book_a.id]
    )
    after = datetime.now()
    assert before + timedelta(days=7) <= slip.due_date <= after + timedelta(days=7)


def test_custom_days_respected(test_session, sample_reader, sample_books_borrow):
    book_a = sample_books_borrow[0]
    borrow_date = datetime(2024, 1, 1)
    slip, _ = create_borrow_slip_multiple(
        reader_id=sample_reader.id,
        book_ids=[book_a.id],
        borrow_date=borrow_date,
        days=14,
    )
    assert slip.due_date == datetime(2024, 1, 15)


def test_explicit_borrow_date_used(test_session, sample_reader, sample_books_borrow):
    book_a = sample_books_borrow[0]
    fixed = datetime(2025, 3, 10)
    slip, _ = create_borrow_slip_multiple(
        reader_id=sample_reader.id,
        book_ids=[book_a.id],
        borrow_date=fixed,
    )
    assert slip.borrow_date == fixed


def test_book_quantity_decremented(test_session, sample_reader, sample_books_borrow):
    book_a = sample_books_borrow[0]
    create_borrow_slip_multiple(reader_id=sample_reader.id, book_ids=[book_a.id])
    assert Book.query.get(book_a.id).quantity == 2


def test_multiple_books_all_decremented(test_session, sample_reader, sample_books_borrow):
    book_a, book_b = sample_books_borrow[0], sample_books_borrow[1]
    slip, details = create_borrow_slip_multiple(
        reader_id=sample_reader.id, book_ids=[book_a.id, book_b.id]
    )
    assert len(details) == 2
    assert Book.query.get(book_a.id).quantity == 2
    assert Book.query.get(book_b.id).quantity == 0


def test_detail_fields_initialised_correctly(test_session, sample_reader, sample_books_borrow):
    book_a = sample_books_borrow[0]
    slip, details = create_borrow_slip_multiple(
        reader_id=sample_reader.id, book_ids=[book_a.id]
    )
    d = details[0]
    assert d.book_id == book_a.id
    assert d.is_returned is False
    assert d.return_date is None
    assert d.borrow_slip_id == slip.id


def test_detail_persisted_in_db(test_session, sample_reader, sample_books_borrow):
    book_a = sample_books_borrow[0]
    slip, _ = create_borrow_slip_multiple(
        reader_id=sample_reader.id, book_ids=[book_a.id]
    )
    db_details = BorrowSlipDetail.query.filter_by(borrow_slip_id=slip.id).all()
    assert len(db_details) == 1
    assert db_details[0].book_id == book_a.id


def test_book_with_zero_quantity_skipped(test_session, sample_reader, sample_books_borrow):
    book_a = sample_books_borrow[0]
    book_c = sample_books_borrow[2]
    slip, details = create_borrow_slip_multiple(
        reader_id=sample_reader.id, book_ids=[book_a.id, book_c.id]
    )
    assert len(details) == 1
    assert details[0].book_id == book_a.id
    assert Book.query.get(book_c.id).quantity == 0


def test_all_books_out_of_stock_returns_empty_details(test_session, sample_reader, sample_books_borrow):
    book_c = sample_books_borrow[2]
    slip, details = create_borrow_slip_multiple(
        reader_id=sample_reader.id, book_ids=[book_c.id]
    )
    assert details == []


def test_nonexistent_book_id_skipped(test_session, sample_reader):
    slip, details = create_borrow_slip_multiple(
        reader_id=sample_reader.id, book_ids=[99999]
    )
    assert details == []


from libraryapp import db
from libraryapp.dao.borrow_slips import create_borrow_slip_multiple

def test_create_borrow_slip_multiple_exception(test_session, sample_reader, sample_books_borrow, mocker):
    called = {"rollback": False}

    def fake_commit():
        raise Exception("DB error")

    def fake_rollback():
        called["rollback"] = True


    mocker.patch.object(db.session, "commit", side_effect=fake_commit)

    mocker.patch.object(db.session, "rollback", side_effect=fake_rollback)

    book = sample_books_borrow[0]

    borrow_slip, details = create_borrow_slip_multiple(
        reader_id=sample_reader.id,
        book_ids=[book.id]
    )

    assert borrow_slip is None
    assert details == []
    assert called["rollback"] is True


def test_get_reader_borrow_slips(test_app, sample_reader, sample_slip, sample_slip_pending):
    results, count = get_reader_borrow_slips(sample_reader.id, page=1)

    assert count >= 2
    assert len(results) <= test_app.config['PAGE_SIZE']


    if len(results) > 1:
        assert results[0].borrow_date >= results[1].borrow_date


def test_get_borrow_slip_details(sample_borrow_details, sample_slip_pending):
    details = get_borrow_slip_details(sample_slip_pending.id)

    assert len(details) == 1
    assert details[0].borrow_slip_id == sample_slip_pending.id


def test_get_borrow_slip_details_empty(test_session):
    details = get_borrow_slip_details(9999)
    assert details == []


def test_get_all_reader_borrow_details(sample_reader, sample_borrow_details):
    details = get_all_reader_borrow_details(sample_reader.id)

    assert len(details) >= 1


def test_get_all_reader_borrow_details_empty(test_session):
    details = get_all_reader_borrow_details(9999)
    assert details == []

def test_count_reader_borrowing_books(sample_reader, sample_borrow_details):
    count = count_reader_borrowing_books(sample_reader.id)
    assert count == 1


def test_count_reader_borrowing_books_ignore_returned(test_session, sample_reader, sample_slip_pending, sample_books_borrow):
    from libraryapp.models import BorrowSlipDetail

    detail = BorrowSlipDetail(
        borrow_slip_id=sample_slip_pending.id,
        book_id=sample_books_borrow[0].id,
        is_returned=True
    )

    test_session.add(detail)
    test_session.commit()

    count = count_reader_borrowing_books(sample_reader.id)

    assert count == 0


def test_count_reader_borrowing_books_ignore_status(test_session, sample_reader, sample_books_borrow):
    slip = BorrowSlip(
        reader_id=sample_reader.id,
        borrow_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=7),
        status=BorrowSlipStatus.RETURNED,
        penalty_fee=0
    )
    test_session.add(slip)
    test_session.commit()

    detail = BorrowSlipDetail(
        borrow_slip_id=slip.id,
        book_id=sample_books_borrow[0].id,
        is_returned=False
    )

    test_session.add(detail)
    test_session.commit()

    count = count_reader_borrowing_books(sample_reader.id)

    assert count == 0




def test_confirm_success_integration(test_session, test_client, mocker, sample_reader):
    u = sample_reader

    b1 = Book(title="A", author="C", type="CS")
    b2 = Book(title="B", author="D", type="IT")
    test_session.add_all([b1, b2])
    test_session.commit()

    mocker.patch('flask_login.utils._get_user', return_value=u)
    mocker.patch('libraryapp.routes.borrow_cart.current_user', u)

    mocker.patch('libraryapp.routes.borrow_cart.get_cart', return_value=[b1.id, b2.id])

    mocker.patch('libraryapp.routes.borrow_cart.count_reader_borrowing_books', return_value=0)

    res = test_client.post('/cart/confirm')

    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'thành công' in data['message']

    assert BorrowSlip.query.filter_by(reader_id=u.id).count() == 1

    with test_client.session_transaction() as sess:
        assert 'cart' not in sess or len(sess['cart']) == 0


def test_borrow_account_locked(test_session, test_client, mocker, sample_reader):
    reader = Reader.query.filter_by(id=sample_reader.id).first()
    reader.status = ReaderStatus.LOCKED
    u = sample_reader
    b1 = Book(title="A", author="C", type="CS")
    b2 = Book(title="B", author="D", type="IT")
    test_session.add_all([b1, b2])
    test_session.commit()

    mocker.patch('flask_login.utils._get_user', return_value=u)
    mocker.patch('libraryapp.routes.borrow_cart.current_user', u)

    mocker.patch('libraryapp.routes.borrow_cart.get_cart', return_value=[b1.id, b2.id])

    mocker.patch('libraryapp.routes.borrow_cart.count_reader_borrowing_books', return_value=0)

    res = test_client.post('/cart/confirm')

    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is False
    assert 'bị khóa' in data['message']

    assert BorrowSlip.query.filter_by(reader_id=u.id).count() == 0

    with test_client.session_transaction() as sess:
        assert 'cart' not in sess or len(sess['cart']) == 2

def test_borrow_overdue(test_session, test_client, mocker, sample_reader):
    u = sample_reader

    b1 = Book(title="A", author="C", type="CS")
    b2 = Book(title="B", author="D", type="IT")
    test_session.add_all([b1, b2])
    test_session.commit()

    mocker.patch('flask_login.utils._get_user', return_value=u)
    mocker.patch('libraryapp.routes.borrow_cart.current_user', u)

    overdue_slip = BorrowSlip(
        reader_id=u.id,
        status=BorrowSlipStatus.OVERDUE,
        due_date=datetime.now()
    )
    test_session.add(overdue_slip)
    test_session.commit()

    mocker.patch('libraryapp.routes.borrow_cart.current_user', u)
    mocker.patch('libraryapp.routes.borrow_cart.get_cart', return_value=[1])

    res = test_client.post('/cart/confirm')
    data = res.get_json()

    assert data['success'] is False
    assert 'trả sách quá hạn' in data['message']


def test_confirm_exceed_limit(test_session,test_client, mocker, sample_reader):
    u = sample_reader

    b1 = Book(title="A", author="C", type="CS")
    b2 = Book(title="B", author="D", type="IT")
    test_session.add_all([b1, b2])
    test_session.commit()

    mocker.patch('flask_login.utils._get_user', return_value=u)
    mocker.patch('libraryapp.routes.borrow_cart.current_user', u)

    mocker.patch('libraryapp.utils.current_user', u)

    mocker.patch('libraryapp.routes.borrow_cart.get_cart', return_value=[b1.id, b2.id])

    mocker.patch('libraryapp.routes.borrow_cart.count_reader_borrowing_books', return_value=4)

    res = test_client.post('/cart/confirm')

    assert res.status_code == 200
    data = res.get_json()

    assert data['success'] is False
    assert 'tối đa 5 quyển' in data['message']

    assert BorrowSlip.query.filter_by(reader_id=u.id).count() == 0

    with test_client.session_transaction() as sess:
        assert 'cart' not in sess or len(sess['cart']) == 2


def test_confirm_create_slip_system_error(test_session, test_client, mocker, sample_reader):
    u = sample_reader

    mocker.patch('flask_login.utils._get_user', return_value=u)
    mocker.patch('libraryapp.routes.borrow_cart.current_user', u)
    mocker.patch('libraryapp.utils.current_user', u)

    mocker.patch('libraryapp.routes.borrow_cart.get_cart', return_value=[101])
    mocker.patch('libraryapp.routes.borrow_cart.count_reader_borrowing_books', return_value=0)

    mocker.patch('libraryapp.routes.borrow_cart.create_borrow_slip_multiple',return_value=(None, None))

    res = test_client.post('/cart/confirm')

    assert res.status_code == 200
    data = res.get_json()

    assert data['success'] is False
    assert 'Lỗi khi tạo phiếu mượn' in data['message']

    assert BorrowSlip.query.filter_by(reader_id=u.id).count() == 0

def test_load_book_detail(test_session, test_client, mocker, sample_reader):
    b1 = Book(title="A", author="C", type="CS")
    test_session.add(b1)
    test_session.commit()

    u = sample_reader
    id = b1.id
    mocker.patch('flask_login.utils._get_user', return_value=u)
    mocker.patch('libraryapp.routes.borrow_cart.current_user', u)
    mocker.patch("libraryapp.routes.book_detail.render_template", return_value="OK")
    res = test_client.get(f'/book-detail/{id}')
    assert res.status_code == 200


def test_view_cart_with_items(test_session, test_client, mocker, sample_reader):

    u = sample_reader

    b1 = Book(title="Book A", author="Author A", type="CS")
    b2 = Book(title="Book B", author="Author B", type="IT")
    test_session.add_all([b1, b2])
    test_session.commit()


    mocker.patch('flask_login.utils._get_user', return_value=u)


    mocker.patch('libraryapp.routes.borrow_cart.current_user', u)


    mocker.patch('libraryapp.routes.borrow_cart.get_cart', return_value=[b1.id, b2.id])
    mocker.patch('libraryapp.routes.borrow_cart.get_book',
                 side_effect=lambda id: b1 if id == b1.id else (b2 if id == b2.id else None))
    mocker.patch('libraryapp.routes.borrow_cart.count_reader_borrowing_books', return_value=1)

    captured = {}

    def fake_render(template, **kwargs):
        captured['template'] = template
        captured['data'] = kwargs
        return "OK"

    mocker.patch('libraryapp.routes.borrow_cart.render_template', side_effect=fake_render)

    res = test_client.get('/cart/view')

    assert res.status_code == 200
    assert captured['template'] == 'reader/borrow_cart.html'

    data = captured['data']
    assert len(data['books']) == 2
    assert data['books'][0].title == "Book A"
    assert data['cart_count'] == 2
    assert data['borrowing_count'] == 1
    assert data['total_books'] == 3

    expected_borrow_date = datetime.now().strftime('%d/%m/%Y')
    expected_due_date = (datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y')
    assert data['borrow_date'] == expected_borrow_date
    assert data['due_date'] == expected_due_date



ROUTE_PATH = 'libraryapp.routes.borrow_history'


def test_render_borrow_history_success(test_client, test_session, mocker, sample_reader):

    reader = Reader.query.filter_by(id=sample_reader.id).first()

    now = datetime.now()

    b1 = Book(title="Sách Test", author="TG A", type="IT")
    test_session.add(b1)
    test_session.commit()


    slip = BorrowSlip(
        reader_id=reader.id,
        status=BorrowSlipStatus.RETURNED,
        borrow_date=now - timedelta(days=10),
        due_date=now - timedelta(days=3),
        penalty_fee=0
    )
    test_session.add(slip)
    test_session.commit()

    detail = BorrowSlipDetail(
        borrow_slip_id=slip.id,
        book_id=b1.id,
        is_returned=True,
        return_date=now - timedelta(days=2)
    )
    test_session.add(detail)
    test_session.commit()


    mocker.patch('flask_login.utils._get_user', return_value=sample_reader)
    mocker.patch('libraryapp.routes.borrow_history.current_user', sample_reader)


    captured = {}

    def fake_render(template, **kwargs):
        captured['data'] = kwargs
        return "OK"

    mocker.patch('libraryapp.routes.borrow_history.render_template', side_effect=fake_render)


    res = test_client.get('/history')


    assert res.status_code == 200
    history = captured['data']['history_list']

    assert len(history) == 1
    assert history[0]['slip_id'] == slip.id
    assert history[0]['status'] == 'Đã trả'
    assert history[0]['books'][0]['title'] == "Sách Test"
    assert history[0]['books'][0]['is_returned'] is True


def test_api_return_slip_success(test_client, test_session, mocker, sample_reader):
    reader = Reader.query.filter_by(id=sample_reader.id).first()
    slip = BorrowSlip(
        reader_id=reader.id,
        status=BorrowSlipStatus.BORROWING,
        borrow_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=7)
    )
    test_session.add(slip)
    test_session.commit()


    mocker.patch('flask_login.utils._get_user', return_value=sample_reader)
    mocker.patch('libraryapp.routes.borrow_history.current_user', sample_reader)


    mocker.patch('libraryapp.routes.borrow_history.request_return_borrow_slip',
                 return_value=(True, "Yêu cầu trả sách đã được gửi!"))

    res = test_client.post(f'/api/return-slip/{slip.id}')

    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['message'] == "Yêu cầu trả sách đã được gửi!"


def test_render_borrow_history_overdue(test_client, test_session, mocker, sample_reader):
    reader = Reader.query.filter_by(id=sample_reader.id).first()

    slip = BorrowSlip(
        id=10, reader_id=reader.id, status=BorrowSlipStatus.OVERDUE,
        borrow_date=datetime.now() - timedelta(days=10),
        due_date=datetime.now() - timedelta(days=1)
    )
    test_session.add(slip)
    test_session.commit()

    mocker.patch('flask_login.utils._get_user', return_value=sample_reader)
    mocker.patch('libraryapp.routes.borrow_history.current_user', sample_reader)

    captured = {}
    mocker.patch('libraryapp.routes.borrow_history.render_template',
                 side_effect=lambda t, **kw: captured.update(kw) or "OK")

    test_client.get('/history')
    assert captured['history_list'][0]['status'] == 'Quá hạn'


def test_render_borrow_history_pending(test_client, test_session, mocker, sample_reader):
    reader = Reader.query.filter_by(id=sample_reader.id).first()

    slip = BorrowSlip(
        id=11, reader_id=reader.id, status=BorrowSlipStatus.PENDING,
        borrow_date=datetime.now(), due_date=datetime.now() + timedelta(days=7)
    )
    test_session.add(slip)
    test_session.commit()

    mocker.patch('flask_login.utils._get_user', return_value=sample_reader)
    mocker.patch('libraryapp.routes.borrow_history.current_user', sample_reader)

    captured = {}
    mocker.patch('libraryapp.routes.borrow_history.render_template',
                 side_effect=lambda t, **kw: captured.update(kw) or "OK")

    test_client.get('/history')
    assert captured['history_list'][0]['status'] == 'Chờ duyệt'


def test_render_borrow_history_borrowing(test_client, test_session, mocker, sample_reader):
    reader = Reader.query.filter_by(id=sample_reader.id).first()

    slip = BorrowSlip(
        id=12, reader_id=reader.id, status=BorrowSlipStatus.BORROWING,
        borrow_date=datetime.now(), due_date=datetime.now() + timedelta(days=7)
    )
    test_session.add(slip)
    test_session.commit()

    mocker.patch('flask_login.utils._get_user', return_value=sample_reader)
    mocker.patch('libraryapp.routes.borrow_history.current_user', sample_reader)

    captured = {}
    mocker.patch('libraryapp.routes.borrow_history.render_template',
                 side_effect=lambda t, **kw: captured.update(kw) or "OK")

    test_client.get('/history')
    assert captured['history_list'][0]['status'] == 'Đang mượn'