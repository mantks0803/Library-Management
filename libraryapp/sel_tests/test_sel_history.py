import time
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By

from libraryapp import app, db
from libraryapp.models import (
    Book,
    BorrowSlip,
    BorrowSlipDetail,
    BorrowSlipStatus,
    Reader,
    ReaderStatus,
    User,
    UserRole,
)
from libraryapp.sel_tests.pages.HistoryPage import HistoryPage
from libraryapp.utils import hash_password


def ensure_book_available(book_id=6):
    book = Book.query.get(book_id)
    if book is None:
        book = Book(
            id=book_id,
            title="Selenium History Book",
            author="Selenium",
            type="Test",
            publish_year=2026,
            quantity=10,
        )
        db.session.add(book)
        return book

    book.quantity = max(book.quantity or 0, 10)
    book.active = True
    return book


def ensure_user(username, password, role, name, phone):
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(
            name=name,
            phone=phone,
            email=f"{username}@test.local",
            username=username,
            password=hash_password(password),
            user_role=role,
        )
        db.session.add(user)
        db.session.flush()
    else:
        user.name = name
        user.phone = phone
        user.password = hash_password(password)
        user.user_role = role
        user.active = True

    if role == UserRole.READER:
        reader = Reader.query.get(user.id)
        if reader is None:
            db.session.add(Reader(id=user.id, status=ReaderStatus.ACTIVE))
        else:
            reader.status = ReaderStatus.ACTIVE

    return user


def delete_reader_slips(reader_id):
    slips = BorrowSlip.query.filter_by(reader_id=reader_id).all()
    for slip in slips:
        BorrowSlipDetail.query.filter_by(borrow_slip_id=slip.id).delete()
        db.session.delete(slip)


def ensure_history_accounts():
    """
    Chuan bi tai khoan dung chung cho cac test lich su muon sach.
    """
    with app.app_context():
        ensure_book_available()
        ensure_user("admin", "123", UserRole.ADMIN, "Admin", "0900000001")
        tester = ensure_user("tester", "Th@nhman08032005", UserRole.READER, "Tester", "0900000002")
        ensure_user("user1", "123", UserRole.READER, "User One", "0900000003")
        delete_reader_slips(tester.id)
        db.session.commit()


def ensure_empty_history_user():
    """
    Chuan bi reader khong co phieu muon de test lich su trong.
    """
    with app.app_context():
        user = ensure_user(
            "history_empty",
            "Abc1234",
            UserRole.READER,
            "History Empty",
            "0900000004",
        )
        delete_reader_slips(user.id)
        db.session.commit()


def ensure_user1_overdue_slips():
    """
    Chuan bi dung 2 phieu qua han cho user1 de test trang thai qua han.
    """
    with app.app_context():
        book = ensure_book_available()
        user = ensure_user("user1", "123", UserRole.READER, "User One", "0900000003")
        reader = Reader.query.get(user.id)
        delete_reader_slips(user.id)
        db.session.flush()

        for _ in range(2):
            slip = BorrowSlip(
                reader_id=user.id,
                borrow_date=datetime.now() - timedelta(days=10),
                due_date=datetime.now() - timedelta(days=3),
                status=BorrowSlipStatus.OVERDUE,
                penalty_fee=30000,
            )
            db.session.add(slip)
            db.session.flush()
            db.session.add(
                BorrowSlipDetail(
                    borrow_slip_id=slip.id,
                    book_id=book.id,
                    is_returned=False,
                )
            )

        reader.status = ReaderStatus.LOCKED
        db.session.commit()


def setup_borrow_data(page):
    ensure_history_accounts()
    page.login("tester", "Th@nhman08032005")
    time.sleep(1)
    page.add_to_cart()
    time.sleep(1)
    page.confirm_borrow()
    time.sleep(2)


def test_borrowing_status(driver):
    """
    TC-1: Sau khi mượn sách thành công, lịch sử hiển thị trạng thái Đang mượn.
    """
    page = HistoryPage(driver)
    setup_borrow_data(page)

    page.go_to_history()
    assert "Đang mượn" in driver.page_source


def test_return_request_status(driver):
    """
    TC-2: Gửi yêu cầu trả sách thành công, lịch sử chuyển sang trạng thái Chờ duyệt.
    """
    page = HistoryPage(driver)
    setup_borrow_data(page)

    page.go_to_history()
    page.click_first_return_btn()
    time.sleep(1)
    page.confirm_return_modal()
    time.sleep(2)

    assert "Chờ duyệt" in driver.page_source


def test_prevent_double_return(driver):
    """
    TC-3: Sau khi đã gửi yêu cầu trả, nút yêu cầu trả không còn hiển thị cho phiếu đó.
    """
    page = HistoryPage(driver)
    setup_borrow_data(page)

    page.go_to_history()
    initial_count = page.get_return_btn_count()

    page.click_first_return_btn()
    time.sleep(1)
    page.confirm_return_modal()
    time.sleep(2)

    final_count = page.get_return_btn_count()
    assert final_count == initial_count - 1


