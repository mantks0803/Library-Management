from selenium.webdriver.common.by import By

from libraryapp.sel_tests.pages.BasePage import BasePage


class BookDetailPage(BasePage):
    URL = f"http://127.0.0.1:5000/book-detail"
    ADD_TO_CART_BTN = (By.CSS_SELECTOR, "button[onclick^='addToCart']")
    RETURN_BTN = (By.CSS_SELECTOR, "a")

    def open(self, id):
        self.open(f"{self.URL}/{id}")

    def add_book_to_cart(self):
        self.click(*self.ADD_TO_CART_BTN)

    def return_home(self):
        self.click(*self.RETURN_BTN)


