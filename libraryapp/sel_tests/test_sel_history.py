import time
from selenium.webdriver.common.by import By

#N5
def test_history_borrow(driver):

    driver.get("http://127.0.0.1:5000/login")
    driver.find_element(By.NAME, "username").send_keys("ndqbao")
    driver.find_element(By.NAME, "password").send_keys("Abc1234@")

    btn_login = driver.find_element(By.XPATH, "//button[contains(., 'ĐĂNG NHẬP')]")
    driver.execute_script("arguments[0].click();", btn_login)
    time.sleep(2)

    driver.get("http://127.0.0.1:5000/book-detail/6")
    time.sleep(1)
    btn_add = driver.find_element(By.XPATH, "//button[contains(., 'THÊM VÀO GIỎ MƯỢN')]")
    driver.execute_script("arguments[0].click();", btn_add)
    time.sleep(1)

    driver.get("http://127.0.0.1:5000/cart/view")
    time.sleep(1)
    btn_confirm = driver.find_element(By.XPATH, '//*[@id="mainContent"]/div/div/div[2]/div/div[2]/button')
    driver.execute_script("arguments[0].click();", btn_confirm)
    time.sleep(1)

    alert = driver.switch_to.alert
    alert.accept()
    time.sleep(2)

    driver.get("http://127.0.0.1:5000/history")
    time.sleep(2)

    assert "Đang mượn" in driver.page_source
    print(" Pass TC 23: Phiếu mới đã hiển thị trạng thái Đang mượn.")

    danh_sach_nut_truoc = driver.find_elements(By.XPATH, "//button[contains(., 'Yêu cầu trả')]")
    so_luong_truoc = len(danh_sach_nut_truoc)

    driver.execute_script("arguments[0].click();", danh_sach_nut_truoc[0])
    time.sleep(1)

    btn_gui_yeu_cau = driver.find_element(By.ID, "btnConfirmReturn")
    driver.execute_script("arguments[0].click();", btn_gui_yeu_cau)
    time.sleep(2)

    alert = driver.switch_to.alert
    alert.accept()
    time.sleep(2)

    assert "Chờ duyệt" in driver.page_source
    print(" Pass TC 24: Trạng thái đã chuyển sang Chờ duyệt màu vàng.")

    danh_sach_nut_sau = driver.find_elements(By.XPATH, "//button[contains(., 'Yêu cầu trả')]")
    so_luong_sau = len(danh_sach_nut_sau)

    assert so_luong_sau == so_luong_truoc - 1
    print("Pass TC 25: Nút Trả sách đã bị ẩn, chặn click 2 lần thành công.")