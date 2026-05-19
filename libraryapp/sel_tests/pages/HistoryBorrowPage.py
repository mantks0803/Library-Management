from selenium.webdriver.common.by import By

from libraryapp.sel_tests.pages.BasePage import BasePage


class HistoryBorrowPage(BasePage):
    URL = 'http://127.0.0.1:5000/history'
    RETURN_BTN = (By.NAME, 'btn-return')


    def open_page(self):
        self.open(self.URL)

