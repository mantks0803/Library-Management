from selenium.webdriver.common.by import By

from libraryapp.sel_tests.pages.BasePage import BasePage


class BookPage1(BasePage):
    URL = "http://127.0.0.1:5000/book-detail/1"

    ADD_BUTTON = (By.CSS_SELECTOR, "div.d-flex.gap-3.mt-5 > button")

    def open_page(self, url=URL):
        self.open(url)

    def add_book(self):
        self.click(*self.ADD_BUTTON)




