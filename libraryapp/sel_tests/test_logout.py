import time
from selenium.webdriver.common.by import By

from libraryapp.sel_tests.buttons.LogoutButton import find_logout_button
from libraryapp.sel_tests.pages.CartPage import CartPage
from libraryapp.sel_tests.pages.HomePage import HomePage
from libraryapp.sel_tests.pages.BookPage import BookPage1
from libraryapp.sel_tests.test_login import do_login


def test_logout_success(driver):
    do_login(driver, 'user2', '123')

    assert driver.current_url == "http://127.0.0.1:5000/"

    user_name = driver.find_element(By.CSS_SELECTOR, "a.dropdown-toggle.rounded-pill")
    assert "Nguyễn Thuận" in user_name.text

    # 2. Bấm nút Đăng xuất
    logout_btn = find_logout_button(driver)
    assert logout_btn is not None, "Không tìm thấy nút Đăng xuất"
    logout_btn.click()
    time.sleep(1)

    # 3. Assert: URL thay đổi thành /login
    assert driver.current_url == "http://127.0.0.1:5000/login"

def test_logout_cart_cleared(driver):
    """
    TC Extended: Kiểm tra giỏ hàng được xóa sau logout
    """

    # 1. Login reader
    do_login(driver, 'user2', '123')
    assert driver.current_url == "http://127.0.0.1:5000/"

    book_page = BookPage1(driver)
    book_page.open_page()
    time.sleep(1)
    book_page.add_book()

    # 2. Logout
    logout_btn = find_logout_button(driver)
    logout_btn.click()
    time.sleep(1)

    # 3. Login lại bằng tài khoản khác
    do_login(driver, 'user1', '123')
    time.sleep(0.5)

    # 4. Kiểm tra giỏ hàng trống
    cart_page = CartPage(driver)
    cart_page.open_page()
    time.sleep(1)

    c = driver.find_element(By.CSS_SELECTOR, "div > p")
    assert "Giỏ mượn trống. Hãy thêm sách để bắt đầu mượn!" in c.text


def test_logout_session_destroyed(driver):
    """
    TC-7 Extended: Kiểm tra session bị hủy sau logout
    - Đăng nhập
    - Đăng xuất
    - Cố gắng access trang /profile mà không có quyền
    - Assert: Bị redirect về /login
    """
    # 1. Login
    do_login(driver, 'man', '123')
    assert driver.current_url == "http://127.0.0.1:5000/"

    # 2. Logout
    logout_btn = find_logout_button(driver)
    logout_btn.click()
    time.sleep(1)

    # 3. Cố access /profile (trang chỉ reader mới vào được)
    driver.get("http://127.0.0.1:5000/profile")
    time.sleep(1)

    # 4. Assert: URL phải redirect về /login
    assert driver.current_url == "http://127.0.0.1:5000/login", \
        f"Session bị hủy, access /profile phải redirect về /login, nhưng URL={driver.current_url}"


def test_logout_header_shows_login_button(driver):
    """
    TC-7.1: Header chuyển về trạng thái chưa đăng nhập sau khi logout.
    - Đăng nhập reader.
    - Đăng xuất.
    - Assert: Header hiển thị lại nút Đăng nhập.
    """
    do_login(driver, 'user2', '123')
    assert driver.current_url == "http://127.0.0.1:5000/"

    logout_btn = find_logout_button(driver)
    logout_btn.click()
    time.sleep(1)

    login_btn = driver.find_element(By.CSS_SELECTOR, "a[href='/login']")
    assert "Đăng nhập" in login_btn.text

