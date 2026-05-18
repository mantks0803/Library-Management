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
    assert "Mật khẩu không khớp, vui lòng nhập lại!" in alert.text

def test_register_false_username(driver):
    register = RegisterPage(driver=driver)
    register.open_page()
    register.register('Hien123','@Hie2010','test123','0944614575','2351010203@ou.edu.vn', '@Hie2010')

    time.sleep(1)

    assert driver.current_url == "http://127.0.0.1:5000/register"

    alert = driver.find_element(By.CSS_SELECTOR, 'div.alert')
    assert "Username đã tồn tại!" in alert.text