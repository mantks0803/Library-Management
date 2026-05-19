import time
from selenium.webdriver.common.by import By

from libraryapp.sel_tests.pages.LoginPage import LoginPage


def do_login(driver, username, password):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login(username, password)
    time.sleep(1)

def test_login_success(driver):
    do_login(driver, 'admin', '123')

    assert driver.current_url == "http://127.0.0.1:5000/"

    c = driver.find_element(By.CSS_SELECTOR, "body > nav > div > div > div > a")
    assert "Nguyễn Thanh Thuận" in c.text

def test_login_false(driver):
    do_login(driver, 'admin', '1234')

    alert = driver.find_element(By.CSS_SELECTOR, 'div.alert')
    assert "Tên đăng nhập hoặc mật khẩu không chính xác!" in alert.text


def test_login_wrong_username(driver):

    do_login(driver, 'admin_not_exists', '123')

    alert = driver.find_element(By.CSS_SELECTOR, 'div.alert')
    assert "Tên đăng nhập hoặc mật khẩu không chính xác!" in alert.text


def test_login_required_fields(driver):

    login = LoginPage(driver=driver)
    login.open_page()

    login.click(*login.LOGIN_BUTTON)
    time.sleep(0.5)

    username_input = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
    assert driver.current_url == "http://127.0.0.1:5000/login"
    assert username_input.get_attribute("validationMessage") != ""
