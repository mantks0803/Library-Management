from selenium.webdriver.common.by import By

from libraryapp.sel_tests.pages.BasePage import BasePage


class RegisterPage(BasePage):
    URL = "http://127.0.0.1:5000/register"
    NAME_INPUT = (By.NAME, "name")
    USERNAME_INPUT = (By.NAME, "username")
    PASSWORD_INPUT = (By.NAME, "password")
    PHONE_INPUT = (By.NAME, "phone")
    EMAIL_INPUT = (By.NAME, "email")
    CONFIRM_PASSWORD_INPUT = (By.NAME, "confirm")



    REGISTER_BUTTON = (By.CSS_SELECTOR, ".card .btn-primary")

    def open_page(self, url=URL):
        self.open(url)

    def register(self, username, password, name, phone, email, confirm):
        self.typing(*self.USERNAME_INPUT, username)
        self.typing(*self.PASSWORD_INPUT, password)
        self.typing(*self.NAME_INPUT, name)
        self.typing(*self.PHONE_INPUT, phone)
        self.typing(*self.EMAIL_INPUT, email)
        self.typing(*self.CONFIRM_PASSWORD_INPUT, confirm)
        self.click(*self.REGISTER_BUTTON)




