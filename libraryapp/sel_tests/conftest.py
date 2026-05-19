from wsgiref.simple_server import server_version

import pytest
from selenium import webdriver
from selenium.webdriver.edge.service import Service

@pytest.fixture(scope="function")
def driver():
    print("\nStarting Selenium tests")

    options = webdriver.EdgeOptions()

    driver = webdriver.Edge(options=options)

    driver.maximize_window()

    driver.implicitly_wait(10)

    yield driver

    print("\nQuit")
    driver.quit()
