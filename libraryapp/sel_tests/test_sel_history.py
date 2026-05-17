import time
from libraryapp.sel_tests.pages.HistoryPage import HistoryPage


def setup_borrow_data(page):
    page.login("tester", "Th@nhman08032005")
    time.sleep(1)
    page.add_to_cart()
    time.sleep(1)
    page.confirm_borrow()
    time.sleep(2)


def test_borrowing_status(driver):
    page = HistoryPage(driver)
    setup_borrow_data(page)

    page.go_to_history()
    assert "Đang mượn" in driver.page_source


def test_return_request_status(driver):
    page = HistoryPage(driver)
    setup_borrow_data(page)

    page.go_to_history()
    page.click_first_return_btn()
    time.sleep(1)
    page.confirm_return_modal()
    time.sleep(2)

    assert "Chờ duyệt" in driver.page_source


def test_prevent_double_return(driver):
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