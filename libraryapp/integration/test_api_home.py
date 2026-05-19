def test_home_route_renders_books(test_client, sample_books, mocker):
    mock_render = mocker.patch("libraryapp.routes.home.render_template", return_value="home html")

    response = test_client.get("/")

    assert response.status_code == 200
    args, kwargs = mock_render.call_args
    assert args == ("index.html",)
    assert len(kwargs["books"]) > 0
    assert kwargs["remaining_overdue"] == 0
