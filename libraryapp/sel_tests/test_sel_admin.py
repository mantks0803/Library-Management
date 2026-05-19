import time
from selenium.webdriver.common.by import By

from libraryapp.sel_tests.pages.AdminPage import AdminPage
from libraryapp.sel_tests.pages.HistoryPage import HistoryPage


def test_unauthorized_access(driver):
    admin_page = AdminPage(driver)
    admin_page.open("http://127.0.0.1:5000/admin")
    time.sleep(1)
    assert "Forbidden" in driver.page_source


def test_admin_login_and_add_book(driver):
    admin_page = AdminPage(driver)

    admin_page.login("admin", "123")

    admin_page.open("http://127.0.0.1:5000/admin")
    time.sleep(1)

    assert "QUẢN TRỊ THƯ VIỆN" in driver.page_source

    admin_page.add_book("Sách Test UI", "Tester", 2025,"Novel",5)
    assert "alert-success" in driver.page_source


def test_inventory_cycle(driver):
    history_page = HistoryPage(driver)
    admin_page = AdminPage(driver)

    history_page.login("tester", "Th@nhman08032005")

    driver.get("http://127.0.0.1:5000/book-detail/6")
    time.sleep(1)
    stock_text = driver.find_element(By.CSS_SELECTOR, ".text-success").text
    initial_stock = int(''.join(filter(str.isdigit, stock_text)))

    history_page.add_to_cart()
    time.sleep(1)
    history_page.confirm_borrow()
    time.sleep(1)
    history_page.go_to_history()
    time.sleep(1)
    history_page.click_first_return_btn()
    time.sleep(1)
    history_page.confirm_return_modal()
    time.sleep(1)
    admin_page.logout()

    admin_page.login("admin", "123")
    approval_result = admin_page.approve_slip()
    assert approval_result is True
    assert "alert-success" in driver.page_source
    admin_page.logout()

    history_page.login("tester", "Th@nhman08032005")
    driver.get("http://127.0.0.1:5000/book-detail/6")
    time.sleep(1)
    stock_text_new = driver.find_element(By.CSS_SELECTOR, ".text-success").text
    final_stock = int(''.join(filter(str.isdigit, stock_text_new)))

    assert final_stock == initial_stock
