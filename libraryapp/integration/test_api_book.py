from io import BytesIO

from libraryapp.models import Book


def _upload_file(filename="cover.png"):
    return BytesIO(b"fake image content"), filename


def test_book_detail_route_renders_book(test_client, sample_books, mocker):
    mock_render = mocker.patch("libraryapp.routes.book_detail.render_template", return_value="book detail")

    response = test_client.get(f"/book-detail/{sample_books[0].id}")

    assert response.status_code == 200
    args, kwargs = mock_render.call_args
    assert args == ("reader/book_detail.html",)
    assert kwargs["book"].id == sample_books[0].id


def test_book_management_route_for_admin(test_client, admin_user, sample_books, mocker):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, admin_user)
    mock_render = mocker.patch("libraryapp.routes.book_management.render_template", return_value="book admin")

    response = test_client.get("/book")

    assert response.status_code == 200
    args, kwargs = mock_render.call_args
    assert args == ("admin/book_management.html",)
    assert kwargs["total_books"] == len(sample_books)


def test_add_book_route_success(test_client, admin_user, mocker):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, admin_user)
    mock_upload = mocker.patch(
        "libraryapp.dao.books.cloudinary.uploader.upload",
        return_value={"secure_url": "https://fake-image.test/cover.png"},
    )

    response = test_client.post(
        "/book/add",
        data={
            "title": "Integration Book",
            "author": "Author",
            "type": "Novel",
            "publish_year": "2024",
            "quantity": "2",
            "avatar": _upload_file(),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/book")
    assert Book.query.filter_by(title="Integration Book").first() is not None
    mock_upload.assert_called_once()