def test_history_requires_login(driver):
    """
    TC-4: Người dùng chưa đăng nhập khi vào lịch sử sẽ bị chuyển về trang login.
    """
    page = HistoryPage(driver)

    page.go_to_history()

    assert driver.current_url == "http://127.0.0.1:5000/login"


def test_empty_history_for_new_user(driver):
    """
    TC-5: User mới chưa mượn sách sẽ thấy thông báo lịch sử trống.
    """

    ensure_empty_history_user()

    page = HistoryPage(driver)
    page.login("history_empty", "Abc1234")
    page.go_to_history()

    assert "Bạn chưa mượn cuốn sách nào!" in driver.page_source
    assert page.get_return_btn_count() == 0


def test_history_displays_borrow_slip_information(driver):
    """
    TC-6: Lịch sử mượn hiển thị thông tin phiếu gồm mã phiếu, tình trạng trả, phí phạt và nút trả.
    """
    page = HistoryPage(driver)
    setup_borrow_data(page)

    page.go_to_history()

    assert "#" in driver.find_element(By.CSS_SELECTOR, "tbody tr td").text
    assert "Chưa trả" in driver.page_source
    assert "0đ" in driver.page_source
    assert page.get_return_btn_count() > 0


def test_return_modal_displays_slip_information(driver):
    """
    TC-7: Modal xác nhận trả hiển thị đủ mã phiếu, ngày mượn, hạn trả, ngày trả và danh sách sách.
    """
    page = HistoryPage(driver)
    setup_borrow_data(page)

    page.go_to_history()
    page.click_first_return_btn()
    time.sleep(1)

    modal = driver.find_element(By.CSS_SELECTOR, "#returnBookModal")
    assert "show" in modal.get_attribute("class")
    assert driver.find_element(By.CSS_SELECTOR, "#modalSlipId").text.startswith("#")
    assert driver.find_element(By.CSS_SELECTOR, "#modalBorrowDate").text != ""
    assert driver.find_element(By.CSS_SELECTOR, "#modalDueDate").text != ""
    assert driver.find_element(By.CSS_SELECTOR, "#modalCurrentDate").text != ""
    assert len(driver.find_elements(By.CSS_SELECTOR, "#modalBookList li")) > 0


def test_cancel_return_modal_keeps_borrowing_status(driver):
    """
    TC-8: Hủy modal trả sách không làm thay đổi trạng thái phiếu đang mượn.
    """
    page = HistoryPage(driver)
    setup_borrow_data(page)

    page.go_to_history()
    initial_count = page.get_return_btn_count()
    page.click_first_return_btn()
    time.sleep(1)

    cancel_btn = driver.find_element(By.CSS_SELECTOR, "#returnBookModal .modal-body button[data-bs-dismiss='modal']")
    driver.execute_script("arguments[0].click();", cancel_btn)
    time.sleep(1)

    assert "Đang mượn" in driver.page_source
    assert page.get_return_btn_count() == initial_count


def test_overdue_history_for_user1(driver):
    """
    TC-9: User có phiếu quá hạn sẽ thấy trạng thái Quá hạn và vẫn có nút yêu cầu trả.
    """
    ensure_user1_overdue_slips()
    page = HistoryPage(driver)
    page.login("user1", "123")

    page.go_to_history()

    assert "Quá hạn" in driver.page_source
    assert page.get_return_btn_count() > 0


def test_returned_history_after_admin_approve(driver):
    """
    TC-10: Sau khi admin duyệt trả sách, lịch sử của reader hiển thị Đã trả và Hoàn tất.
    """
    page = HistoryPage(driver)
    setup_borrow_data(page)

    page.go_to_history()
    slip_text = driver.find_element(By.CSS_SELECTOR, "tbody tr td").text
    slip_id = slip_text.replace("#", "").strip()

    page.click_first_return_btn()
    time.sleep(1)
    page.confirm_return_modal()
    time.sleep(2)

    driver.get("http://127.0.0.1:5000/logout")
    page.login("admin", "123")
    driver.get("http://127.0.0.1:5000/slip?status=pending")
    approve_btn = driver.find_element(
        By.CSS_SELECTOR,
        f"form[action='/slip/approve/{slip_id}'] button[type='submit']"
    )
    driver.execute_script("arguments[0].click();", approve_btn)
    time.sleep(1)
    driver.switch_to.alert.accept()
    time.sleep(2)

    assert "status=pending" in driver.current_url

    driver.get("http://127.0.0.1:5000/logout")
    page.login("tester", "Th@nhman08032005")
    page.go_to_history()

    assert "Đã trả" in driver.page_source
    assert "Hoàn tất" in driver.page_source
