from libraryapp.sel_tests.pages.BasePage import BasePage


class BookDetailPage(BasePage):
    URL = f"http://127.0.0.1:5000/book-detail"

    def open(self, id):
        self.open(f"{self.URL}/{id}")


