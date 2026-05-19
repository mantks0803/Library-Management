import time

from selenium.webdriver.common.by import By

from libraryapp.sel_tests.pages.BasePage import BasePage


class CartPage(BasePage):
    URL = 'http://127.0.0.1:5000/cart/view'
    BORROW_BTN = (By.CSS_SELECTOR, '#mainContent > div > div > div.col-lg-4 > div > div.card-body > button')
    DELETE_BTN = (By.CSS_SELECTOR, 'tbody > tr > td.text-end > button')
    CLEAR_BTN = (By.CSS_SELECTOR, 'div.d-flex.justify-content-between.mt-3 > button')

    def open_page(self):
        self.open(self.URL)

    def borrow_book(self):
        element = self.driver.find_element(*self.BORROW_BTN)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
        self.click(*self.BORROW_BTN)

    def delete_book(self):
        self.click(*self.DELETE_BTN)
        time.sleep(1)
        self.driver.switch_to.alert.accept()

    def clear_cart(self):
        self.click(*self.CLEAR_BTN)
        time.sleep(1)
        self.driver.switch_to.alert.accept()
