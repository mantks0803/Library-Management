from libraryapp import Book
from libraryapp.dao.books import get_list_books, count_books, get_book, add_book
from libraryapp.test.test_base import test_session, test_app, sample_books, sample_user, mock_cloudinary, test_client


def test_get_all(sample_books):
    actual_books = get_list_books()
    assert len(actual_books) == len(sample_books)

def test_count_books(sample_books):
    assert count_books() == 5

def test_count_books_with_filters(sample_books):
    assert count_books(keyword="Clean") == 2
    assert count_books(author="Robert") == 2
    assert count_books(type="Programming") == 2

def test_get_books_by_id(sample_books):
    res = get_book(1)
    assert res is not None
    assert res.title == "Clean Code"

def test_get_by_keyword(sample_books):
    actual_books = get_list_books(keyword='Code')
    assert len(actual_books) == 2
    assert all("Code" in book.title for book in actual_books)

def test_get_by_keyword_less_than_2(sample_books):
    actual_books = get_list_books(keyword='C')
    assert len(actual_books) == 5

def test_get_kw_none(sample_books):
    actual_books = get_list_books(keyword="Fluent Python")
    assert len(actual_books) == 0

def test_get_by_author(sample_books):
    actual_books = get_list_books(author='James Clear')
    assert len(actual_books) == 1
    assert all("James Clear" in book.author for book in actual_books)

def test_get_by_author_less_than_2(sample_books):
    actual_books = get_list_books(author='J')
    assert len(actual_books) == 5

def test_get_by_author_none(sample_books):
    actual_books = get_list_books(author="Andrew")
    assert len(actual_books) == 0

# def test_page(sample_books):
#     actual_books = get_list_books(page=1)
#     assert len(actual_books) == 2
#     assert "Clean Code" in actual_books[0].title
#     assert "Introduction to Algorithms" in actual_books[1].title

def test_page_none(sample_books):
    actual_books = get_list_books(page=4)
    assert len(actual_books) == 0

def test_kw_author(sample_books):
    actual_books = get_list_books(keyword="Clean Code", author="Robert C. Martin")
    assert len(actual_books) == 2
    assert "Clean Code" in actual_books[0].title
    assert "Clean Code" in actual_books[1].title
    assert "Robert C. Martin" in actual_books[0].author
    assert "Robert C. Martin" in actual_books[1].author

def test_kw_author_none(sample_books):
    actual_books = get_list_books(keyword="Clean Code", author="J.K. Rowling")
    assert len(actual_books) == 0

def test_kw_page(sample_books):
    actual_books = get_list_books(keyword="Clean Code", page=1)
    assert len(actual_books) == 2
    assert all("Clean Code" in book.title for book in actual_books)

def test_kw_author_page(sample_books):
    actual_books = get_list_books(keyword="Clean Code", page=1, author="Robert C. Martin")
    assert len(actual_books) == 2
    assert all("Clean Code" in book.title for book in actual_books)
    assert all("Robert C. Martin" in book.author for book in actual_books)

def test_get_list_books_filter_type(test_session, sample_books):
    books = get_list_books(type="Programming")

    assert len(books) > 0
    assert all("Programming" in b.type for b in books)

def test_add_book_with_avatar(test_session, mock_cloudinary):
    success, book = add_book(title="Test", author="A", type="Test", avatar="fake",publish_year=2026, quantity=20)

    assert success is True
    assert book.avatar == "https://fake-image.png"

def test_add_book_failed(test_session, mocker):
    mocker.patch("libraryapp.dao.books.db.session.commit", side_effect=Exception("DB error"))

    success, error = add_book(title="Test book", author="author test", type="Test")

    assert success is False
    assert "DB error" in error


def test_home_default_no_params(test_client, mocker):

    mock_books = mocker.patch('libraryapp.routes.home.books')
    mock_render_template = mocker.patch('libraryapp.routes.home.render_template')

    mock_books.get_list_books.return_value = ['Book A', 'Book B']
    mock_books.count_books.return_value = 15
    mock_books.get_all_book_types.return_value = ['Type 1', 'Type 2']
    mock_render_template.return_value = "Mocked HTML"

    response = test_client.get('/')

    assert response.status_code == 200

    mock_books.get_list_books.assert_called_once_with(
        page=1, keyword=None, author=None, type=None
    )

    args, kwargs = mock_render_template.call_args
    assert args == ("index.html",)
    assert kwargs["books"] == ['Book A', 'Book B']
    assert kwargs["err_msg"] is None
    assert kwargs["pages"] == 1
    assert kwargs["types"] == ['Type 1', 'Type 2']
    assert kwargs["remaining_overdue"] == 0


