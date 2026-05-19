import time

from selenium.webdriver.common.by import By

from libraryapp import app, db
from libraryapp.models import User
from libraryapp.sel_tests.pages.ProfilePage import ProfilePage
from libraryapp.sel_tests.test_login import do_login
from libraryapp.utils import hash_password

def click_css(driver, selector):
    element = driver.find_element(By.CSS_SELECTOR, selector)
    element.click()
    time.sleep(0.5)
    return element

def reset_user_password(username="man", password="123"):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            user.password = hash_password(password)
            db.session.commit()


def open_profile_after_login(driver):
    reset_user_password()
    do_login(driver, "man", "123")

    profile_page = ProfilePage(driver)
    profile_page.open_page()

def open_change_password_after_login(driver):
    reset_user_password()
    do_login(driver, "man", "123")

    click_css(driver, "a.dropdown-toggle.rounded-pill")

    click_css(driver, "a[data-bs-target='#changePasswordModal']")



def test_update_profile_success(driver):
    open_profile_after_login(driver)

    click_css(driver, "button[data-bs-target='#updateProfileModal']")

    name_input = click_css(driver, "#updateName")
    name_input.clear()
    name_input.send_keys("Nguyễn Thanh Thuận New1")

    click_css(driver, "#updateProfileForm button[type='submit']")
    browser_alert = driver.switch_to.alert
    assert "Cập nhật thông tin thành công" in browser_alert.text
    browser_alert.accept()



def test_update_phone_invalid(driver):

    open_profile_after_login(driver)

    click_css(driver, "button[data-bs-target='#updateProfileModal']")

    phone_input = click_css(driver, "#updatePhone")
    phone_input.clear()
    phone_input.send_keys("123")

    click_css(driver, "#updateProfileForm button[type='submit']")
    browser_alert = driver.switch_to.alert
    assert "Số điện thoại không hợp lệ" in browser_alert.text
    browser_alert.accept()


def test_change_password_success(driver):
    open_change_password_after_login(driver)

    click_css(driver, "#oldPassword").send_keys("123")
    click_css(driver, "#newPassword").send_keys("NewPass123")
    click_css(driver, "#confirmPassword").send_keys("NewPass123")

    click_css(driver, "#changePasswordForm button[type='submit']")
    browser_alert = driver.switch_to.alert
    assert "Đổi mật khẩu thành công" in browser_alert.text
    browser_alert.accept()


def test_change_password_mismatch(driver):
    open_change_password_after_login(driver)

    click_css(driver, "#oldPassword").send_keys("123")
    click_css(driver, "#newPassword").send_keys("NewPass123")
    click_css(driver, "#confirmPassword").send_keys("DifferentPass456")

    click_css(driver, "#changePasswordForm button[type='submit']")
    confirm_error = click_css(driver, "#confirmPasswordError")
    assert "Mật khẩu xác nhận không khớp" in confirm_error.text


def test_change_password_wrong_old(driver):
    open_change_password_after_login(driver)

    click_css(driver, "#oldPassword").send_keys("WrongPassword")
    click_css(driver, "#newPassword").send_keys("NewPass123")
    click_css(driver, "#confirmPassword").send_keys("NewPass123")

    click_css(driver, "#changePasswordForm button[type='submit']")
    browser_alert = driver.switch_to.alert
    assert "Mật khẩu hiện tại không chính xác" in browser_alert.text
    browser_alert.accept()


def test_update_phone_success(driver):

    open_profile_after_login(driver)

    click_css(driver, "button[data-bs-target='#updateProfileModal']")

    phone_input = click_css(driver, "#updatePhone")
    phone_input.clear()
    phone_input.send_keys("0901234567")

    click_css(driver, "#updateProfileForm button[type='submit']")
    browser_alert = driver.switch_to.alert
    assert "Cập nhật thông tin thành công" in browser_alert.text
    browser_alert.accept()

    phone_text = click_css(driver, "#info-phone").text
    assert "0901234567" in phone_text


def test_change_password_too_short_realtime(driver):

    open_change_password_after_login(driver)

    click_css(driver, "#newPassword").send_keys("A1b")

    error = click_css(driver, "#newPasswordError")
    assert "6" in error.text


def test_change_password_missing_number_realtime(driver):

    open_change_password_after_login(driver)

    click_css(driver, "#newPassword").send_keys("NewPass")

    error = click_css(driver, "#newPasswordError")
    assert "chữ số" in error.text


def test_change_password_missing_lowercase_realtime(driver):

    open_change_password_after_login(driver)

    click_css(driver, "#newPassword").send_keys("NEWPASS123")

    error = click_css(driver, "#newPasswordError")
    assert "chữ thường" in error.text


def test_change_password_missing_uppercase_realtime(driver):

    open_change_password_after_login(driver)

    click_css(driver, "#newPassword").send_keys("newpass123")

    error = click_css(driver, "#newPasswordError")
    assert "chữ hoa" in error.text
