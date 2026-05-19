from libraryapp.sel_tests.pages.BasePage import BasePage


class ProfilePage(BasePage):
    URL = 'http://127.0.0.1:5000/profile'

    def open_page(self):
        self.open(self.URL)
