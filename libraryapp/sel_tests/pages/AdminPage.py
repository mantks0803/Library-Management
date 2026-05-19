import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from libraryapp.sel_tests.pages.BasePage import BasePage


class AdminPage(BasePage):
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[name='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")

    OPEN_ADD_MODAL_BTN = (By.CSS_SELECTOR, "button[data-bs-target='#addBookModal']")
    TITLE_INPUT = (By.CSS_SELECTOR, "input[name='title']")
    AUTHOR_INPUT = (By.CSS_SELECTOR, "input[name='author']")
    YEAR_INPUT = (By.CSS_SELECTOR, "input[name='publish_year']")
    TYPE_INPUT = (By.CSS_SELECTOR, "input[name='type']")
    QTY_INPUT = (By.CSS_SELECTOR, "input[name='quantity']")
    SAVE_BOOK_BTN = (By.CSS_SELECTOR, "form[action='/book/add'] button[type='submit']")

    PENDING_TAB = (By.CSS_SELECTOR, "a.nav-link[href='/slip?status=pending']")
    APPROVE_BTN = (By.CSS_SELECTOR, "form[action^='/slip/approve/'] button[type='submit']")

    def login(self, username, password):
        self.open('http://127.0.0.1:5000/login')
        self.typing(*self.USERNAME_INPUT, username)
        pass_element = self.find(*self.PASSWORD_INPUT)
        pass_element.send_keys(password)
        pass_element.send_keys(Keys.ENTER)
        time.sleep(2)

    def logout(self):
        self.open('http://127.0.0.1:5000/logout')
        time.sleep(1)

    def add_book(self, title, author,pubyear, book_type, qty):
        self.open('http://127.0.0.1:5000/book')
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", self.find(*self.OPEN_ADD_MODAL_BTN))
        time.sleep(1)
        self.typing(*self.TITLE_INPUT, title)
        time.sleep(1)
        self.typing(*self.AUTHOR_INPUT, author)
        time.sleep(1)

        self.typing(*self.TYPE_INPUT, book_type)
        time.sleep(1)
        self.typing(*self.YEAR_INPUT,pubyear)
        time.sleep(1)
        #fix : điền số bị chèn
        qty_el = self.find(*self.QTY_INPUT)
        qty_el.clear()
        qty_el.send_keys(str(qty))  #
        self.driver.execute_script("arguments[0].click();", self.find(*self.SAVE_BOOK_BTN))
        time.sleep(2)

    def approve_slip(self):
        self.open('http://127.0.0.1:5000/slip')
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", self.find(*self.PENDING_TAB))
        time.sleep(1)
        buttons = self.finds(*self.APPROVE_BTN)
        if len(buttons) > 0:
            self.driver.execute_script("arguments[0].click();", buttons[0])
            time.sleep(1)
            self.driver.switch_to.alert.accept()
            time.sleep(2)
            return True
        return False