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


def test_login_required_password(driver):
    """
    TC-5: Đăng nhập thất bại khi bỏ trống password.
    - Nhập username nhưng không nhập password.
    - Assert: Browser giữ nguyên trang login và hiển thị validation required ở password.
    """
    login = LoginPage(driver=driver)
    login.open_page()

    login.typing(*login.USERNAME_INPUT, "admin")
    login.click(*login.LOGIN_BUTTON)
    time.sleep(0.5)

    password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    assert driver.current_url == "http://127.0.0.1:5000/login"
    assert password_input.get_attribute("validationMessage") != ""


def test_login_page_redirects_when_authenticated(driver):
    """
    TC-6: Người dùng đã đăng nhập không được ở lại trang login.
    - Đăng nhập thành công.
    - Mở lại /login.
    - Assert: Hệ thống redirect về trang chủ.
    """
    do_login(driver, 'admin', '123')

    driver.get("http://127.0.0.1:5000/login")
    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/"


def test_login_user1_updates_two_overdue_slips(driver):
    """
    TC-7: Đăng nhập user1 và kiểm tra cảnh báo phiếu quá hạn.
    - Dùng tài khoản user1/123.
    - Assert: Trang chủ hiển thị cảnh báo 2 phiếu mượn quá hạn của user này.
    """
    do_login(driver, 'user1', '123')

    assert driver.current_url == "http://127.0.0.1:5000/"

    alert = driver.find_element(By.CSS_SELECTOR, "div.alert-warning")
    assert "2" in alert.text
    assert "quá hạn" in alert.text
