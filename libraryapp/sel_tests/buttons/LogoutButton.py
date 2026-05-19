from selenium.webdriver.common.by import By
import time

def find_logout_button(driver):

    try:
        user_dropdown = driver.find_element(By.CSS_SELECTOR,"a.dropdown-toggle.rounded-pill")
        user_dropdown.click()
        time.sleep(0.5)

        logout_btn = driver.find_element(By.CSS_SELECTOR,"a[href='/logout']")
        return logout_btn

    except Exception as e:
        print(f"Không tìm thấy nút đăng xuất: {e}")
        return None
