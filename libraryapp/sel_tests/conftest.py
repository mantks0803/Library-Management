import pytest
from selenium import webdriver

@pytest.fixture(scope="function")
def driver():
    print("\nStarting Selenium tests")

    options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(options=options)

    driver.maximize_window()

    driver.implicitly_wait(10)

    yield driver

    print("\nQuit")
    driver.quit()
