from selenium.webdriver.common.by import By
from libraryapp.sel_tests.pages.BasePage import BasePage
import time

class HomePage(BasePage):
    URL = 'http://127.0.0.1:5000/'
    SEARCH_BOOK_NAME_INPUT =(By.CSS_SELECTOR, '.container-fluid .input-group > input')
    SEARCH_AUTHOR_INPUT =(By.CSS_SELECTOR, '#advancedFilter > div > div:nth-child(1) > input')
    SEARCH_BTN = (By.CSS_SELECTOR, '.container-fluid button.btn.btn-primary')
    FILTER_BTN = (By.CSS_SELECTOR, '[data-bs-toggle="collapse"]')
    SELECT_FORM = (By.CSS_SELECTOR, '.form-select')
    # Sử dụng XPath để tìm button "Xem chi tiết" đầu tiên (ít nhạy cảm hơn)
    BOOK_BUTTON1 = (By.XPATH, "//button[contains(text(), 'Xem chi tiết')]")
    BOOK_BUTTON2 = (By.XPATH, "(//button[contains(text(), 'Xem chi tiết')])[2]")
    # Tìm button "Thêm vào giỏ" trên trang chi tiết
    ADD_BOOK_BUTTON1 = (By.CSS_SELECTOR, 'div.col-md-8.p-5 > div.d-flex.gap-3.mt-5 > button')


    def open_page(self):
        self.open(self.URL)

    def search_book_name(self, kw):
        self.typing(*self.SEARCH_BOOK_NAME_INPUT, kw)
        self.click(*self.SEARCH_BTN)

    def search_author(self, kw):
        self.click(*self.FILTER_BTN)
        time.sleep(1)
        self.typing(*self.SEARCH_AUTHOR_INPUT, kw)
        self.click(*self.SEARCH_BTN)

    def search_type(self, value):
        self.click(*self.FILTER_BTN)
        time.sleep(1)
        self.select(*self.SELECT_FORM,value)
        self.click(*self.SEARCH_BTN)

    def search_all(self, name, author, book_type):
        self.typing(*self.SEARCH_BOOK_NAME_INPUT,name)
        self.click(*self.FILTER_BTN)
        time.sleep(1)
        self.typing(*self.SEARCH_AUTHOR_INPUT, author)
        self.select(*self.SELECT_FORM, book_type)
        self.click(*self.SEARCH_BTN)

    def get_dynamic_view_btn(self, index):
        xpath = f"(//div[contains(@class, 'card-body')]//button)[{index}]"
        return (By.XPATH, xpath)


    def view_book_detail(self, book_index):
        target_btn_locator = self.get_dynamic_view_btn(book_index)
        self.click(*target_btn_locator)





