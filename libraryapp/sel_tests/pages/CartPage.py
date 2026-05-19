import time

from selenium.webdriver.common.by import By

from libraryapp.sel_tests.pages.BasePage import BasePage


class CartPage(BasePage):
    URL = 'http://127.0.0.1:5000/cart/view'
    BORROW_BTN = (By.CSS_SELECTOR, '#mainContent > div > div > div.col-lg-4 > div > div.card-body > button')

    def open_page(self):
        self.open(self.URL)

    def borrow_book(self):
        element = self.driver.find_element(*self.BORROW_BTN)

        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

        time.sleep(0.5)

        self.click(*self.BORROW_BTN)
