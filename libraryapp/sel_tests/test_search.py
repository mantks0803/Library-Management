from selenium.webdriver.common.by import By

from libraryapp.sel_tests.pages.HomePage import HomePage
import time

def test_search_book_by_name(driver):
    kw = 'Clean Code'
    home = HomePage(driver=driver)
    home.open_page()
    home.search_book_name(kw)

    time.sleep(1)

    results = driver.find_elements(By.CSS_SELECTOR, '.container-fluid .card-title')
    assert all(kw in r.text for r in results)

def test_search_book_not_found(driver):
    kw = 'Truyện Kiều'
    home = HomePage(driver=driver)
    home.open_page()
    home.search_book_name(kw)

    time.sleep(1)

    results = driver.find_elements(By.CSS_SELECTOR, '.container-fluid .card-title')
    assert results == []


def test_search_book_by_author(driver):
    author = 'Robert C. Martin'
    home = HomePage(driver=driver)
    home.open_page()
    home.search_author(author)

    time.sleep(1)

    results = driver.find_elements(By.CSS_SELECTOR, '.author-name')
    assert all(author in r.text for r in results)

def test_search_kw_less(driver):
    home = HomePage(driver=driver)
    home.open_page()
    home.search_book_name('a')
    time.sleep(1)

    alert = driver.find_element(By.CSS_SELECTOR, '.alert')
    assert 'Vui lòng nhập ít nhất 2 ký tự để tìm kiếm!' in alert.text

def test_paging_book(driver):
    home = HomePage(driver=driver)
    home.open_page()

    books = driver.find_elements(By.CSS_SELECTOR, '.book-card')

    assert len(books) == 50


def test_search_type_book(driver):
    home = HomePage(driver=driver)
    home.open_page()

    home.search_type('Computer Science')
    time.sleep(1)
    results = driver.find_elements(By.CSS_SELECTOR, '.book-type')

    assert all('Computer Science' in r.text for r in results)

def test_search_all(driver):
    home = HomePage(driver=driver)
    home.open_page()

    book_name = "Clean Code"
    author = "Robert C. Martin"
    book_type = "Programming"

    home.search_all(book_name, author, book_type)
    time.sleep(1)

    res_name = driver.find_elements(By.CSS_SELECTOR, '.container-fluid .card-title')
    res_author = driver.find_elements(By.CSS_SELECTOR, '.author-name')
    res_type = driver.find_elements(By.CSS_SELECTOR, '.book-type')

    assert len(res_name) > 0
    assert all(book_name in r.text for r in res_name)
    assert all(author in r.text for r in res_author)
    assert all(book_type in r.text for r in res_type)

def test_search_not_found(driver):
    home = HomePage(driver=driver)
    home.open_page()

    book_name = "Clean Code"
    author = "Robert C. Martin"
    book_type = "Computer Science"

    home.search_all(book_name, author, book_type)

    time.sleep(1)

    res = driver.find_elements(By.CSS_SELECTOR, '.container-fluid .book-card')
    alert = driver.find_element(By.CSS_SELECTOR, '.container-fluid .alert')

    assert len(res) == 0
    assert "Không có sách nào phù hợp!" in alert.text