def test_home_short_keyword_error(test_client, mocker):
    mock_books = mocker.patch('libraryapp.routes.home.books')
    mock_render_template = mocker.patch('libraryapp.routes.home.render_template')

    mock_books.count_books.return_value = 0
    mock_render_template.return_value = "Mocked HTML"

    response = test_client.get('/?keyword=a')

    assert response.status_code == 200


    args, kwargs = mock_render_template.call_args
    assert kwargs['err_msg'] == "Vui lòng nhập ít nhất 2 ký tự để tìm kiếm!"


def test_home_search_without_any_condition_sets_error(test_client, mocker):
    mock_books = mocker.patch('libraryapp.routes.home.books')
    mock_render_template = mocker.patch('libraryapp.routes.home.render_template')

    mock_books.get_list_books.return_value = []
    mock_books.count_books.return_value = 0
    mock_books.get_all_book_types.return_value = []
    mock_render_template.return_value = "Mocked HTML"

    response = test_client.get('/?keyword=')

    assert response.status_code == 200
    assert mock_render_template.call_args.kwargs["err_msg"] is not None
    assert "1" in mock_render_template.call_args.kwargs["err_msg"]


def test_home_short_author_error(test_client, mocker):
    mock_books = mocker.patch('libraryapp.routes.home.books')
    mock_render_template = mocker.patch('libraryapp.routes.home.render_template')

    mock_books.count_books.return_value = 0
    mock_render_template.return_value = "Mocked HTML"

    response = test_client.get('/?author=x')

    assert response.status_code == 200

    args, kwargs = mock_render_template.call_args
    assert kwargs['err_msg'] == "Vui lòng nhập ít nhất 2 ký tự để tìm kiếm!"


def test_home_valid_search_and_pagination(test_client, mocker):

    mock_books = mocker.patch('libraryapp.routes.home.books')
    mock_render_template = mocker.patch('libraryapp.routes.home.render_template')

    mock_books.count_books.return_value = 5
    mock_render_template.return_value = "Mocked HTML"

    response = test_client.get('/?keyword=python&author=guido&type=tech&page=2')

    assert response.status_code == 200

    mock_books.get_list_books.assert_called_once_with(
        page=2,
        keyword='python',
        author='guido',
        type='tech'
    )

    args, kwargs = mock_render_template.call_args
    assert kwargs['err_msg'] is None
    assert kwargs['pages'] == 1


def test_home_authenticated_user_sets_remaining_overdue(test_client, sample_user, mocker):
    mock_books = mocker.patch('libraryapp.routes.home.books')
    mock_render_template = mocker.patch('libraryapp.routes.home.render_template')
    mocker.patch(
        'libraryapp.routes.home.current_user',
        mocker.Mock(is_authenticated=True, id=sample_user.id),
    )
    mocker.patch('libraryapp.routes.home.get_current_user', return_value=sample_user)
    mocker.patch('libraryapp.routes.home.get_reader', return_value=mocker.Mock(id=sample_user.id))
    mocker.patch('libraryapp.routes.home.get_borrow_slip_status_overdue', return_value=[1, 2])

    mock_books.get_list_books.return_value = []
    mock_books.count_books.return_value = 0
    mock_books.get_all_book_types.return_value = []
    mock_render_template.return_value = "Mocked HTML"

    response = test_client.get('/')

    assert response.status_code == 200
    assert mock_render_template.call_args.kwargs["remaining_overdue"] == 2


def test_home_load_user_delegates_get_current_user(mocker):
    from libraryapp.routes.home import load_user

    mock_get_user = mocker.patch('libraryapp.routes.home.get_current_user', return_value="user")

    assert load_user(1) == "user"
    mock_get_user.assert_called_once_with(1)

