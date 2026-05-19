from selenium.webdriver.common.by import By
from libraryapp.sel_tests.pages.BookDetailPage import BookDetailPage
from libraryapp.sel_tests.pages.CartPage import CartPage
from libraryapp.sel_tests.pages.HistoryBorrowPage import HistoryBorrowPage
from libraryapp.sel_tests.pages.HomePage import HomePage
from libraryapp.sel_tests.pages.LoginPage import LoginPage
import time

def test_add_book_to_cart_success(driver):
    login_page = LoginPage(driver)
    login_page.open_page()
    login_page.login("ndqbao", "Abc1234@")

    home_page = HomePage(driver)
    book_detail_page = BookDetailPage(driver)

    for i in range(5):
        if i > 2:
            driver.execute_script("window.scrollBy(0, 700);")
            time.sleep(1)
        home_page.view_book_detail(i+1)
        book_detail_page.add_book_to_cart()
        book_detail_page.return_home()
        time.sleep(1)

    cart = driver.find_element(By.CSS_SELECTOR, '#cart-badge');
    assert '5' in cart.text


def test_add_book_to_cart_fail(driver):
    login_page = LoginPage(driver)
    login_page.open_page()
    login_page.login("ndqbao", "Abc1234@")

    home_page = HomePage(driver)
    book_detail_page = BookDetailPage(driver)

    for i in range(5):
        if i > 2:
            driver.execute_script("window.scrollBy(0, 700);")
            time.sleep(1)
        home_page.view_book_detail(i+1)
        book_detail_page.add_book_to_cart()
        book_detail_page.return_home()
        time.sleep(1)

    driver.execute_script("window.scrollBy(0, 700);")
    time.sleep(1)
    home_page.view_book_detail(6)
    book_detail_page.add_book_to_cart()

    alert = driver.find_element(By.CSS_SELECTOR, '.alert-warning')
    cart = driver.find_element(By.CSS_SELECTOR, '#cart-badge')
    assert 'Bạn chỉ có thể mượn tối đa 5 cuốn sách!' in alert.text
    assert '5' in cart.text


# def test_delete_book(driver):
#     login_page = LoginPage(driver)
#     login_page.open_page()
#     login_page.login("ndqbao", "Abc1234@")
#     home_page = HomePage(driver)



def test_borrow_book_success(driver):
    login_page = LoginPage(driver=driver)
    home_page = HomePage(driver=driver)
    book_detail_page = BookDetailPage(driver=driver)
    cart_page = CartPage(driver=driver)
    history_page = HistoryBorrowPage(driver=driver)

    login_page.open_page()
    login_page.login("ndqbao", "Abc1234@")


    home_page.view_book_detail(1)
    time.sleep(2)
    book_detail_page.add_book_to_cart()

    cart_page.open_page()
    cart_page.borrow_book()

    time.sleep(2)
    driver.switch_to.alert.accept()

    time.sleep(2)
    history_page.open_page()
    time.sleep(2)
    status = driver.find_element(By.NAME, 'status')

    assert "Đang mượn" in status.text


def test_borrow_6th_book(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login("ndqbao", "Abc1234@")

    home_page = HomePage(driver=driver)
    book_detail_page = BookDetailPage(driver=driver)
    cart_page = CartPage(driver=driver)

    for i in range(5):
        if i > 2:
            driver.execute_script("window.scrollBy(0, 700);")
            time.sleep(1)
        home_page.view_book_detail(i+1)
        book_detail_page.add_book_to_cart()
        book_detail_page.return_home()
        time.sleep(1)

    cart_page.open_page()
    cart_page.borrow_book()
    time.sleep(1)
    driver.switch_to.alert.accept()

    home_page.open_page()
    driver.execute_script("window.scrollBy(0, 700);")
    time.sleep(1)
    home_page.view_book_detail(6)
    book_detail_page.add_book_to_cart()

    cart_page.open_page()
    warning = driver.find_element(By.CSS_SELECTOR, 'div.alert.alert-danger.small.mb-3 > strong')
    assert warning is not None





