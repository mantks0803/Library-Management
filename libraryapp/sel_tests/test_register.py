import time
from selenium.webdriver.common.by import By

from libraryapp.sel_tests.pages.RegisterPage import RegisterPage


def test_register_success(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register('Hien123','@Hie2010','test123','0944614575','2351010203@ou.edu.vn', '@Hie2010')

    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/login"

    alert = driver.find_element(By.CSS_SELECTOR, 'div.alert')
    assert "Đăng ký thành công! Vui lòng đăng nhập." in alert.text

def test_register_false_password(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register('Hien123456','@Hie2010','test123','0944614575','2351010203@ou.edu.vn', '@Hie20111')

    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/register"

    alert = driver.find_element(By.CSS_SELECTOR, 'div.alert')
    assert "Mật khẩu xác nhận không khớp!" in alert.text

def test_register_false_username(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register('Hien123','@Hie2010','test123','0944614575','2351010203@ou.edu.vn', '@Hie2010')

    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/register"

    alert = driver.find_element(By.CSS_SELECTOR, 'div.alert')
    assert "Username đã tồn tại!" in alert.text

def test_register_false_phone(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register('HienPhone123','@Hie2010','test123','12345','2351010203@ou.edu.vn', '@Hie2010')

    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/register"

    alert = driver.find_element(By.CSS_SELECTOR, 'div.alert')
    assert "Số điện thoại không hợp lệ!" in alert.text

def test_register_password_too_short(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register('HienShort123','@H1a','test123','0944614575','2351010203@ou.edu.vn', '@H1a')

    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/register"

    alert = driver.find_element(By.CSS_SELECTOR, 'div.alert')
    assert "Mật khẩu phải có ít nhất 6 ký tự!" in alert.text

def test_register_password_missing_number(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register('HienNoNumber123','@Hieabc','test123','0944614575','2351010203@ou.edu.vn', '@Hieabc')

    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/register"

    alert = driver.find_element(By.CSS_SELECTOR, 'div.alert')
    assert "Mật khẩu phải chứa ít nhất một chữ số!" in alert.text

def test_register_password_missing_lowercase(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register('HienNoLower123','@HIE2010','test123','0944614575','2351010203@ou.edu.vn', '@HIE2010')

    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/register"

    alert = driver.find_element(By.CSS_SELECTOR, 'div.alert')
    assert "Mật khẩu phải chứa ít nhất một chữ thường!" in alert.text

def test_register_password_missing_uppercase(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register('HienNoUpper123','@hie2010','test123','0944614575','2351010203@ou.edu.vn', '@hie2010')

    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/register"

    alert = driver.find_element(By.CSS_SELECTOR, 'div.alert')
    assert "Mật khẩu phải chứa ít nhất một chữ hoa!" in alert.text
