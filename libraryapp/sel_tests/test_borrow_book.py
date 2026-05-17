from libraryapp.sel_tests.pages.BookDetailPage import BookDetailPage
from libraryapp.sel_tests.pages.CartPage import CartPage
from libraryapp.sel_tests.pages.LoginPage import LoginPage
import time


def test_view_detail_book(driver):
    detail = BookDetailPage(driver=driver)
    detail.open(1)


def test_view_cart(driver):
    cart = CartPage(driver=driver)
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('ndqbao', 'Abc1234@')
    time.sleep(2)
    cart.open_page()
    time.sleep(2)