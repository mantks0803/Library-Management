import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from libraryapp.sel_tests.pages.BasePage import BasePage


class HistoryPage(BasePage):
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[name='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")
    LOGIN_BTN = (By.CSS_SELECTOR, "form button[type='submit']")

    ADD_CART_BTN = (By.CSS_SELECTOR, "button[onclick^='addToCart']")
    CONFIRM_BORROW_BTN = (By.CSS_SELECTOR, "button[onclick='confirmBorrow()']")

    RETURN_BTN = (By.CSS_SELECTOR, "button[onclick^='openReturnModal']")
    CONFIRM_MODAL_BTN = (By.CSS_SELECTOR, "#btnConfirmReturn")

    def login(self, username, password):
        self.open('http://127.0.0.1:5000/login')
        self.typing(*self.USERNAME_INPUT, username)

        e_pass = self.find(*self.PASSWORD_INPUT)
        e_pass.send_keys(password)
        e_pass.send_keys(Keys.ENTER)

        time.sleep(2)

    def add_to_cart(self):
        self.open('http://127.0.0.1:5000/book-detail/6')
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", self.find(*self.ADD_CART_BTN))

    def confirm_borrow(self):
        self.open('http://127.0.0.1:5000/cart/view')
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", self.find(*self.CONFIRM_BORROW_BTN))
        time.sleep(1)
        self.driver.switch_to.alert.accept()

    def go_to_history(self):
        self.open('http://127.0.0.1:5000/history')
        time.sleep(2)

    def get_return_btn_count(self):
        return len(self.finds(*self.RETURN_BTN))

    def click_first_return_btn(self):
        self.driver.execute_script("arguments[0].click();", self.find(*self.RETURN_BTN))

    def confirm_return_modal(self):
        self.driver.execute_script("arguments[0].click();", self.find(*self.CONFIRM_MODAL_BTN))
        time.sleep(2)
        self.driver.switch_to.alert.accept()
