from selenium.webdriver.common.by import By

from libraryapp.sel_tests.pages.BasePage import BasePage


class LoginPage(BasePage):
    URL = "http://127.0.0.1:5000/login"
    USERNAME_INPUT = (By.NAME, "username")
    PASSWORD_INPUT = (By.NAME, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, ".card .btn-primary")

    def open_page(self, url=URL):
        self.open(url)

    def login(self, username, password):
        self.typing(*self.USERNAME_INPUT, username)
        self.typing(*self.PASSWORD_INPUT, password)
        self.click(*self.LOGIN_BUTTON)




