def test_load_user_delegates_to_get_current_user(mocker):
    import libraryapp.index as index

    mock_get_user = mocker.patch("libraryapp.index.get_current_user", return_value="user")

    assert index.load_user(1) == "user"
    mock_get_user.assert_called_once_with(1)


def test_register_routes_registers_all_route_blueprints(mocker):
    import libraryapp.index as index

    mock_register = mocker.patch.object(index.app, "register_blueprint")

    index.register_routes()

    assert mock_register.call_count == 9
    mock_register.assert_any_call(index.home.home_bp)
    mock_register.assert_any_call(index.login_logout.login_logout_bp)
    mock_register.assert_any_call(index.return_slips.return_slips_bp)
    mock_register.assert_any_call(index.slip_management.slip_management_bp)


def test_register_api_registers_all_api_blueprints(mocker):
    import libraryapp.index as index

    mock_register = mocker.patch.object(index.app, "register_blueprint")

    index.register_api()

    assert mock_register.call_count == 2
    mock_register.assert_any_call(index.api_users.api_users_bp)
    mock_register.assert_any_call(index.api_cart.api_cart_bp)


def test_index_main_registers_routes_and_runs_app(mocker):
    import runpy

    mock_register = mocker.patch("flask.app.Flask.register_blueprint")
    mock_run = mocker.patch("flask.app.Flask.run")

    runpy.run_module("libraryapp.index", run_name="__main__")

    assert mock_register.call_count == 11
    mock_run.assert_called_once_with(debug=True)
