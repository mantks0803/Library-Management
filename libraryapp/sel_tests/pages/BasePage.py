from selenium.webdriver.support.select import Select


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def open(self, url):
        self.driver.get(url)

    def find(self,by, value):
        return self.driver.find_element(by, value)

    def finds(self, by, value):
        return self.driver.find_elements(by, value)

    def typing(self, by, value, text):
        e = self.find(by, value)
        e.send_keys(text)

    def click(self, by, value):
        e = self.find(by, value)
        e.click()

    def select(self, by, value, text):
        e = self.find(by, value)
        select = Select(e)
        select.select_by_visible_text(text)
